#!/usr/bin/env python3
"""
Trackpad lock-in de-risk spike (macOS).

Question this answers: can we read ABSOLUTE trackpad finger position
(NSTouch.normalizedPosition, 0..1, origin lower-left) and get it into a
QWebEngineView canvas — i.e. does an NSView over Chromium actually receive
indirect (trackpad) touches?

It tries TWO capture mechanisms at once and logs which one fires:
  A) TouchCaptureView  — a transparent NSView added over the webview, made
     first responder, implementing touchesBegan/Moved/Ended.
  B) Local NSEvent monitor — app-level interception of any event carrying
     touches, independent of the responder chain.

Run (from repo root, with pyobjc installed in the env):
    out/pyenv/bin/python experiments/trackpad-spike/spike.py
Then: focus the window, put ONE finger on the trackpad and move it. Coloured
dots should trail your finger (blue = mechanism A, orange = mechanism B), and
events are printed to stdout. Ctrl-C or close the window to quit.
"""
import sys
import objc
from AppKit import NSView, NSEvent, NSApplication
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer, Qt

# --- AppKit constants (pyobjc doesn't always expose these) ---
NSTouchPhaseAny = 0xFFFFFFFFFFFFFFFF
NSTouchTypeMaskIndirect = 1 << 1          # NSTouchTypeIndirect = 1
NSViewWidthSizable, NSViewHeightSizable = 2, 16
NSEventMaskAny = 0xFFFFFFFFFFFFFFFF

HTML = """
<!doctype html><meta charset=utf-8>
<style>
 html,body{margin:0;height:100%;background:#0f172a;color:#e2e8f0;font:14px -apple-system,sans-serif;overflow:hidden}
 #hud{position:fixed;top:10px;left:12px;z-index:2;line-height:1.5}
 #hud b{color:#7dd3fc} .a{color:#60a5fa} .b{color:#fb923c}
 canvas{position:fixed;inset:0}
</style>
<div id=hud>
  <b>Trackpad capture spike</b><br>
  Focus this window, then drag ONE finger on the trackpad.<br>
  <span class=a>● blue = NSView (mechanism A)</span> &nbsp; <span class=b>● orange = monitor (mechanism B)</span><br>
  A events: <b id=ca>0</b> &nbsp; B events: <b id=cb>0</b> &nbsp; last: <span id=last>—</span>
</div>
<canvas id=c></canvas>
<script>
 const cv=document.getElementById('c'),x=cv.getContext('2d');
 let ca=0,cb=0;
 function fit(){cv.width=innerWidth;cv.height=innerHeight;}
 addEventListener('resize',fit);fit();
 // nx,ny in 0..1 with origin lower-left (as NSTouch gives); invert y for canvas
 window.drawDot=function(nx,ny,mech){
   const px=nx*cv.width, py=(1-ny)*cv.height;
   x.beginPath();x.arc(px,py,mech==='A'?5:8,0,7);
   x.fillStyle = mech==='A' ? 'rgba(96,165,250,.9)' : 'rgba(251,146,60,.55)';
   x.fill();
   if(mech==='A')document.getElementById('ca').textContent=++ca;
   else document.getElementById('cb').textContent=++cb;
   document.getElementById('last').textContent=mech+' '+nx.toFixed(3)+', '+ny.toFixed(3);
 };
</script>
"""

_webview = None
_counts = {"A": 0, "B": 0}


@objc.python_method
def emit(mech, phase, x, y):
    _counts[mech] += 1
    n = _counts[mech]
    # print all begins/ends; sample moves to keep the log readable
    if phase in ("began", "ended", "cancelled") or n % 12 == 0:
        print(f"[{mech}] {phase:9s} x={x:.4f} y={y:.4f}  (mech {mech} total={n})", flush=True)
    if _webview is not None:
        try:
            _webview.page().runJavaScript(f"window.drawDot({x:.4f},{y:.4f},'{mech}')")
        except Exception as e:
            print("  runJavaScript failed:", e, flush=True)


class TouchCaptureView(NSView):
    def initWithFrame_(self, frame):
        self = objc.super(TouchCaptureView, self).initWithFrame_(frame)
        if self is None:
            return None
        try:
            self.setAllowedTouchTypes_(NSTouchTypeMaskIndirect)
        except Exception as e:
            print("setAllowedTouchTypes_ failed:", e, flush=True)
        try:
            self.setAcceptsTouchEvents_(True)   # legacy path, still honored
            self.setWantsRestingTouches_(False)
        except Exception:
            pass
        return self

    def acceptsFirstResponder(self):
        return True

    def becomeFirstResponder(self):
        print(">> TouchCaptureView BECAME first responder", flush=True)
        return True

    def resignFirstResponder(self):
        print("<< TouchCaptureView resigned first responder", flush=True)
        return True

    @objc.python_method
    def _handle(self, phase, event):
        try:
            touches = event.touchesMatchingPhase_inView_(NSTouchPhaseAny, self)
        except Exception as e:
            print("touchesMatchingPhase failed (A):", e, flush=True)
            return
        for t in touches:
            np = t.normalizedPosition()
            emit("A", phase, np.x, np.y)

    def touchesBeganWithEvent_(self, e):
        self._handle("began", e)

    def touchesMovedWithEvent_(self, e):
        self._handle("moved", e)

    def touchesEndedWithEvent_(self, e):
        self._handle("ended", e)

    def touchesCancelledWithEvent_(self, e):
        self._handle("cancelled", e)


_monitor = None


def install_monitor():
    """Mechanism B: app-level event monitor, independent of responder chain."""
    def handler(event):
        try:
            touches = event.touchesMatchingPhase_inView_(NSTouchPhaseAny, None)
            if touches is not None and touches.count() > 0:
                for t in touches:
                    np = t.normalizedPosition()
                    emit("B", "touch", np.x, np.y)
        except Exception:
            pass
        return event
    global _monitor
    _monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(NSEventMaskAny, handler)
    print("mechanism B: local NSEvent monitor installed", flush=True)


def attach(webview, window):
    """Attach the NSView over the webview and make it first responder."""
    try:
        nsview = objc.objc_object(c_void_p=int(webview.winId()))
    except Exception as e:
        print("FATAL: could not get NSView from winId():", e, flush=True)
        return
    print("webview NSView:", nsview, flush=True)
    frame = nsview.bounds()
    tv = TouchCaptureView.alloc().initWithFrame_(frame)
    tv.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
    nsview.addSubview_(tv)
    nswin = nsview.window()
    if nswin is not None:
        ok = nswin.makeFirstResponder_(tv)
        print(f"mechanism A: TouchCaptureView attached; makeFirstResponder -> {ok}", flush=True)
    else:
        print("WARNING: nsview.window() is None; cannot set first responder yet", flush=True)
    install_monitor()

    # Re-assert first responder periodically in case the webview steals it,
    # and print a heartbeat so silence is distinguishable from 'no events'.
    state = {"ticks": 0}

    def reassert():
        state["ticks"] += 1
        nswin2 = nsview.window()
        if nswin2 is not None and nswin2.firstResponder() is not tv:
            nswin2.makeFirstResponder_(tv)
        if state["ticks"] % 5 == 0:
            print(f"[heartbeat] alive; A={_counts['A']} B={_counts['B']} "
                  f"firstResponder_is_ours={nswin2.firstResponder() is tv if nswin2 else '?'}",
                  flush=True)
    t = QTimer(window)
    t.timeout.connect(reassert)
    t.start(1500)
    window._timer = t  # keep ref
    window._touchview = tv


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("Trackpad capture spike — drag one finger on the trackpad")
    win.resize(900, 600)
    global _webview
    _webview = QWebEngineView()
    _webview.setHtml(HTML)
    win.setCentralWidget(_webview)
    win.show()
    win.raise_()
    win.activateWindow()
    # Attach after the native window/view exists.
    QTimer.singleShot(500, lambda: attach(_webview, win))
    print("spike started; window shown. Drag one finger on the trackpad.", flush=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
