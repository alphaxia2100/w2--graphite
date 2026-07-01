# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Graph-construction ("draw it from blank") flashcards.

A self-contained note type for topics that are really a graph (an AWS
architecture, a network topology, a state machine, the water cycle): the
learner constructs the diagram from memory in an in-card drawing pad, then
reveals a canonical reference and grades themselves. No AI is required — the
reference plus a rubric checklist is the standard the learner grades against
(see BrainLift SPOV 3). The AI judge is a later, opt-in assist.

This is the AI-off baseline described in PRD.md: capture in an in-app editor,
reveal the reference after the attempt, learner makes the final call.
"""

from __future__ import annotations

import aqt
from anki.collection import Collection
from aqt.qt import QAction, qconnect
from aqt.utils import tooltip

NOTETYPE_NAME = "Graph Construction (Draw from Blank)"
FIELDS = ["Prompt", "Reference", "Rubric"]

# The drawing pad is deliberately dependency-free (a small canvas freehand
# editor). Strokes are kept on a window-scoped global so they survive the
# question -> answer transition (the reviewer reuses one webview), letting the
# learner compare their own drawing to the reference side by side.
_EDITOR_SCRIPT = r"""
<script>
(function () {
    window.__gc = window.__gc || { strokes: [] };
    function padEl() { return document.getElementById("gc-pad"); }
    function fit(c) {
        var r = c.getBoundingClientRect();
        c.width = Math.max(1, r.width);
        c.height = Math.max(1, r.height);
    }
    function redraw() {
        var c = padEl();
        if (!c) return;
        var ctx = c.getContext("2d");
        ctx.clearRect(0, 0, c.width, c.height);
        ctx.lineWidth = 2.5;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.strokeStyle = getComputedStyle(document.body).color || "#333";
        window.__gc.strokes.forEach(function (s) {
            ctx.beginPath();
            s.forEach(function (p, i) { i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y); });
            ctx.stroke();
        });
    }
    window.gcClear = function () { window.__gc.strokes = []; redraw(); };
    window.gcInit = function (readonly) {
        var c = padEl();
        if (!c) return;
        fit(c);
        redraw();
        if (readonly) return;
        var drawing = false, cur = null;
        function pos(e) {
            var r = c.getBoundingClientRect();
            var t = e.touches ? e.touches[0] : e;
            return { x: t.clientX - r.left, y: t.clientY - r.top };
        }
        function start(e) { drawing = true; cur = [pos(e)]; window.__gc.strokes.push(cur); e.preventDefault(); }
        function move(e) { if (!drawing) return; cur.push(pos(e)); redraw(); e.preventDefault(); }
        function end() { drawing = false; }
        c.addEventListener("mousedown", start);
        c.addEventListener("mousemove", move);
        window.addEventListener("mouseup", end);
        c.addEventListener("touchstart", start, { passive: false });
        c.addEventListener("touchmove", move, { passive: false });
        c.addEventListener("touchend", end);
        window.addEventListener("resize", function () { fit(c); redraw(); });
    };
})();
</script>
"""

_FRONT_TEMPLATE = (
    """
<div class="gc-card">
  <div class="gc-prompt">{{Prompt}}</div>
  <div class="gc-padwrap"><canvas id="gc-pad" class="gc-pad"></canvas></div>
  <div class="gc-toolbar">
    <button type="button" class="gc-btn" onclick="gcClear()">Clear</button>
    <span class="gc-hint">Draw the architecture from a blank page, then reveal the reference.</span>
  </div>
</div>
"""
    + _EDITOR_SCRIPT
    + "<script>if (window.gcInit) window.gcInit(false);</script>"
)

_BACK_TEMPLATE = (
    """
<div class="gc-card">
  <div class="gc-prompt">{{Prompt}}</div>
  <div class="gc-cols">
    <div class="gc-col">
      <div class="gc-label">Your drawing</div>
      <div class="gc-padwrap gc-readonly"><canvas id="gc-pad" class="gc-pad"></canvas></div>
    </div>
    <div class="gc-col">
      <div class="gc-label">Reference</div>
      <div class="gc-ref">{{Reference}}</div>
    </div>
  </div>
  <div class="gc-rubric">
    <div class="gc-label">Check yourself against the reference, then grade honestly</div>
    {{Rubric}}
  </div>
</div>
"""
    + _EDITOR_SCRIPT
    + "<script>if (window.gcInit) window.gcInit(true);</script>"
)

_CSS = """
.card { font-family: -apple-system, Segoe UI, Roboto, sans-serif; }
.gc-card { max-width: 900px; margin: 0 auto; text-align: left; }
.gc-prompt {
    font-size: 1.15em;
    font-weight: 600;
    line-height: 1.4;
    margin: 0.2em 0 0.7em;
}
.gc-padwrap {
    position: relative;
    height: 320px;
    border: 1px solid var(--border, #d0d0d0);
    border-radius: var(--border-radius-medium, 10px);
    background:
        var(--canvas-inset, #fafafa)
        repeating-linear-gradient(0deg, transparent 0 23px, rgba(128,128,128,0.08) 23px 24px)
        repeating-linear-gradient(90deg, transparent 0 23px, rgba(128,128,128,0.08) 23px 24px);
}
.gc-pad { position: absolute; inset: 0; width: 100%; height: 100%; touch-action: none; cursor: crosshair; }
.gc-readonly .gc-pad { cursor: default; }
.gc-toolbar { display: flex; align-items: center; gap: 0.8em; margin-top: 0.6em; }
.gc-hint { color: var(--fg-subtle, #777); font-size: 0.85em; }
.gc-btn {
    padding: 5px 14px;
    border-radius: var(--border-radius, 6px);
    border: 1px solid var(--border, #ccc);
    background: var(--canvas-elevated, #fff);
    color: var(--fg, #222);
    cursor: pointer;
}
.gc-btn:hover { border-color: var(--border-strong, #999); }
.gc-cols { display: flex; gap: 1em; flex-wrap: wrap; margin-top: 0.4em; }
.gc-col { flex: 1 1 320px; min-width: 300px; }
.gc-col .gc-padwrap { height: 260px; }
.gc-label { font-size: 0.8em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--fg-subtle, #888); margin-bottom: 0.35em; }
.gc-ref {
    height: 260px;
    border: 1px solid var(--border, #d0d0d0);
    border-radius: var(--border-radius-medium, 10px);
    background: var(--canvas-inset, #fafafa);
    padding: 8px;
    overflow: auto;
}
.gc-ref svg { width: 100%; height: 100%; }
.gc-rubric { margin-top: 1em; }
.gc-rubric ul { margin: 0.2em 0; padding-left: 1.1em; }
.gc-rubric li { margin: 0.25em 0; line-height: 1.4; }
"""


def get_or_create_notetype(col: Collection) -> dict:
    """Return the graph-construction note type, creating it if absent."""
    existing = col.models.by_name(NOTETYPE_NAME)
    if existing:
        return existing

    nt = col.models.new(NOTETYPE_NAME)
    for field_name in FIELDS:
        col.models.add_field(nt, col.models.new_field(field_name))
    nt["css"] = _CSS
    template = col.models.new_template("Draw from Blank")
    template["qfmt"] = _FRONT_TEMPLATE
    template["afmt"] = _BACK_TEMPLATE
    col.models.add_template(nt, template)
    col.models.add(nt)
    # add() may assign a fresh copy; re-fetch to be safe.
    return col.models.by_name(NOTETYPE_NAME) or nt


# A tiny built-in sample so the feature is demonstrable out of the box.
_SAMPLE_REFERENCE = """
<svg viewBox="0 0 320 240" xmlns="http://www.w3.org/2000/svg" font-size="11" font-family="sans-serif">
  <rect x="8" y="8" width="304" height="224" rx="8" fill="none" stroke="#8888" stroke-dasharray="4 4"/>
  <text x="16" y="24" fill="#888">VPC</text>
  <rect x="120" y="20" width="80" height="26" rx="4" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="132" y="37">Route 53</text>
  <rect x="120" y="60" width="80" height="26" rx="4" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="140" y="77">ALB</text>
  <rect x="30" y="110" width="110" height="30" rx="4" fill="#57d06433" stroke="#57d064"/>
  <text x="44" y="129">Web (AZ-a)</text>
  <rect x="180" y="110" width="110" height="30" rx="4" fill="#57d06433" stroke="#57d064"/>
  <text x="194" y="129">Web (AZ-b)</text>
  <rect x="95" y="175" width="130" height="30" rx="4" fill="#ffab0033" stroke="#ffab00"/>
  <text x="108" y="194">RDS (private, Multi-AZ)</text>
  <line x1="160" y1="46" x2="160" y2="60" stroke="#888"/>
  <line x1="150" y1="86" x2="85" y2="110" stroke="#888"/>
  <line x1="170" y1="86" x2="235" y2="110" stroke="#888"/>
  <line x1="85" y1="140" x2="150" y2="175" stroke="#888"/>
  <line x1="235" y1="140" x2="170" y2="175" stroke="#888"/>
</svg>
"""

_SAMPLE_RUBRIC = """
<ul>
  <li>Public entry (Route 53 / ALB) reaches the web tier?</li>
  <li>Web tier spread across <b>two Availability Zones</b>?</li>
  <li>Load balancer in front of both web instances?</li>
  <li>Database in a <b>private</b> subnet (no public route)?</li>
  <li>Database is Multi-AZ for failover?</li>
</ul>
"""


def add_sample_notes(col: Collection, deck_name: str = "Graph Practice") -> int:
    nt = get_or_create_notetype(col)
    deck_id = col.decks.id(deck_name)
    samples = [
        (
            "Design a resilient, multi-AZ public web tier with a private "
            "database and S3 static assets for a small web app.",
            _SAMPLE_REFERENCE,
            _SAMPLE_RUBRIC,
        ),
    ]
    added = 0
    for prompt, reference, rubric in samples:
        note = col.new_note(nt)
        note["Prompt"] = prompt
        note["Reference"] = reference
        note["Rubric"] = rubric
        col.add_note(note, deck_id)
        added += 1
    return added


def install_and_add_sample(mw: aqt.main.AnkiQt) -> None:
    """Menu action: ensure the note type exists and add a sample card."""
    added = add_sample_notes(mw.col)
    mw.reset()
    tooltip(f"Added {added} graph-construction card(s) to 'Graph Practice'.")


def setup_menu(mw: aqt.main.AnkiQt) -> None:
    """Add a discoverable Tools-menu entry for the feature."""
    action = QAction("Add Graph-Construction Sample Deck", mw)
    qconnect(action.triggered, lambda: install_and_add_sample(mw))
    mw.form.menuTools.addAction(action)
