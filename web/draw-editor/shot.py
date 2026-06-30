#!/usr/bin/env python3
"""Diagnostic: load the editor, grab a screenshot, and probe the DOM/CSS state.
    out/pyenv/bin/python web/draw-editor/shot.py <out.png> [query]
Quits itself after capturing.
"""
import sys, os, threading, http.server, socketserver, functools
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QTimer

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8138
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/editor-shot.png"
QUERY = sys.argv[2] if len(sys.argv) > 2 else ""


class Page(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        print(f"[console] {message}", flush=True)


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), h) as s:
        s.serve_forever()


PROBE = r"""(function(){
  var ex=document.querySelector('.excalidraw');
  var r=ex?ex.getBoundingClientRect():null;
  var sh=[];
  for(var i=0;i<document.styleSheets.length;i++){var s=document.styleSheets[i];var n;
    try{n=s.cssRules?s.cssRules.length:-1}catch(e){n='blocked'}
    sh.push((s.href?s.href.split('/').slice(-1)[0]:'inline')+':'+n)}
  var tb=document.querySelector('.App-toolbar')||document.querySelector('.Island');
  var tbr=tb?tb.getBoundingClientRect():null;
  return JSON.stringify({excalidraw:!!ex,size:r?Math.round(r.width)+'x'+Math.round(r.height):null,
    toolbar:!!tb, toolbarSize: tbr?Math.round(tbr.width)+'x'+Math.round(tbr.height):null, sheets:sh});
})()"""


def main():
    threading.Thread(target=serve, daemon=True).start()
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.resize(1200, 800)
    v = QWebEngineView()
    v.setPage(Page(v))
    win.setCentralWidget(v)
    win.show(); win.raise_(); win.activateWindow()
    v.load(QUrl(f"http://127.0.0.1:{PORT}/index.html{QUERY}"))

    def cap():
        v.page().runJavaScript(PROBE, lambda r: print("PROBE " + str(r), flush=True))
        pm = v.grab()
        ok = pm.save(OUT)
        print(f"SHOT saved={ok} -> {OUT} ({pm.width()}x{pm.height()})", flush=True)
        QTimer.singleShot(600, app.quit)
    QTimer.singleShot(6500, cap)
    app.exec()


if __name__ == "__main__":
    main()
