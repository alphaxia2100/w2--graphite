#!/usr/bin/env python3
"""Trackpad lock-in launcher: the draw editor + native absolute-trackpad input.

Click "Trackpad draw" to lock: the cursor freezes (decoupled, not hidden), a
trackpad-shaped outline appears, and a single finger draws into Excalidraw via
absolute mapping (NSTouch.normalizedPosition -> synthesized pointer events).
Press Esc to unlock. Public macOS APIs only (NSEvent touches + Core Graphics).

    out/pyenv/bin/python web/draw-editor/serve-trackpad.py
"""
import sys, os, threading, http.server, socketserver, functools
import objc
from AppKit import NSEvent
from Quartz import CGAssociateMouseAndMouseCursorPosition
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QTimer, Qt

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8139
NSTouchPhaseAny = 0xFFFFFFFFFFFFFFFF
NSEventMaskAny = 0xFFFFFFFFFFFFFFFF
NSEventTypeKeyDown = 10
ESC_KEYCODE = 53
PHASE = {1: "began", 2: "moved", 4: "moved", 8: "ended", 16: "cancelled"}

CTRL = None
_monitor = None


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), h) as s:
        s.serve_forever()


class Page(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        code = getattr(level, "value", level)
        lvl = {0: "LOG", 1: "WARN", 2: "ERR"}.get(code, str(level))
        print(f"[console:{lvl}] {message}", flush=True)


class Controller:
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
        try:
            CGAssociateMouseAndMouseCursorPosition(False)   # freeze cursor; touches still flow
        except Exception as e:
            print("decouple failed:", e, flush=True)
        print("NATIVE: LOCKED (cursor frozen; draw with one finger, Esc to stop)", flush=True)

    def unlock(self, reason=""):
        if not self.locked:
            return
        self.locked = False
        try:
            CGAssociateMouseAndMouseCursorPosition(True)
        except Exception:
            pass
        self.js("window.__trackpad&&window.__trackpad.unlock()")
        print(f"NATIVE: UNLOCKED {reason}".rstrip(), flush=True)


def on_title(t):
    if t == "TP:lock":
        CTRL.lock()
    elif t == "TP:unlock":
        CTRL.unlock("(js)")


def event_handler(event):
    try:
        if int(event.type()) == NSEventTypeKeyDown:
            if int(event.keyCode()) == ESC_KEYCODE and CTRL.locked:
                CTRL.unlock("(esc)")
            return event
        if CTRL.locked:
            ts = event.touchesMatchingPhase_inView_(NSTouchPhaseAny, None)
            # draw only with a SINGLE finger; 2+ fingers fall through to Excalidraw
            if ts is not None and ts.count() == 1:
                for t in ts:
                    np = t.normalizedPosition()
                    CTRL.forward(PHASE.get(int(t.phase()), "moved"), np.x, np.y)
    except Exception:
        pass
    return event


def install_monitor():
    global _monitor
    _monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(NSEventMaskAny, event_handler)
    print("NATIVE: NSEvent monitor installed (touches + Esc)", flush=True)


def main():
    global CTRL
    threading.Thread(target=serve, daemon=True).start()
    app = QApplication(sys.argv)
    CTRL = Controller()
    win = QMainWindow()
    win.setWindowTitle("Trackpad draw — water cycle")
    win.resize(1150, 780)
    view = QWebEngineView()
    view.setPage(Page(view))
    CTRL.view = view
    view.page().titleChanged.connect(on_title)
    win.setCentralWidget(view)
    win.show(); win.raise_(); win.activateWindow()
    view.load(QUrl(f"http://127.0.0.1:{PORT}/index.html?trackpad=1"))
    QTimer.singleShot(800, install_monitor)

    # ---- safety: never leave the cursor frozen ----
    app.aboutToQuit.connect(lambda: CTRL.unlock("(quit)"))
    app.applicationStateChanged.connect(
        lambda s: CTRL.unlock("(app inactive)") if s != Qt.ApplicationState.ApplicationActive else None)
    wd = {"ticks": 0}

    def watchdog():
        wd["ticks"] = wd["ticks"] + 1 if CTRL.locked else 0
        if wd["ticks"] >= 60:
            CTRL.unlock("(watchdog 60s)")
    t = QTimer(); t.timeout.connect(watchdog); t.start(1000)
    win._wd = t

    print(f"trackpad launcher: http://127.0.0.1:{PORT}/index.html?trackpad=1", flush=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
