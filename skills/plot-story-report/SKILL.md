---
name: "plot-story-report"
description: "Write plot-oriented reports like Chris Deotte's Kaggle writeups: a story told by 6-10 headline figures plus short plain text. Use for writeups, readouts, post-mortems or Chris-style reports."
---

# Plot-Story Report

The model is Chris Deotte's "Two Farmers and a Cow" Kaggriculture writeup. Three things make it work:

1. **Read only the figure titles and you get the whole story.** Each title is a claim ("When everyone plays the same tape, nobody wins"), never a topic ("Win rate vs tapes").
2. **One claim per section.** Each section is one figure plus 1-3 short paragraphs. The text and the figure say the same thing on purpose, so skimmers and readers both get it.
3. **Plain words and honest numbers.** Every term is defined the first time it appears, every number has its denominator, the ending names what still beats you, and the methods go at the end for the curious.

Only about a third of the figures are data charts. The rest are simple diagrams (box-and-arrow flows, layered stacks, layout maps), which explain *how* something works.

## Step 0: Collect the material (before any plotting)

- **The result line:** final score, rank, number of teams or users, and the date.
- **The arc:** what was tried, what stalled and why, what worked, and what you would do differently.
- **The numbers behind each claim, with their denominators.** Look in the person's files, logs, memory and past chats first.
- **Audience:**
  - `peers` (technical or Kaggle; the default)
  - `stakeholders` (business; add a "Decision" section and drop the jargon)
  - `public`
- **Language:** the language of the request, unless the destination needs another (a Kaggle post means English).

**Never invent a number.** If a claim has no real data behind it, there are three options:
- draw it as a diagram instead of a chart;
- leave an HTML comment `<!-- TODO: need X -->` and list the missing numbers in the reply;
- ask for them.

A placeholder chart filled with made-up values is never acceptable.

## Step 1: Write the story spine

Write 6-10 headline sentences, one per figure, each 70 characters or less. Then read them alone, in order. If they don't tell the story, fix the story before drawing anything.

A typical arc (adapt it; skip what doesn't apply):

| # | Beat | Usual figure |
|---|------|--------------|
| 1 | The setup: what the problem or game is | `flow`, `grid` or `chips` |
| 2 | The starting point or baseline | `flow` or `layers` |
| 3 | What we added to it | `layers` |
| 4 | Why it stalled (the surprise, with its number) | `tokens`, `bars` or `hist` |
| 5 | The pivot or key idea | `chips`, `grid` or `flow` |
| 6 | How it was built: one measured change at a time | `progress` |
| 7 | The cleverest detail ("the trick") | 3-step `flow` |
| 8 | Results | `bars` |
| 9 | What we learned, honestly (who still beats us) | `grouped` |

If the person is present and the report is long, show them the spine before rendering. Otherwise proceed.

## Step 2: Pick a figure type for each claim

| The claim is about... | Use |
|---|---|
| a sequence, timeline or pipeline | `pk.flow(steps)` |
| "X plus the things we added" | `pk.layers(base, items)` |
| a set of parts, an opening or a shopping list | `pk.chips(items, notes)` |
| space, allocation or a layout | `pk.grid(cells, center)` |
| many identical copies ("everyone does the same") | `pk.tokens((n, label))` |
| a few final numbers, or before/after | `pk.bars(labels, values, notes)` |
| an ablation: cumulative gains, one change at a time | `pk.progress(labels, values, baseline)` |
| a comparison across segments | `pk.grouped(groups, {series: values})` |
| a trend over time | `pk.line(x, {series: y}, mark)` |
| a distribution plus "where we landed" | `pk.hist(values, marker)` |

## Step 3: Render with plotkit

1. Write the plotkit code from the end of this file to `plotkit.py` in the working directory, exactly as given.
2. Write one script, `make_figs.py`, that renders every figure into `figs/` as `01_...png`, `02_...png` and so on.

```python
import plotkit as pk
pk.setup("figs")
COLORS = {"baseline": "teal", "final": "green", "rival": "red"}   # decide once, reuse everywhere
paths = [
    pk.flow([...], title="<headline claim>", caption="<one line with the key number>", name="01_setup"),
    ...
]
pk.sheet(paths)   # contact sheet for the visual check in Step 6
```

Figure rules:
- **title:** the headline sentence. **caption:** one line carrying the key number and its n.
- **Same entity, same colour, in every figure** (the `COLORS` map above).
- **Flows:** at most 7 boxes, at most 12 words per box. Use `"\n"` to force a line break.
- **Bars:** direct value labels on the bars, no gridlines, a legend only when there is more than one series.
- **Axis ranges:** let the axis start above zero when all values sit in a narrow band (scores, ratings), and say so in the caption.

## Step 4: Write the text around each figure

- **Sentences:** about 20 words or fewer. **Paragraphs:** at most 4 sentences. Use active voice and "we" or "I".
- **Define each term the first time it appears, in plain words**, then keep using that exact term. For example: "Many rival tapes are 'floaters': every few hours they buy a big wheat lot to resell later."
- **One analogy per core idea, at most:** a music tape, a coin flip.
- **Every number gets its context:** "won 50 percent of its games against other tapes, with a median margin of 29 dollars"; "fires in about one game in ten and is worth about 1,000 dollars when it does."
- **Bold one key phrase per paragraph, at most.**
- **Use numbered or bulleted lists only for real enumerations** (the layers, the changes that mattered).
- **No hedging filler, no hype, no "we leveraged".** Say what the thing does.
- **The honest lesson goes near the end**, in one or two sentences: what still beats you and why.

## Step 5: Assemble with this template

```markdown
# <Title with a hook>: <subtitle> (explained simply)

<Team / author>. Final result: <score>, rank <r> of <N>. <One line on how it was built.>

<The problem in 3-4 plain sentences: what you do, what the catch is, how you win.>
![<alt>](figs/01_setup.png)

<One sentence on what follows.>

## Part 1: <first approach>, <its result>
### What is <the key term>?
...figure + short text...
### What we added
...
### Why it stalled
...

## Part 2: <second approach>, <its result>
### The idea
### How it was built: one measured change at a time
### The last trick: <name>

## Part 3: What happened
<result figure + 2-3 sentences>
### What we learned
<honest comparison figure + the moral in 1-2 sentences>

**Methods, for the curious:** <one dense paragraph: validation scheme, seeds, checks, tooling.>
```

Length: a competition writeup is usually 700-1,200 words. A stakeholder readout runs shorter and adds `## Decision` after the results.

## Step 6: Check before handing it over

1. **Open the contact sheet** (`figs/_contact_sheet.png`) and look at every figure. Check for:
   - overlapping or clipped text;
   - a caption colliding with the drawing;
   - unreadable tick labels;
   - colours that are inconsistent across figures.

   Fix any problem and re-render. Never skip this step.
2. **Headline-only read:** list the titles in order. Do they tell the story?
3. **Number audit:** every number in the text matches its figure and its source. Recompute any derived number (a percentage or a difference) in code.
4. **Jargon pass:** every term is defined on first use; nothing is left unexplained for the stated audience.

## Delivering

Deliver the Markdown file plus the `figs/` folder (zip both together). Offer a one-file HTML preview if useful.

For a Kaggle post, the images need public URLs; Chris hosts his in a GitHub repo and links the raw files. Keep the relative paths, and tell the person which files to upload and where to swap in the URLs.

## plotkit.py (write to disk verbatim)

```python
"""plotkit: figures for plot-oriented reports.

Every figure gets a HEADLINE title (a sentence that states the claim) and one CAPTION
line that carries the key number. Diagrams explain mechanisms; charts show numbers.

    import plotkit as pk
    pk.setup("figs")
    pk.flow(["Day 0\nbuy seeds", "Day 1\nhire hands", ("Day 29\nsell all", "yellow")],
            title='A "tape bot" plays the same script every game',
            caption="Hundreds of teams copied the same public notebook.", name="02_tape")

Diagram functions: flow, layers, chips, grid, tokens
Chart functions:   bars, progress, grouped, line, hist
Check:             sheet(paths) -> one contact-sheet PNG to look at every figure at once
"""
from __future__ import annotations

import os
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

# ---------------------------------------------------------------- palette
INK = "#1B3326"     # all text, outlines, arrows
MUTED = "#5F6F66"   # secondary text
C = dict(red="#B5524A", orange="#D9822B", teal="#1A8A9A", green="#1F7A4A",
         yellow="#E3B83E", brown="#8B5A2B", grey="#9AA3A0")          # strong fills
SOFT = dict(blue="#E3F0FB", yellow="#FFF6DA", red="#F3D1CA", green="#D1E7D7",
            grey="#EEEEEE", white="#FFFFFF")                          # light fills
SERIES = [C["teal"], C["green"], C["orange"], C["red"], C["yellow"], C["brown"]]

_CFG = {"out": "figs", "dpi": 150}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "text.color": INK,
})


def setup(outdir: str = "figs", dpi: int = 150) -> None:
    _CFG.update(out=outdir, dpi=dpi)
    os.makedirs(outdir, exist_ok=True)


def color(name: str) -> str:
    """'teal' / 'soft:blue' / '#hex' -> hex."""
    if name.startswith("#"):
        return name
    if name.startswith("soft:"):
        return SOFT[name[5:]]
    return C.get(name) or SOFT.get(name) or name


# ---------------------------------------------------------------- frame helpers
def _fig(w: float, h: float):
    return plt.figure(figsize=(w, h), facecolor="white")


def _frame(fig, title: str, caption: str | None):
    fig.suptitle(title, fontsize=17, fontweight="bold", color=INK, y=0.955)
    if caption:
        w_in = fig.get_size_inches()[0]
        width = max(40, int(w_in * 11))
        fig.text(0.5, 0.035, textwrap.fill(caption, width), ha="center", va="bottom",
                 fontsize=11.5, color=INK, linespacing=1.35)


def _canvas(fig, caption_lines: int = 1):
    bottom = 0.06 + 0.055 * max(caption_lines, 1) + 0.02
    ax = fig.add_axes([0.02, bottom, 0.96, 0.86 - bottom - 0.02])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return ax


def _caption_lines(fig, caption):
    if not caption:
        return 0
    width = max(40, int(fig.get_size_inches()[0] * 11))
    return len(textwrap.wrap(caption, width))


def _ax_inches(ax):
    bb = ax.get_position()
    w, h = ax.figure.get_size_inches()
    return bb.width * w, bb.height * h


def _text_in_box(ax, x, y, w, h, text, fs=12.0, bold=False, tc=INK, min_fs=8.0):
    """Wrap + shrink text until it fits inside a (x, y, w, h) data-unit box."""
    aw, ah = _ax_inches(ax)
    w_in, h_in = w / 100 * aw, h / 100 * ah
    size = fs
    while True:
        chars = max(4, int(w_in * 0.88 * 72 / (size * 0.60)))
        paras = [textwrap.fill(p, chars) if p else "" for p in str(text).split("\n")]
        wrapped = "\n".join(paras)
        n_lines = wrapped.count("\n") + 1
        longest = max(len(line) for line in wrapped.split("\n"))
        fits_h = n_lines * size * 1.32 / 72 <= h_in * 0.86
        fits_w = longest * size * 0.60 / 72 <= w_in * 0.92
        if (fits_h and fits_w) or size <= min_fs:
            break
        size -= 0.5
    ax.text(x + w / 2, y + h / 2, wrapped, ha="center", va="center", fontsize=size,
            fontweight="bold" if bold else "normal", color=tc, linespacing=1.25)


def _box(ax, x, y, w, h, text="", face="soft:blue", fs=12, bold=False, edge=INK, lw=1.6,
         rounded=True):
    face = color(face)
    aw, ah = _ax_inches(ax)
    aspect = (100 / ah) / (100 / aw)
    style = "round,pad=0,rounding_size=1.6" if rounded else "square,pad=0"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, mutation_aspect=aspect,
                                facecolor=face, edgecolor=edge, linewidth=lw))
    if text:
        dark = face in (C["red"], C["teal"], C["green"], C["brown"])
        _text_in_box(ax, x, y, w, h, text, fs=fs, bold=bold, tc="white" if dark else INK)


def _arrow(ax, p0, p1, lw=2.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=18,
                                 color=INK, linewidth=lw, shrinkA=0, shrinkB=0))


def _save(fig, name: str) -> str:
    os.makedirs(_CFG["out"], exist_ok=True)
    path = os.path.join(_CFG["out"], name if name.endswith(".png") else name + ".png")
    fig.savefig(path, dpi=_CFG["dpi"], facecolor="white")
    plt.close(fig)
    return path


def _norm(item, default_face):
    if isinstance(item, (tuple, list)):
        return item[0], color(item[1])
    return item, color(default_face)


# ---------------------------------------------------------------- diagrams
def flow(steps, title, caption=None, name="flow", face="soft:blue", w=12, h=4.6):
    """Left-to-right sequence of boxes joined by arrows. steps: str or (text, color)."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _canvas(fig, _caption_lines(fig, caption))
    n = len(steps)
    gap = 3.2 if n > 1 else 0
    bw = (96 - gap * (n - 1)) / n
    for i, s in enumerate(steps):
        text, f = _norm(s, face)
        x = 2 + i * (bw + gap)
        _box(ax, x, 12, bw, 76, text, f, fs=12.5)
        if i < n - 1:
            _arrow(ax, (x + bw + 0.2, 50), (x + bw + gap - 0.2, 50))
    return _save(fig, name)


def layers(base, items, title, caption=None, name="layers", base_face="soft:blue", w=12, h=5.4):
    """A base block plus N added layers. base: (heading, body). items: [(name, desc, color)]."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _canvas(fig, _caption_lines(fig, caption))
    _box(ax, 2, 4, 30, 92, "", base_face)
    head, body = base
    _text_in_box(ax, 2, 72, 30, 22, head, fs=13, bold=True)
    _text_in_box(ax, 2, 8, 30, 62, body, fs=11.5)
    n = len(items)
    gap = 4
    bh = (92 - gap * (n - 1)) / n
    for i, (nm, desc, col) in enumerate(items):
        y = 96 - (i + 1) * bh - i * gap
        _box(ax, 40, y, 27, bh, nm, col, fs=12.5, bold=True)
        _box(ax, 70, y, 28, bh, desc, "soft:white", fs=11.5)
        _arrow(ax, (32.3, 50), (39.8, y + bh / 2))
    return _save(fig, name)


def chips(items, title, caption=None, notes=None, name="chips", face="soft:green", w=12, h=4.8):
    """A row of tiles (a shopping list, a set of parts). notes: extra lines under the row."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _canvas(fig, _caption_lines(fig, caption))
    n = len(items)
    gap = 1.8
    bw = (96 - gap * (n - 1)) / n
    top = 96 if not notes else 98
    bh = 52 if notes else 76
    for i, it in enumerate(items):
        text, f = _norm(it, face)
        _box(ax, 2 + i * (bw + gap), top - bh, bw, bh, text, f, fs=12.5, bold=True)
    if notes:
        lines = notes if isinstance(notes, (list, tuple)) else [notes]
        step = min(11.0, (top - bh - 4) / (len(lines) + 0.5))
        for j, line in enumerate(lines):
            ax.text(50, top - bh - (j + 0.8) * step, line, ha="center", va="center",
                    fontsize=11.5, color=MUTED if line.startswith("(") else INK,
                    style="italic" if line.startswith("(") else "normal")
    return _save(fig, name)


def grid(cells, title, caption=None, center=None, name="grid", w=10, h=8):
    """A layout map. cells: rows of (text, color). center: optional (label, color) badge."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _canvas(fig, _caption_lines(fig, caption))
    rows, cols = len(cells), max(len(r) for r in cells)
    cw, ch = 96 / cols, 96 / rows
    for r, row in enumerate(cells):
        for c, cell in enumerate(row):
            text, f = _norm(cell, "soft:grey")
            x, y = 2 + c * cw, 98 - (r + 1) * ch
            ax.add_patch(Rectangle((x, y), cw, ch, facecolor=f, edgecolor=INK, linewidth=2))
            _text_in_box(ax, x, y, cw, ch, text, fs=13)
    if center:
        label, f = _norm(center, "brown")
        ax.add_patch(Rectangle((44, 43), 12, 14, facecolor=f, edgecolor=INK, linewidth=1.5))
        ax.text(50, 50, label, ha="center", va="center", fontsize=12, fontweight="bold",
                color="white")
    return _save(fig, name)


def tokens(labels, title, caption=None, name="tokens", face="soft:blue", w=12, h=4.4):
    """A row of identical circles (many copies of the same thing). labels: list or (n, text)."""
    if isinstance(labels, tuple):
        labels = [labels[1]] * labels[0]
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _canvas(fig, _caption_lines(fig, caption))
    n = len(labels)
    xs = [100 * (i + 0.5) / n for i in range(n)]
    faces = []
    for lab in labels:
        t, f = _norm(lab, face)
        faces.append((t, f))
    diam = min(72.0, fig.get_size_inches()[0] * 72 * 0.8 / n)   # circle diameter in points
    ax.scatter(xs, [50] * n, s=diam ** 2, c=[f for _, f in faces], edgecolors=INK,
               linewidths=1.6, zorder=2)
    longest = max(len(str(t)) for t, _ in faces)
    fs = max(7.0, min(12.0, diam * 0.78 / (longest * 0.62)))
    for x, (t, _) in zip(xs, faces):
        ax.text(x, 50, t, ha="center", va="center", fontsize=fs, zorder=3)
    return _save(fig, name)


# ---------------------------------------------------------------- charts
def _chart(fig, caption):
    lines = _caption_lines(fig, caption)
    bottom = 0.16 + 0.05 * max(lines - 1, 0)
    ax = fig.add_axes([0.085, bottom + 0.06, 0.885, 0.84 - bottom - 0.12])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=11)
    return ax


def _wrap_labels(labels, width=12):
    return [textwrap.fill(str(lbl), width) for lbl in labels]


def _fit_xticks(ax, labels, fs=11.0):
    """Wrap tick labels to the width each bar slot actually has, so they never collide."""
    aw, _ = _ax_inches(ax)
    slot_in = aw / max(len(labels), 1)
    chars = max(6, int(slot_in * 0.9 * 72 / (fs * 0.6)))
    while chars < max(len(w) for lbl in labels for w in str(lbl).split()) and fs > 8:
        fs -= 0.5
        chars = max(6, int(slot_in * 0.9 * 72 / (fs * 0.6)))
    ax.set_xticks(range(len(labels)), _wrap_labels(labels, chars), fontsize=fs)


def bars(labels, values, title, ylabel="", caption=None, colors=None, fmt="{:,.0f}",
         notes=None, ylim=None, name="bars", w=10, h=6):
    """Simple bars, one per item (final results, before/after). notes: text above each bar."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _chart(fig, caption)
    cols = [color(c) for c in (colors or [SERIES[i % len(SERIES)] for i in range(len(values))])]
    x = range(len(values))
    rects = ax.bar(x, values, width=0.55, color=cols, edgecolor=INK, linewidth=1)
    lo, hi = ylim if ylim else (0, max(values) * 1.18)
    ax.set_ylim(lo, hi)
    _fit_xticks(ax, labels, fs=12)
    ax.set_ylabel(ylabel, fontsize=11.5)
    pad = (hi - lo) * 0.015
    for r, v, i in zip(rects, values, x):
        txt = notes[i] if notes else (fmt.format(v) if isinstance(fmt, str) else fmt(v))
        ax.text(r.get_x() + r.get_width() / 2, v + pad, txt, ha="center", va="bottom",
                fontsize=14, fontweight="bold", color=INK, linespacing=1.15)
    return _save(fig, name)


def progress(labels, values, title, ylabel="", caption=None, fmt="{:.0f}%", bar_color="green",
             baseline=None, ylim=None, highlight=None, name="progress", w=12, h=6.2):
    """'One measured change at a time': cumulative bars left to right.
    baseline: (value, label) dashed reference line. highlight: indexes drawn in orange."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _chart(fig, caption)
    cols = [color(bar_color)] * len(values)
    for i in (highlight or []):
        cols[i] = C["orange"]
    x = range(len(values))
    rects = ax.bar(x, values, width=0.8, color=cols, edgecolor=INK, linewidth=1)
    lo, hi = ylim if ylim else (0, max(values) * 1.18)
    ax.set_ylim(lo, hi)
    _fit_xticks(ax, labels, fs=10.5)
    ax.set_ylabel(ylabel, fontsize=11.5)
    pad = (hi - lo) * 0.012
    for r, v in zip(rects, values):
        txt = fmt.format(v) if isinstance(fmt, str) else fmt(v)
        ax.text(r.get_x() + r.get_width() / 2, v + pad, txt, ha="center", va="bottom",
                fontsize=11.5, fontweight="bold", color=INK)
    if baseline:
        bv, bl = baseline
        ax.axhline(bv, color=MUTED, linestyle="--", linewidth=1.3, zorder=0)
        ax.text(-0.45, bv + pad, bl, ha="left", va="bottom", fontsize=10.5, color=MUTED,
                zorder=4, bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    return _save(fig, name)


def grouped(groups, series, title, ylabel="", caption=None, colors=None, fmt="{:.0f}%",
            ylim=None, name="grouped", w=12, h=6.2):
    """Segments on x, one bar per series. series: {name: [values per group]}."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _chart(fig, caption)
    names = list(series)
    k = len(names)
    width = 0.8 / k
    allv = [v for vals in series.values() for v in vals]
    lo, hi = ylim if ylim else (0, max(allv) * 1.2)
    ax.set_ylim(lo, hi)
    pad = (hi - lo) * 0.012
    for j, nm in enumerate(names):
        col = color((colors or {}).get(nm, SERIES[j % len(SERIES)]) if isinstance(colors, dict)
                    else (colors[j] if colors else SERIES[j % len(SERIES)]))
        xs = [i - 0.4 + width * (j + 0.5) for i in range(len(groups))]
        rects = ax.bar(xs, series[nm], width=width, color=col, edgecolor=INK, linewidth=1, label=nm)
        for r, v in zip(rects, series[nm]):
            txt = fmt.format(v) if isinstance(fmt, str) else fmt(v)
            ax.text(r.get_x() + r.get_width() / 2, v + pad, txt, ha="center", va="bottom",
                    fontsize=11, color=INK)
    _fit_xticks(ax, groups, fs=12)
    ax.set_ylabel(ylabel, fontsize=11.5)
    if k > 1:
        ax.legend(frameon=False, fontsize=11, loc="upper right")
    return _save(fig, name)


def line(x, series, title, ylabel="", xlabel="", caption=None, colors=None, fmt="{:.2f}",
         ylim=None, mark=None, name="line", w=12, h=6):
    """Trends with direct end labels (no legend). series: {name: [y]}. mark: (x, label)."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _chart(fig, caption)
    for j, (nm, ys) in enumerate(series.items()):
        col = color((colors or {}).get(nm, SERIES[j % len(SERIES)]) if isinstance(colors, dict)
                    else SERIES[j % len(SERIES)])
        ax.plot(x, ys, color=col, linewidth=2.6, marker="o", markersize=5)
        ax.text(x[-1], ys[-1], f"  {nm} {fmt.format(ys[-1])}", color=col, fontsize=11.5,
                fontweight="bold", va="center")
    if ylim:
        ax.set_ylim(*ylim)
    if mark:
        ax.axvline(mark[0], color=MUTED, linestyle="--", linewidth=1.2)
        ax.text(mark[0], ax.get_ylim()[1], f" {mark[1]}", color=MUTED, fontsize=10.5, va="top")
    ax.set_ylabel(ylabel, fontsize=11.5)
    ax.set_xlabel(xlabel, fontsize=11.5)
    ax.margins(x=0.02)
    ax.set_xlim(right=ax.get_xlim()[1] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.18)
    return _save(fig, name)


def hist(values, title, xlabel="", caption=None, marker=None, bins=30, fmt="{:.3f}",
         bar_color="teal", name="hist", w=12, h=5.6):
    """Distribution with an optional 'you are here' marker. marker: (value, label)."""
    fig = _fig(w, h)
    _frame(fig, title, caption)
    ax = _chart(fig, caption)
    ax.hist(values, bins=bins, color=color(bar_color), edgecolor=INK, linewidth=0.8)
    ax.set_xlabel(xlabel, fontsize=11.5)
    ax.set_ylabel("count", fontsize=11.5)
    if marker:
        mv, ml = marker
        ax.axvline(mv, color=C["red"], linewidth=2.4, zorder=3)
        ax.set_ylim(top=ax.get_ylim()[1] * 1.15)
        ax.text(mv, ax.get_ylim()[1] * 0.98, f" {ml} ", color=C["red"], fontsize=12,
                fontweight="bold", va="top", ha="left", zorder=4,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    return _save(fig, name)


# ---------------------------------------------------------------- check
def sheet(paths, name="_contact_sheet", cols=2, w_each=7.0):
    """Tile every figure into one PNG so you can LOOK at all of them in one pass."""
    import math

    import matplotlib.image as mpimg

    rows = math.ceil(len(paths) / cols)
    imgs = [mpimg.imread(p) for p in paths]
    h_each = w_each * max(i.shape[0] / i.shape[1] for i in imgs)
    fig, axes = plt.subplots(rows, cols, figsize=(w_each * cols, h_each * rows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, img, p in zip(axes.flat, imgs, paths):
        ax.imshow(img)
        ax.set_title(os.path.basename(p), fontsize=9, color=MUTED)
    fig.tight_layout()
    return _save(fig, name)
```