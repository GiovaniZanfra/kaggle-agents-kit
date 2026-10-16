"""Relatório da campanha calculado a partir dos dados — não do que os agentes dizem.

    python src/campaign_report.py                    # campanha = tudo registrado desde o último relatório
    python src/campaign_report.py --since 2026-10-15T14:00
    python src/campaign_report.py --authors j1,j2,j3 # só esses jobs

Saída (pasta de artefatos): reports/campaigns/cNN/
  figs/01_deltas.png        cada experimento vs. o pai, com o ruído pareado entre folds
  figs/02_trajetoria.png    melhor modelo único e ensemble nested ao longo do tempo
  figs/03_contribuicao.png  peso de cada job no ensemble atual
  figs/_contact_sheet.png   todas as figuras numa imagem, para conferir de uma vez
  data.json                 todos os números usados (fonte única para o texto)
  report_skeleton.md        títulos calculados, figuras, tabelas e checagem dos learnings

O gerente escreve report.md em cima do esqueleto usando skills/plot-story-report
(ver prompts/30_manager.md). Rode ANTES de mover os learnings para _done/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plotkit as pk  # noqa: E402
from common import (CFG, ENS_DIR, LEARN_DIR, REPORT_DIR, blocked_models, get_folds, get_target,  # noqa: E402
                    higher_is_better, load_meta, load_oof, per_fold_scores, read_registry)

CAMP_DIR = REPORT_DIR / "campaigns"
INDEX = CAMP_DIR / "index.json"
GREEN, ORANGE, RED, GREY = "#1F7A4A", "#D9822B", pk.C["red"], pk.C["grey"]
VERDICT_COLOR = {"melhor": GREEN, "ruído": GREY, "pior": RED, "referência": pk.SOFT["blue"]}
CITE_RE = re.compile(r"\b([a-z0-9]+_[a-z0-9]+_\d{3,})\b[^\n]{0,60}?(\d+\.\d{3,})")


# --------------------------------------------------------------------------- dados

class Lazy:
    """Target e folds só são lidos se algum meta não tiver fold_scores."""

    def __init__(self):
        self._y = self._folds = None

    def fold_scores(self, name: str) -> np.ndarray:
        fs = load_meta(name).get("fold_scores")
        if fs:
            return np.asarray(fs, dtype=float)
        if self._y is None:
            self._y, self._folds = get_target(), get_folds()
        return np.asarray(per_fold_scores(self._y, load_oof(name), self._folds), dtype=float)


def load_index() -> list:
    return json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else []


def audit_status() -> dict:
    p = REPORT_DIR / "audit.json"
    if not p.exists():
        return {}
    return {n: i.get("status", "") for n, i in json.loads(p.read_text(encoding="utf-8"))["models"].items()}


def decimals(values) -> int:
    m = max([abs(v) for v in values if v == v] + [1e-12])
    return int(max(2, min(6, 2 - math.floor(math.log10(m)))))


def check_learnings(reg: pd.DataFrame, authors: set) -> tuple[list, list]:
    """Procura 'nome ... 0.xxxx' nos learnings e compara com o registry."""
    cv = dict(zip(reg["name"], reg["cv"].astype(float)))
    rows, seen = [], set()
    files = sorted(p for p in LEARN_DIR.glob("*.md")) if LEARN_DIR.exists() else []
    for p in files:
        parts = p.stem.split("_")
        author = parts[1] if len(parts) > 1 else ""
        if authors and author not in authors:
            continue
        seen.add(author)
        for name, num in CITE_RE.findall(p.read_text(encoding="utf-8")):
            dec = len(num.split(".")[1])
            cited = float(num)
            if name not in cv:
                rows.append({"file": p.name, "name": name, "cited": cited, "registry": None, "status": "não registrado"})
                continue
            ok = abs(cited - cv[name]) <= 0.5 * 10 ** (-dec) + 1e-9
            rows.append({"file": p.name, "name": name, "cited": cited, "registry": cv[name],
                         "status": "ok" if ok else "DIVERGE"})
    missing = sorted(a for a in authors if a not in seen)
    return rows, missing


# --------------------------------------------------------------------------- figuras

def _axes(fig, caption, left=0.085):
    lines = pk._caption_lines(fig, caption)
    bottom = 0.16 + 0.05 * max(lines - 1, 0)
    ax = fig.add_axes([left, bottom + 0.06, 0.97 - left, 0.84 - bottom - 0.12])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=11)
    return ax


def fig_deltas(exps: list, title: str, caption: str, p: int) -> str:
    n = len(exps)
    fig = pk._fig(12, max(4.2, 2.0 + 0.45 * n))
    pk._frame(fig, title, caption)
    ax = _axes(fig, caption, left=0.24)
    ys = np.arange(n)[::-1]
    vals = [e["delta"] for e in exps]
    errs = [2 * e["se"] for e in exps]
    cols = [VERDICT_COLOR[e["verdict"]] for e in exps]
    ax.barh(ys, vals, height=0.62, color=cols, edgecolor=pk.INK, linewidth=1)
    ax.errorbar(vals, ys, xerr=errs, fmt="none", ecolor=pk.INK, elinewidth=1.4, capsize=4)
    ax.axvline(0, color=pk.INK, linewidth=1.2)
    span = max([abs(v) + e for v, e in zip(vals, errs)] + [1e-9])
    ax.set_xlim(-span * 1.9, span * 1.9)
    for y, e, v, er in zip(ys, exps, vals, errs):
        shown_v = 0.0 if abs(v) < 0.5 * 10 ** (-p) else v
        label = "ref." if e["verdict"] == "referência" else f"{shown_v:+.{p}f}  {e['verdict']}"
        x = v + er if v >= 0 else v - er
        ax.text(x + (0.03 if v >= 0 else -0.03) * span, y, label, va="center",
                ha="left" if v >= 0 else "right", fontsize=11, color=pk.INK)
    names = [e["name"] + (f"  ({e['audit']})" if e["audit"] in ("WARN", "FAIL", "BLOQ") else "") for e in exps]
    ax.set_yticks(ys, names, fontsize=11)
    ax.set_xlabel(f"melhoria em {CFG['metric']} (positivo = melhor)", fontsize=11.5)
    ax.grid(False)
    return pk._save(fig, "01_deltas")


def fig_trajectory(reg: pd.DataFrame, hist: pd.DataFrame, since, sign: float, title: str, caption: str,
                   p: int) -> str:
    fig = pk._fig(12, 6)
    pk._frame(fig, title, caption)
    ax = _axes(fig, caption)
    r = reg.sort_values("created_dt")
    best, xs, ys = None, [], []
    for t, v in zip(r["created_dt"], r["cv"].astype(float)):
        best = v if best is None else (max(best, v) if sign > 0 else min(best, v))
        xs.append(t)
        ys.append(best)
    ax.step(xs, ys, where="post", color=GREEN, linewidth=2.6)
    ax.plot(xs[-1], ys[-1], "o", color=GREEN, markersize=8)
    ax.annotate(f" melhor único {ys[-1]:.{p}f}", (xs[-1], ys[-1]), color=pk.INK, fontsize=11.5,
                fontweight="bold", va="bottom", ha="right", xytext=(0, 6), textcoords="offset points")
    if not hist.empty and hist["cv_nested"].notna().any():
        h = hist.dropna(subset=["cv_nested"]).sort_values("created_dt")
        ax.plot(h["created_dt"], h["cv_nested"], color=ORANGE, linewidth=2.0, linestyle="--", marker="o",
                markersize=8, zorder=3)
        ax.annotate(f" ensemble nested {h['cv_nested'].iloc[-1]:.{p}f}", (h["created_dt"].iloc[-1], h["cv_nested"].iloc[-1]),
                    color=pk.INK, fontsize=11.5, fontweight="bold", va="top", ha="right",
                    xytext=(0, -8), textcoords="offset points")
    if since is not None:
        ax.axvline(since, color=pk.MUTED, linestyle="--", linewidth=1.2)
        ax.text(since, ax.get_ylim()[1], " início da campanha", color=pk.MUTED, fontsize=10.5, va="top")
    ax.set_ylabel(f"CV ({CFG['metric']})", fontsize=11.5)
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
    return pk._save(fig, "02_trajetoria")


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="ISO datetime; padrão: fim do relatório anterior")
    ap.add_argument("--authors", default="", help="lista de autores/jobs separados por vírgula")
    ap.add_argument("--redo", action="store_true", help="refaz o último relatório (mesmo id e mesmo início)")
    args = ap.parse_args()

    reg = read_registry()
    if reg.empty:
        sys.exit("registry vazio")
    reg["created_dt"] = pd.to_datetime(reg["created_at"])
    reg["cv"] = reg["cv"].astype(float)
    sign = 1.0 if higher_is_better() else -1.0
    index = load_index()
    if args.redo and index:
        last = index.pop()
        args.since = args.since or last["since"]
    since = pd.Timestamp(args.since) if args.since else (pd.Timestamp(index[-1]["until"]) if index else None)
    authors = {a for a in args.authors.split(",") if a}
    camp = reg if since is None else reg[reg["created_dt"] > since]
    if authors:
        camp = camp[camp["author"].isin(authors)]
    if camp.empty:
        sys.exit(f"nenhum experimento novo desde {since}")
    camp = camp.sort_values("created_dt")
    cid = f"c{len(index) + 1:02d}"
    out = CAMP_DIR / cid
    pk.setup(str(out / "figs"))

    blocked = blocked_models()
    audit = audit_status()
    lazy = Lazy()
    names = set(reg["name"])
    k = int(CFG["n_folds"])

    before = reg if since is None else reg[reg["created_dt"] <= since]
    before = before[(before["level"] == 1) & ~before["name"].isin(list(blocked))]
    if since is not None and not before.empty:
        ref = before.sort_values("cv", ascending=sign < 0)["name"].iloc[0]
    else:
        ref = camp[camp["level"] == 1]["name"].iloc[0] if (camp["level"] == 1).any() else camp["name"].iloc[0]
    cv_of = dict(zip(reg["name"], reg["cv"]))

    exps = []
    for row in camp.itertuples():
        base = row.parent if isinstance(row.parent, str) and row.parent in names else ref
        st = "BLOQ" if row.name in blocked else audit.get(row.name, "sem audit")
        e = {"name": row.name, "author": row.author, "level": int(row.level), "cv": float(row.cv),
             "base": base, "audit": st}
        if base == row.name:
            e.update(delta=0.0, se=0.0, verdict="referência")
        else:
            d = sign * (lazy.fold_scores(row.name) - lazy.fold_scores(base))
            se = float(np.std(d, ddof=1) / np.sqrt(len(d))) if len(d) > 1 else 0.0
            delta = sign * (float(row.cv) - float(cv_of[base]))
            thr = max(2 * se, 1e-6)
            verdict = "melhor" if delta > thr else ("pior" if delta < -thr else "ruído")
            e.update(delta=delta, se=se, verdict=verdict)
        exps.append(e)

    shown = [e for e in exps if e["audit"] not in ("BLOQ", "FAIL")]
    hidden = [e["name"] for e in exps if e["audit"] in ("BLOQ", "FAIL")]
    p = decimals([e["delta"] for e in shown if e["verdict"] != "referência"] + [1e-4])
    n_eval = sum(e["verdict"] != "referência" for e in shown)
    n_better = sum(e["verdict"] == "melhor" for e in shown)
    n_worse = sum(e["verdict"] == "pior" for e in shown)
    t1 = (f"{n_better} de {n_eval} experimentos {'melhorou' if n_better == 1 else 'melhoraram'} além do ruído" if n_better
          else f"Nenhum dos {n_eval} experimentos passou do ruído")
    c1 = (f"Melhoria = CV do experimento − CV da base (o pai; sem pai: {ref}). Barra de erro = ±2 erros-padrão "
          f"das diferenças por fold (k={k}). {n_worse} {'piorou' if n_worse == 1 else 'pioraram'} além do ruído."
          + (f" Fora do gráfico (bloqueados/FAIL): {', '.join(hidden)}." if hidden else ""))
    f1 = fig_deltas(shown or exps, t1, c1, p)

    # trajetória
    ok_reg = reg[(reg["level"] == 1) & ~reg["name"].isin(list(blocked))]
    hist_path = ENS_DIR / "history.csv"
    hist = pd.read_csv(hist_path) if hist_path.exists() else pd.DataFrame(columns=["created_at", "cv_nested"])
    hist["created_dt"] = pd.to_datetime(hist["created_at"]) if len(hist) else pd.Series(dtype="datetime64[ns]")
    b_before = (before["cv"].max() if sign > 0 else before["cv"].min()) if not before.empty and since is not None else None
    b_after = ok_reg["cv"].max() if sign > 0 else ok_reg["cv"].min()
    ens_last = float(hist["cv_nested"].dropna().iloc[-1]) if len(hist) and hist["cv_nested"].notna().any() else None
    pt = decimals([b_after]) + 2
    t2 = (f"Melhor único {b_before:.{pt}f} → {b_after:.{pt}f}" if b_before is not None and b_after != b_before
          else f"Melhor único parado em {b_after:.{pt}f}" if b_before is not None else f"Melhor único: {b_after:.{pt}f}")
    if ens_last is not None:
        t2 += f"; ensemble nested {ens_last:.{pt}f}"
    c2 = "Linha verde: melhor modelo de nível 1 registrado até cada momento (sem bloqueados). Laranja: CV nested de cada ensemble."
    f2 = fig_trajectory(ok_reg, hist, since, sign, t2, c2, pt)

    # contribuição no ensemble
    camp_authors = sorted(set(camp["author"]))
    latest = sorted(ENS_DIR.glob("hc_*.json"))
    contrib, ens_info = [], None
    if latest:
        ens_info = json.loads(latest[-1].read_text(encoding="utf-8"))
        author_of = dict(zip(reg["name"], reg["author"]))
        camp_names = set(camp["name"])
        share = {}
        for n, w in ens_info["weights"].items():
            key = author_of.get(n, "?") if n in camp_names else "anteriores"
            share[key] = share.get(key, 0.0) + 100 * w
        for a in camp_authors + ["anteriores"]:
            ea = [e for e in exps if e["author"] == a]
            contrib.append({"author": a, "weight_pct": round(share.get(a, 0.0), 1), "n_exps": len(ea),
                            "n_better": sum(e["verdict"] == "melhor" for e in ea)})
        camp_pct = sum(c["weight_pct"] for c in contrib if c["author"] != "anteriores")
        plot_rows = [c for c in contrib if c["author"] != "anteriores" and c["weight_pct"] > 0]
        zero = [c for c in contrib if c["author"] != "anteriores" and c["weight_pct"] == 0]
        if zero:
            plot_rows.append({"author": f"outros {len(zero)} jobs", "weight_pct": 0.0,
                              "n_exps": sum(c["n_exps"] for c in zero), "n_better": sum(c["n_better"] for c in zero)})
        prev = next(c for c in contrib if c["author"] == "anteriores")
        if since is not None or prev["weight_pct"] > 0:
            plot_rows.append(prev)
        t3 = f"Modelos desta campanha levam {camp_pct:.0f}% do peso do ensemble"
        c3 = (f"Pesos do {ens_info['id']} (hill climbing). Jobs sem peso aparecem agregados em cinza; "
              "o detalhe está na tabela do relatório.")
        stale = since is not None and pd.Timestamp(ens_info["created_at"]) <= since
        if stale:
            c3 = f"ATENÇÃO: {ens_info['id']} é anterior à campanha — rode hill_climb.py. " + c3
        labels = [f"{c['author']} ({c['n_exps']} exps)" if c["author"] != "anteriores" else "campanhas anteriores"
                  for c in plot_rows]
        cols = [GREY if c["author"] == "anteriores" or c["weight_pct"] == 0 else GREEN for c in plot_rows]
        f3 = pk.bars(labels, [c["weight_pct"] for c in plot_rows], title=t3, ylabel="% do peso", caption=c3,
                     colors=cols, fmt="{:.0f}%", name="03_contribuicao")
    else:
        for a in camp_authors:
            ea = [e for e in exps if e["author"] == a]
            contrib.append({"author": a, "weight_pct": None, "n_exps": len(ea),
                            "n_better": sum(e["verdict"] == "melhor" for e in ea)})
        t3 = f"{len(camp)} experimentos em {len(camp_authors)} jobs (sem ensemble ainda)"
        c3 = "Rode python src/hill_climb.py --nested para ver a contribuição de cada job no ensemble."
        f3 = pk.bars([c["author"] for c in contrib], [c["n_better"] for c in contrib], title=t3,
                     ylabel="experimentos além do ruído", caption=c3, colors=[GREEN] * len(contrib),
                     fmt="{:.0f}", name="03_contribuicao")
    sheet = pk.sheet([f1, f2, f3])

    cites, missing = check_learnings(reg, set(camp_authors))
    n_div = sum(c["status"] != "ok" for c in cites)
    until = reg["created_dt"].max().isoformat()
    data = {
        "id": cid, "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "since": since.isoformat() if since is not None else None, "until": until, "metric": CFG["metric"],
        "higher_is_better": sign > 0, "reference": ref, "best_single_before": b_before, "best_single_after": b_after,
        "ensemble": ({"id": ens_info["id"], "cv_nested": ens_info.get("cv_nested"),
                      "cv_insample": ens_info.get("cv_insample"), "weights": ens_info["weights"]} if ens_info else None),
        "experiments": exps, "contribution": contrib, "learnings_citations": cites,
        "authors_without_learnings": missing,
        "titles": [t1, t2, t3], "figures": [Path(f).name for f in (f1, f2, f3)],
    }
    (out / "data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    st_counts = {s: sum(e["audit"] == s for e in exps) for s in ("OK", "WARN", "FAIL", "BLOQ")}
    lines = [
        f"# Campanha {cid} — {dt.date.today():%d/%m/%Y}",
        "",
        "<!-- Esqueleto gerado por src/campaign_report.py. Figuras e números vêm do registry, não dos agentes.",
        "     O gerente escreve report.md a partir daqui (prompts/30_manager.md + skills/plot-story-report/KIT.md). -->",
        "",
        f"**Resultado:** {len(camp)} experimentos de {len(camp_authors)} jobs; {n_better} acima do ruído, "
        f"{n_worse} abaixo. Melhor único {b_after:.{pt}f}"
        + (f" (antes {b_before:.{pt}f})" if b_before is not None else "")
        + (f"; ensemble nested {ens_last:.{pt}f} ({ens_info['id']})" if ens_info and ens_last is not None else "")
        + f". Audit: OK {st_counts['OK']}, WARN {st_counts['WARN']}, FAIL {st_counts['FAIL']}, BLOQ {st_counts['BLOQ']}.",
        "",
        f"## {t1}", "", "![](figs/01_deltas.png)", "", "<!-- TEXTO: o que separa os 'melhor' dos 'ruído'? -->", "",
        f"## {t2}", "", "![](figs/02_trajetoria.png)", "", "<!-- TEXTO: a campanha moveu o teto? -->", "",
        f"## {t3}", "", "![](figs/03_contribuicao.png)", "", "<!-- TEXTO: quem trouxe diversidade? -->", "",
        "## Experimentos da campanha", "",
        "| experimento | job | base | CV | melhoria | ±2·se | veredito | audit |", "|---|---|---|---|---|---|---|---|",
    ]
    for e in exps:
        lines.append(f"| {e['name']} | {e['author']} | {e['base']} | {e['cv']:.{pt}f} | {e['delta']:+.{p}f} | "
                     f"{2 * e['se']:.{p}f} | {e['verdict']} | {e['audit']} |")
    lines += ["", f"## Checagem dos learnings ({len(cites)} CVs citados, {n_div} divergências)", ""]
    if cites:
        lines += ["| arquivo | experimento | citado | registry | status |", "|---|---|---|---|---|"]
        for c in cites:
            reg_txt = f"{c['registry']:.6f}" if c["registry"] is not None else "—"
            lines.append(f"| {c['file']} | {c['name']} | {c['cited']} | {reg_txt} | {c['status']} |")
    else:
        lines.append("- nenhum CV citado nos learnings desta campanha")
    lines += ["", "**Jobs sem learnings:** " + (", ".join(missing) if missing else "nenhum")]
    (out / "report_skeleton.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    index.append({"id": cid, "since": data["since"], "until": until, "n_experiments": len(camp)})
    INDEX.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"[ok] {cid}: {len(camp)} experimento(s) | {n_better} acima do ruído, {n_worse} abaixo | "
          f"{n_div} citações divergentes | sem learnings: {', '.join(missing) or 'nenhum'}")
    print(f"     {out / 'report_skeleton.md'}\n     {sheet}")


if __name__ == "__main__":
    main()
