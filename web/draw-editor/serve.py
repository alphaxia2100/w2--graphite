#!/usr/bin/env python3
"""Dev launcher for the draw-editor: serve this dir over HTTP and open it in a
QWebEngineView, capturing the page's JS console to stdout so we can see whether
Excalidraw mounts (and any load errors) without needing eyes on the window.

    out/pyenv/bin/python web/draw-editor/serve.py
"""
import sys, os, threading, http.server, socketserver, functools
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QTimer

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8137


class Page(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        # In PyQt6 `level` is a JavaScriptConsoleMessageLevel enum (has .value).
        code = getattr(level, "value", level)
        lvl = {0: "LOG", 1: "WARN", 2: "ERR"}.get(code, str(level))
        src = (source or "").rsplit("/", 1)[-1]
        try:
            print(f"[console:{lvl}] {message}  ({src}:{line})", flush=True)
        except Exception:
            pass


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        httpd.serve_forever()


def main():
    threading.Thread(target=serve, daemon=True).start()
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("Draw editor v1 — water cycle")
    win.resize(1100, 760)
    view = QWebEngineView()
    view.setPage(Page(view))
    win.setCentralWidget(view)
    win.show(); win.raise_(); win.activateWindow()
    query = sys.argv[1] if len(sys.argv) > 1 else ""   # e.g. "?selftest=1"
    view.load(QUrl(f"http://127.0.0.1:{PORT}/index.html{query}"))

    def check(tag):
        view.page().runJavaScript(
            "!!window.EDITOR_MOUNTED",
            lambda r: print(f"MOUNT_CHECK[{tag}]: {'OK — Excalidraw mounted' if r else 'not mounted yet'}", flush=True),
        )
    QTimer.singleShot(4000, lambda: check("4s"))
    QTimer.singleShot(9000, lambda: check("9s"))
    print(f"serving {HERE} at http://127.0.0.1:{PORT}/index.html", flush=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
