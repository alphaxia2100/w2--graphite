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
    color: var(--fg, #222);
    padding: 8px;
    overflow: auto;
}
.gc-ref svg { width: 100%; height: 100%; }
/* Keep reference labels readable in both light and dark mode. */
.gc-ref svg text { fill: var(--fg, #222); }
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


# Built-in samples so the feature can be end-to-end tested out of the box.
# Each reference is a small inline SVG; labels use the theme foreground (see
# `.gc-ref svg text` in the CSS) so they read in both light and dark mode.

_SVG_MULTI_AZ = """
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

_SVG_SERVERLESS = """
<svg viewBox="0 0 360 250" xmlns="http://www.w3.org/2000/svg" font-size="11" font-family="sans-serif">
  <rect x="140" y="8" width="80" height="24" rx="4" fill="#8882" stroke="#888"/>
  <text x="163" y="24">Client</text>
  <rect x="30" y="60" width="100" height="26" rx="4" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="48" y="77">CloudFront</text>
  <rect x="30" y="115" width="100" height="26" rx="4" fill="#ffab0033" stroke="#ffab00"/>
  <text x="42" y="132">S3 (static site)</text>
  <rect x="160" y="60" width="110" height="26" rx="4" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="176" y="77">API Gateway</text>
  <rect x="290" y="60" width="62" height="26" rx="4" fill="#33b3c433" stroke="#33b3c4"/>
  <text x="300" y="77">Cognito</text>
  <rect x="160" y="120" width="110" height="26" rx="4" fill="#57d06433" stroke="#57d064"/>
  <text x="188" y="137">Lambda</text>
  <rect x="160" y="180" width="110" height="26" rx="4" fill="#ffab0033" stroke="#ffab00"/>
  <text x="180" y="197">DynamoDB</text>
  <line x1="160" y1="32" x2="90" y2="60" stroke="#888"/>
  <line x1="80" y1="86" x2="80" y2="115" stroke="#888"/>
  <line x1="200" y1="32" x2="215" y2="60" stroke="#888"/>
  <line x1="270" y1="73" x2="290" y2="73" stroke="#888"/>
  <line x1="215" y1="86" x2="215" y2="120" stroke="#888"/>
  <line x1="215" y1="146" x2="215" y2="180" stroke="#888"/>
</svg>
"""

_SVG_SQS = """
<svg viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg" font-size="11" font-family="sans-serif">
  <rect x="15" y="60" width="100" height="30" rx="4" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="24" y="79">Upload (S3/API)</text>
  <rect x="145" y="60" width="80" height="30" rx="4" fill="#b18cff33" stroke="#b18cff"/>
  <text x="168" y="79">SQS</text>
  <rect x="255" y="52" width="95" height="46" rx="4" fill="#57d06433" stroke="#57d064"/>
  <text x="266" y="72">Workers</text>
  <text x="268" y="88">(Auto Scaling)</text>
  <rect x="145" y="130" width="80" height="28" rx="4" fill="#b18cff22" stroke="#b18cff" stroke-dasharray="3 3"/>
  <text x="168" y="148">DLQ</text>
  <rect x="255" y="140" width="95" height="28" rx="4" fill="#ffab0033" stroke="#ffab00"/>
  <text x="262" y="158">S3 / DynamoDB</text>
  <line x1="115" y1="75" x2="145" y2="75" stroke="#888"/>
  <line x1="225" y1="75" x2="255" y2="75" stroke="#888"/>
  <line x1="185" y1="90" x2="185" y2="130" stroke="#888" stroke-dasharray="3 3"/>
  <line x1="302" y1="98" x2="302" y2="140" stroke="#888"/>
</svg>
"""

_SVG_VPC = """
<svg viewBox="0 0 360 250" xmlns="http://www.w3.org/2000/svg" font-size="11" font-family="sans-serif">
  <rect x="10" y="10" width="340" height="230" rx="8" fill="none" stroke="#8888" stroke-dasharray="4 4"/>
  <text x="18" y="26" fill="#888">VPC</text>
  <rect x="150" y="16" width="60" height="22" rx="4" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="163" y="31">IGW</text>
  <rect x="25" y="55" width="150" height="150" rx="6" fill="none" stroke="#8886" stroke-dasharray="2 3"/>
  <text x="33" y="70" fill="#888">public subnet</text>
  <rect x="40" y="80" width="120" height="26" rx="4" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="86" y="97">ALB</text>
  <rect x="40" y="125" width="120" height="26" rx="4" fill="#33b3c433" stroke="#33b3c4"/>
  <text x="72" y="142">NAT Gateway</text>
  <rect x="195" y="55" width="140" height="150" rx="6" fill="none" stroke="#8886" stroke-dasharray="2 3"/>
  <text x="203" y="70" fill="#888">private subnet</text>
  <rect x="210" y="95" width="115" height="30" rx="4" fill="#57d06433" stroke="#57d064"/>
  <text x="228" y="114">App (EC2)</text>
  <line x1="180" y1="38" x2="100" y2="80" stroke="#888"/>
  <line x1="160" y1="93" x2="210" y2="108" stroke="#888"/>
  <line x1="240" y1="125" x2="150" y2="138" stroke="#888"/>
  <line x1="120" y1="125" x2="180" y2="38" stroke="#888" stroke-dasharray="3 3"/>
</svg>
"""

_SVG_WATER = """
<svg viewBox="0 0 340 240" xmlns="http://www.w3.org/2000/svg" font-size="11" font-family="sans-serif">
  <rect x="15" y="175" width="130" height="45" rx="6" fill="#4c9aff33" stroke="#4c9aff"/>
  <text x="55" y="202">Ocean</text>
  <rect x="105" y="15" width="140" height="40" rx="20" fill="#33b3c433" stroke="#33b3c4"/>
  <text x="120" y="39">Atmosphere (clouds)</text>
  <rect x="195" y="175" width="130" height="45" rx="6" fill="#57d06433" stroke="#57d064"/>
  <text x="225" y="202">Land / ground</text>
  <line x1="80" y1="175" x2="140" y2="55" stroke="#888"/>
  <text x="70" y="120" fill="#888">evaporation</text>
  <line x1="210" y1="55" x2="250" y2="175" stroke="#888"/>
  <text x="240" y="120" fill="#888">precipitation</text>
  <line x1="195" y1="205" x2="145" y2="205" stroke="#888"/>
  <text x="150" y="222" fill="#888">runoff</text>
  <text x="140" y="70" fill="#888">condensation</text>
</svg>
"""

_SVG_TRAFFIC = """
<svg viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg" font-size="11" font-family="sans-serif">
  <rect x="15" y="55" width="80" height="34" rx="6" fill="#57d06433" stroke="#57d064"/>
  <text x="42" y="76">Green</text>
  <rect x="120" y="55" width="80" height="34" rx="6" fill="#ffab0033" stroke="#ffab00"/>
  <text x="145" y="76">Yellow</text>
  <rect x="225" y="55" width="80" height="34" rx="6" fill="#ff563033" stroke="#ff5630"/>
  <text x="255" y="76">Red</text>
  <line x1="95" y1="72" x2="120" y2="72" stroke="#888"/>
  <line x1="200" y1="72" x2="225" y2="72" stroke="#888"/>
  <text x="100" y="48" fill="#888">timer</text>
  <text x="205" y="48" fill="#888">timer</text>
  <path d="M265 89 Q265 140 160 140 Q55 140 55 89" fill="none" stroke="#888"/>
  <text x="140" y="155" fill="#888">timer (red &#8594; green)</text>
</svg>
"""


def _rubric(items: list[str]) -> str:
    lis = "".join(f"  <li>{item}</li>\n" for item in items)
    return f"<ul>\n{lis}</ul>"


GRAPH_SAMPLES: list[dict[str, str]] = [
    {
        "prompt": (
            "Design a resilient, multi-AZ public web tier with a private "
            "database and S3 static assets for a small web app."
        ),
        "reference": _SVG_MULTI_AZ,
        "rubric": _rubric(
            [
                "Public entry (Route 53 / ALB) reaches the web tier?",
                "Web tier spread across <b>two Availability Zones</b>?",
                "Load balancer in front of both web instances?",
                "Database in a <b>private</b> subnet (no public route)?",
                "Database is Multi-AZ for failover?",
            ]
        ),
    },
    {
        "prompt": (
            "Design a serverless REST API for a to-do app: a static site, "
            "authenticated HTTP requests, business logic, and a managed NoSQL "
            "store \u2014 no servers to manage."
        ),
        "reference": _SVG_SERVERLESS,
        "rubric": _rubric(
            [
                "Static site served from S3 (via CloudFront)?",
                "API Gateway as the HTTPS entry to the API?",
                "Auth via Cognito (or a Lambda authorizer)?",
                "Business logic in <b>Lambda</b> (no EC2)?",
                "Data in DynamoDB (managed NoSQL)?",
            ]
        ),
    },
    {
        "prompt": (
            "Design a decoupled image-processing pipeline: users upload "
            "images; processing is asynchronous and must not drop work under "
            "load."
        ),
        "reference": _SVG_SQS,
        "rubric": _rubric(
            [
                "Upload path decoupled from processing?",
                "<b>SQS</b> queue buffers work between producer and consumers?",
                "Worker fleet scales with queue depth (Auto Scaling)?",
                "Dead-letter queue for poison messages?",
                "Results stored (S3 / DynamoDB)?",
            ]
        ),
    },
    {
        "prompt": (
            "Lay out a secure VPC: a public-facing load balancer, private app "
            "servers that need outbound internet for updates, and no inbound "
            "internet to the app tier."
        ),
        "reference": _SVG_VPC,
        "rubric": _rubric(
            [
                "Internet Gateway attached to the VPC?",
                "ALB in a <b>public</b> subnet?",
                "App servers in a <b>private</b> subnet (no public IP)?",
                "Outbound updates via a NAT Gateway in the public subnet?",
                "Security groups: ALB \u2192 app only, on the app port?",
            ]
        ),
    },
    {
        "prompt": (
            "Draw the water cycle as a closed loop: show the reservoirs and "
            "the processes that move water between them."
        ),
        "reference": _SVG_WATER,
        "rubric": _rubric(
            [
                "Evaporation from ocean/surface to the atmosphere?",
                "Condensation forming clouds?",
                "Precipitation (rain/snow) back to the surface?",
                "Runoff / infiltration returning water to the ocean?",
                "The loop <b>closes</b> (no dead ends)?",
            ]
        ),
    },
    {
        "prompt": (
            "Model a traffic light as a state machine: the states and the "
            "transitions (with triggers) between them."
        ),
        "reference": _SVG_TRAFFIC,
        "rubric": _rubric(
            [
                "Three states (Green / Yellow / Red)?",
                "Green \u2192 Yellow \u2192 Red order correct?",
                "Red \u2192 Green closes the cycle?",
                "Transitions labelled with their trigger (timer)?",
            ]
        ),
    },
]


# Plain recognition cards, so the colour-coded review buttons can be tested on
# ordinary cards alongside the graph-construction ones.
BASIC_SAMPLES: list[tuple[str, str]] = [
    (
        "Which AWS storage class fits data that is accessed unpredictably and "
        "should minimise cost automatically?",
        "S3 Intelligent-Tiering \u2014 it moves objects between access tiers "
        "based on usage, with no retrieval fees for tiering.",
    ),
    (
        "You need a managed relational database that fails over automatically "
        "to a standby. Which option?",
        "Amazon RDS with Multi-AZ (a synchronous standby in another AZ).",
    ),
    (
        "What decouples a producer from a consumer so work is not lost when "
        "the consumer is busy or down?",
        "Amazon SQS (a managed message queue).",
    ),
    (
        "How do you give an EC2 instance permission to read from S3 without "
        "storing access keys on it?",
        "Attach an IAM role (instance profile) granting the S3 permissions.",
    ),
    (
        "Which service caches content at edge locations to reduce latency for "
        "global users?",
        "Amazon CloudFront (CDN).",
    ),
    (
        "What is the SAA-C03 passing score, and on what scale?",
        "720 out of a scaled range of 100\u20131000.",
    ),
]


def _existing_first_fields(col: Collection, deck_name: str) -> set[str]:
    """First-field values already present in a deck, for de-duplication."""
    result: set[str] = set()
    for nid in col.find_notes(f'deck:"{deck_name}"'):
        note = col.get_note(nid)
        if note.fields:
            result.add(note.fields[0].strip())
    return result


def add_graph_samples(col: Collection, deck_name: str = "Graph Practice") -> int:
    nt = get_or_create_notetype(col)
    deck_id = col.decks.id(deck_name)
    existing = _existing_first_fields(col, deck_name)
    added = 0
    for sample in GRAPH_SAMPLES:
        if sample["prompt"].strip() in existing:
            continue
        note = col.new_note(nt)
        note["Prompt"] = sample["prompt"]
        note["Reference"] = sample["reference"]
        note["Rubric"] = sample["rubric"]
        col.add_note(note, deck_id)
        added += 1
    return added


def add_basic_samples(col: Collection, deck_name: str = "AWS SAA Basics") -> int:
    basic = col.models.by_name("Basic")
    if not basic:
        return 0
    deck_id = col.decks.id(deck_name)
    existing = _existing_first_fields(col, deck_name)
    added = 0
    for front, back in BASIC_SAMPLES:
        if front.strip() in existing:
            continue
        note = col.new_note(basic)
        note["Front"] = front
        note["Back"] = back
        col.add_note(note, deck_id)
        added += 1
    return added


# Backwards-compatible alias.
add_sample_notes = add_graph_samples


def install_and_add_sample(mw: aqt.main.AnkiQt) -> None:
    """Menu action: ensure the note type exists and add the sample decks."""
    graph = add_graph_samples(mw.col)
    basic = add_basic_samples(mw.col)
    mw.reset()
    tooltip(
        f"Added {graph} graph card(s) to 'Graph Practice' and "
        f"{basic} basic card(s) to 'AWS SAA Basics'."
    )


def setup_menu(mw: aqt.main.AnkiQt) -> None:
    """Add a discoverable Tools-menu entry for the feature."""
    action = QAction("Add SAA Sample Decks (Graph + Basics)", mw)
    qconnect(action.triggered, lambda: install_and_add_sample(mw))
    mw.form.menuTools.addAction(action)
