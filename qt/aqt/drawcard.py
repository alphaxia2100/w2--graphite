# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Draw-it-from-blank diagram card editor (w2-graphite study feature).

Opens an Anki dialog with a native toolbar (prompt + Trackpad/Done buttons) above
an Excalidraw canvas, with a macOS trackpad lock-in: press the button or Space to
lock, then one finger draws in absolute position; two-finger drag/pinch move and
resize the region while unlocked; Esc unlocks. Native macOS APIs only (NSTouch +
Core Graphics), degrading to mouse/stylus if pyobjc is unavailable.
"""
from __future__ import annotations

import functools
import http.server
import os
import socketserver
import threading

from aqt.qt import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    Qt,
    QTimer,
    QUrl,
    QVBoxLayout,
    QWidget,
    qconnect,
)

try:
    from aqt.qt import QWebEngineView
except Exception:  # pragma: no cover
    from PyQt6.QtWebEngineWidgets import QWebEngineView

from PyQt6.QtWebEngineCore import QWebEnginePage


class _Page(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):  # noqa: N802
        if os.environ.get("ANKIDEV"):
            try:
                print("[drawcard] " + str(message), flush=True)
            except Exception:
                pass

# macOS absolute-trackpad capture via public AppKit/Quartz; optional.
try:
    import objc  # noqa: F401
    from AppKit import NSEvent
    from Quartz import CGAssociateMouseAndMouseCursorPosition

    HAVE_PYOBJC = True
except Exception:
    HAVE_PYOBJC = False

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drawcard_web")
PORT = 8142
_NS_TOUCH_ANY = 0xFFFFFFFFFFFFFFFF
_NS_EVENT_ANY = 0xFFFFFFFFFFFFFFFF
_NS_KEYDOWN = 10
_ESC = 53
_PHASE = {1: "began", 2: "moved", 4: "moved", 8: "ended", 16: "cancelled"}

_server_started = False


def _start_server() -> None:
    global _server_started
    if _server_started:
        return
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=WEB_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    _server_started = True


class _Controller:
    """Bridges native trackpad touches into the web canvas; freezes the cursor while locked."""

    def __init__(self) -> None:
        self.view = None
        self.locked = False

    def js(self, code: str) -> None:
        if self.view is not None:
            self.view.page().runJavaScript(code)

    def forward(self, phase: str, x: float, y: float) -> None:
        self.js(f"window.__trackpad&&window.__trackpad.onTouch('{phase}',{x:.4f},{y:.4f})")

    def lock(self) -> None:
        if self.locked:
            return
        self.locked = True
        if HAVE_PYOBJC:
            try:
                CGAssociateMouseAndMouseCursorPosition(False)
            except Exception:
                pass

    def unlock(self, *_: object) -> None:
        if not self.locked:
            return
        self.locked = False
        if HAVE_PYOBJC:
            try:
                CGAssociateMouseAndMouseCursorPosition(True)
            except Exception:
                pass
        self.js("window.__trackpad&&window.__trackpad.unlock()")


_CTL = _Controller()
_monitor = None


def _install_monitor() -> None:
    global _monitor
    if not HAVE_PYOBJC or _monitor is not None:
        return

    def handler(ev):
        try:
            if int(ev.type()) == _NS_KEYDOWN:
                if int(ev.keyCode()) == _ESC and _CTL.locked:
                    _CTL.unlock("esc")
                return ev
            if _CTL.locked:
                touches = ev.touchesMatchingPhase_inView_(_NS_TOUCH_ANY, None)
                if touches is not None and touches.count() == 1:  # single finger only
                    for t in touches:
                        np = t.normalizedPosition()
                        _CTL.forward(_PHASE.get(int(t.phase()), "moved"), np.x, np.y)
        except Exception:
            pass
        return ev

    _monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(_NS_EVENT_ANY, handler)


class DrawCardDialog(QDialog):
    def __init__(self, mw) -> None:
        super().__init__(mw)
        self.setWindowTitle("Draw-it-from-blank")
        self.resize(1080, 760)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        bar = QWidget()
        bar.setObjectName("drawcardBar")
        bar.setStyleSheet("#drawcardBar { border-bottom: 1px solid palette(mid); }")
        h = QHBoxLayout(bar)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(10)
        self.prompt = QLabel("Loading…")
        self.prompt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lock_btn = QPushButton("✋ Trackpad draw (Space)")
        self.done_btn = QPushButton("Done — reveal & self-judge")
        self.done_btn.setDefault(True)
        h.addWidget(self.prompt, 1)
        h.addWidget(self.lock_btn)
        h.addWidget(self.done_btn)
        root.addWidget(bar)

        self.web = QWebEngineView(self)
        self.web.setPage(_Page(self.web))
        root.addWidget(self.web, 1)
        _CTL.view = self.web
        self.web.page().titleChanged.connect(self._on_title)
        _start_server()
        self.web.setUrl(QUrl(f"http://127.0.0.1:{PORT}/index.html?trackpad=1&chrome=native"))

        qconnect(
            self.lock_btn.clicked,
            lambda: _CTL.js(
                "window.__trackpad && (window.__trackpad.isLocked()"
                "? window.__trackpad.unlock() : window.__trackpad.lock())"
            ),
        )
        qconnect(self.done_btn.clicked, lambda: _CTL.js("window.__done && window.__done()"))
        QTimer.singleShot(500, _install_monitor)
        QTimer.singleShot(900, self._load_prompt)

        app = QApplication.instance()
        if app is not None:
            app.applicationStateChanged.connect(self._on_app_state)

    def _load_prompt(self) -> None:
        self.web.page().runJavaScript("window.__prompt || ''", self._set_prompt)

    def _set_prompt(self, text) -> None:
        if text:
            self.prompt.setText(str(text))

    def _on_title(self, title: str) -> None:
        if title == "TP:lock":
            _CTL.lock()
        elif title == "TP:unlock":
            _CTL.unlock("js")

    def _on_app_state(self, state) -> None:
        if state != Qt.ApplicationState.ApplicationActive:
            _CTL.unlock("inactive")  # never leave the cursor frozen

    def closeEvent(self, e) -> None:
        _CTL.unlock("close")
        super().closeEvent(e)


_dialog = None


def open_draw_editor(mw) -> None:
    global _dialog
    _dialog = DrawCardDialog(mw)
    _dialog.show()
    _dialog.raise_()
    _dialog.activateWindow()
    if os.environ.get("ANKIDEV"):
        print("drawcard: opened (pyobjc=" + str(HAVE_PYOBJC) + ")", flush=True)
