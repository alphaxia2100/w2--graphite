"""w2_drawcard — draw-it-from-blank diagram card, inside Anki.

Adds Tools → "Draw-it-from-blank (diagram card)", which opens the Excalidraw
draw editor with the macOS trackpad lock-in (Space to lock, one finger draws,
2-finger move / pinch resize the region, Esc to unlock). Reuses the same web
assets as the standalone editor; the native trackpad capture runs inside Anki's
own Qt event loop (no separate process).
"""
import os
import threading
import http.server
import socketserver
import functools

from aqt import mw, gui_hooks
from aqt.qt import (
    QAction, QDialog, QVBoxLayout, QUrl, QTimer, Qt, QApplication, qconnect,
)

try:
    from aqt.qt import QWebEngineView
except Exception:  # pragma: no cover
    from PyQt6.QtWebEngineWidgets import QWebEngineView

# macOS absolute-trackpad capture (public AppKit/Quartz). Degrade gracefully.
try:
    import objc  # noqa: F401
    from AppKit import NSEvent
    from Quartz import CGAssociateMouseAndMouseCursorPosition
    HAVE_PYOBJC = True
except Exception:
    HAVE_PYOBJC = False

ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ADDON_DIR, "web")
PORT = 8142
NSTouchPhaseAny = 0xFFFFFFFFFFFFFFFF
NSEventMaskAny = 0xFFFFFFFFFFFFFFFF
NSEventTypeKeyDown = 10
ESC_KEYCODE = 53
PHASE = {1: "began", 2: "moved", 4: "moved", 8: "ended", 16: "cancelled"}

_server_started = False


def _start_server():
    global _server_started
    if _server_started:
        return
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=WEB_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    _server_started = True


class _Controller:
    """Bridges native trackpad touches -> the web canvas; freezes the cursor while locked."""

    def __init__(self):
        self.view = None
        self.locked = False

    def js(self, code):
        if self.view is not None:
            self.view.page().runJavaScript(code)

    def forward(self, phase, x, y):
        self.js(f"window.__trackpad&&window.__trackpad.onTouch('{phase}',{x:.4f},{y:.4f})")

    def lock(self):
        if self.locked:
            return
        self.locked = True
        if HAVE_PYOBJC:
            try:
                CGAssociateMouseAndMouseCursorPosition(False)
            except Exception:
                pass

    def unlock(self, *_):
        if not self.locked:
            return
        self.locked = False
        if HAVE_PYOBJC:
            try:
                CGAssociateMouseAndMouseCursorPosition(True)
            except Exception:
                pass
        self.js("window.__trackpad&&window.__trackpad.unlock()")


CTL = _Controller()
_monitor = None


def _install_monitor():
    global _monitor
    if not HAVE_PYOBJC or _monitor is not None:
        return

    def handler(ev):
        try:
            if int(ev.type()) == NSEventTypeKeyDown:
                if int(ev.keyCode()) == ESC_KEYCODE and CTL.locked:
                    CTL.unlock("esc")
                return ev
            if CTL.locked:
                ts = ev.touchesMatchingPhase_inView_(NSTouchPhaseAny, None)
                if ts is not None and ts.count() == 1:   # single finger only
                    for t in ts:
                        np = t.normalizedPosition()
                        CTL.forward(PHASE.get(int(t.phase()), "moved"), np.x, np.y)
        except Exception:
            pass
        return ev

    _monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(NSEventMaskAny, handler)


class DrawDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Draw-it-from-blank")
        self.resize(1100, 780)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.view = QWebEngineView(self)
        lay.addWidget(self.view)
        CTL.view = self.view
        self.view.page().titleChanged.connect(self._on_title)
        _start_server()
        self.view.load(QUrl(f"http://127.0.0.1:{PORT}/index.html?trackpad=1"))
        QTimer.singleShot(500, _install_monitor)

    def _on_title(self, t):
        if t == "TP:lock":
            CTL.lock()
        elif t == "TP:unlock":
            CTL.unlock("js")

    def closeEvent(self, e):
        CTL.unlock("close")   # never leave the cursor frozen
        super().closeEvent(e)


_dialog = None


def open_draw_editor():
    global _dialog
    _dialog = DrawDialog(mw)
    _dialog.show()
    _dialog.raise_()
    _dialog.activateWindow()


def _add_menu():
    act = QAction("Draw-it-from-blank (diagram card)", mw)
    qconnect(act.triggered, open_draw_editor)
    mw.form.menuTools.addAction(act)
    print("w2_drawcard: menu item added (Tools menu); pyobjc=" + str(HAVE_PYOBJC), flush=True)
    # safety: restore the cursor if Anki loses focus or quits while locked
    app = QApplication.instance()
    if app is not None:
        app.applicationStateChanged.connect(
            lambda s: CTL.unlock("inactive") if s != Qt.ApplicationState.ApplicationActive else None)
        app.aboutToQuit.connect(lambda: CTL.unlock("quit"))


gui_hooks.main_window_did_init.append(_add_menu)
