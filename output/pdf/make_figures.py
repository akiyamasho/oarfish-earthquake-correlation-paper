from pathlib import Path
import math

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
import numpy as np


OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)

BLUE = "#1f77b4"
ORANGE = "#ff7f0e"
GREEN = "#2ca02c"
RED = "#d62728"
GRAY = "#6b7280"
LIGHT = "#f3f4f6"


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def add_box(ax, xy, text, w=0.24, h=0.12, fc=LIGHT, ec=GRAY, fs=8):
    x, y = xy
    box = Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=1.1,
                    zorder=2)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            zorder=3)
    return box


def add_arrow(ax, start, end, color=GRAY):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=12,
                                 linewidth=1.2, color=color, zorder=1))


def global_linkage_schematic():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.set_xlim(-10, 200)
    ax.set_ylim(-0.9, 2.6)
    ax.axis("off")

    ax.add_patch(Rectangle((0, -0.12), 7, 0.24, facecolor="#dbeafe", edgecolor="none"))
    ax.add_patch(Rectangle((7, -0.12), 173, 0.24, facecolor="#fef3c7", edgecolor="none"))
    ax.hlines(0, 0, 180, color="#111827", linewidth=2.2)
    for x in [0, 7, 90, 180]:
        ax.vlines(x, -0.13, 0.13, color="#111827", linewidth=1)
        ax.text(x, -0.32, f"{x}d", ha="center", fontsize=9)
    ax.text(38, -0.62, "0-7d short-window sensitivity", ha="center",
            fontsize=8, color=BLUE)
    ax.text(105, 0.32, "primary global window: 0-180 days, no radius",
            ha="center", fontsize=9, weight="bold")

    ax.scatter([0], [0], s=170, marker="*", color=ORANGE, zorder=4)
    ax.text(-6, 0.68, "Feb 20, 2026\nMexico oarfish", ha="left", fontsize=9)

    quake_x = [107, 124, 124]
    quake_y = [0.82, 1.24, 0.68]
    quake_labels = ["Jun 7\nPH M7.8", "Jun 24\nJP M6.9", "Jun 24\nVE M7.5/M7.2"]
    quake_colors = [BLUE, GREEN, RED]
    for x, y, label, color in zip(quake_x, quake_y, quake_labels, quake_colors):
        ax.scatter([x], [y], s=65, color=color, edgecolor="white", zorder=5)
        ax.text(x, y + 0.2, label, ha="center", fontsize=8)

    ax.annotate("Worldwide earthquake catalog:\nall qualifying events are eligible",
                xy=(124, 1.18), xytext=(100, 2.05),
                arrowprops=dict(arrowstyle="->", color=GRAY),
                ha="center", fontsize=9)

    inset = Circle((24, 1.8), 0.42, fill=False, edgecolor=GRAY, linewidth=1.2)
    ax.add_patch(inset)
    ax.scatter([24], [1.8], s=35, marker="*", color=ORANGE)
    ax.scatter([24.34], [1.95], s=30, color=BLUE)
    ax.text(39, 1.78, "Secondary local checks:\n100, 500, 1000 km", va="center", fontsize=8)
    add_arrow(ax, (24.5, 1.8), (37, 1.8))

    ax.text(90, 2.42, "Global sighting-to-earthquake linkage", ha="center",
            fontsize=13, weight="bold")
    save(fig, "global_linkage_schematic")


def pipeline_diagram():
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    boxes = [
        ((0.04, 0.68), "Raw sighting\nsources"),
        ((0.31, 0.68), "Taxonomy,\ntime, location\nharmonization"),
        ((0.58, 0.68), "Accepted\nRegalecidae\nevents"),
        ((0.04, 0.28), "Official\nearthquake\ncatalogs"),
        ((0.31, 0.28), "Global 0-180d\nlinkage table"),
        ((0.58, 0.28), "Permutation\nnull models"),
    ]
    for xy, text in boxes:
        add_box(ax, xy, text, w=0.22, h=0.18, fs=8)
    add_box(ax, (0.80, 0.47), "Tables,\nfigures,\ninference", w=0.16, h=0.18, fc="#e0f2fe")

    for a, b in [((0.26, 0.77), (0.31, 0.77)), ((0.53, 0.77), (0.58, 0.77)),
                 ((0.69, 0.68), (0.80, 0.57)), ((0.26, 0.37), (0.31, 0.37)),
                 ((0.53, 0.37), (0.58, 0.37)), ((0.69, 0.46), (0.80, 0.54)),
                 ((0.15, 0.68), (0.39, 0.46)), ((0.15, 0.46), (0.39, 0.37))]:
        add_arrow(ax, a, b)
    ax.text(0.5, 0.94, "Reproducible 1980-2026 study pipeline", ha="center",
            fontsize=13, weight="bold")
    save(fig, "pipeline_diagram")


def null_model_schematic():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    add_box(ax, (0.05, 0.62), "Observed\nsighting dates", w=0.18, h=0.16, fc="#fff7ed")
    add_box(ax, (0.32, 0.62), "Observed\n0-180d\nhit count", w=0.18, h=0.16, fc="#e0f2fe")
    add_box(ax, (0.05, 0.24), "Stratum-preserving\ncontrol dates", w=0.18, h=0.16)
    add_box(ax, (0.32, 0.24), "Null replicate\nhit counts", w=0.18, h=0.16)
    add_box(ax, (0.68, 0.43), "Empirical p-value:\n(1 + null >= observed)\n/ (B + 1)", w=0.25, h=0.18, fc="#ecfdf5")
    for a, b in [((0.23, 0.70), (0.32, 0.70)), ((0.23, 0.32), (0.32, 0.32)),
                 ((0.50, 0.70), (0.68, 0.55)), ((0.50, 0.32), (0.68, 0.49)),
                 ((0.14, 0.62), (0.14, 0.40))]:
        add_arrow(ax, a, b)
    ax.text(0.14, 0.52, "shuffle within era,\nseason, reliability tier", ha="center", fontsize=8)
    ax.text(0.5, 0.92, "Permutation null model for the global endpoint", ha="center",
            fontsize=13, weight="bold")
    save(fig, "null_model_schematic")


def baseline_heatmap():
    days = 365.25 * 32
    counts = np.array([4360 + 450 + 33, 450 + 33, 33], dtype=float)
    windows = np.array([1, 7, 90, 180, 365], dtype=float)
    probs = np.zeros((len(counts), len(windows)))
    for i, count in enumerate(counts):
        probs[i, :] = 1 - np.exp(-(count / days) * windows)

    fig, ax = plt.subplots(figsize=(7.0, 3.7))
    im = ax.imshow(probs, vmin=0, vmax=1, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(windows)))
    ax.set_xticklabels([f"0-{int(w)}d" for w in windows], fontsize=8)
    ax.set_yticks(range(3))
    ax.set_yticklabels(["M6+", "M7+", "M8+"], fontsize=9)
    for i in range(probs.shape[0]):
        for j in range(probs.shape[1]):
            color = "white" if probs[i, j] > 0.65 else "#111827"
            ax.text(j, i, f"{probs[i, j]:.3f}", ha="center", va="center",
                    color=color, fontsize=8, weight="bold" if windows[j] == 180 else "normal")
    ax.set_title("Prospective global no-radius coincidence probability", fontsize=12, weight="bold")
    ax.set_xlabel("Window after oarfish sighting")
    ax.set_ylabel("Magnitude threshold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("P(at least one earthquake)")
    save(fig, "baseline_heatmap")


def bias_dag():
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    nodes = {
        "Oceanography": (0.08, 0.68),
        "Fishing /\nbeach access": (0.08, 0.30),
        "Media /\ncitizen science": (0.36, 0.30),
        "Observed\noarfish report": (0.36, 0.68),
        "Earthquake\noccurrence": (0.70, 0.68),
        "Claimed\nassociation": (0.70, 0.30),
    }
    for text, (x, y) in nodes.items():
        add_box(ax, (x, y), text, w=0.20, h=0.14, fc="#f8fafc")
    arrows = [
        ("Oceanography", "Observed\noarfish report"),
        ("Fishing /\nbeach access", "Observed\noarfish report"),
        ("Media /\ncitizen science", "Observed\noarfish report"),
        ("Media /\ncitizen science", "Claimed\nassociation"),
        ("Observed\noarfish report", "Claimed\nassociation"),
        ("Earthquake\noccurrence", "Claimed\nassociation"),
    ]
    centers = {k: (v[0] + 0.10, v[1] + 0.07) for k, v in nodes.items()}
    for a, b in arrows:
        add_arrow(ax, centers[a], centers[b])
    ax.text(0.5, 0.94, "Reporting-bias pathways", ha="center", fontsize=13, weight="bold")
    save(fig, "bias_dag")


def baseline_coincidence():
    days = 365.25 * 32
    counts = {"M6+": 4360 + 450 + 33, "M7+": 450 + 33, "M8+": 33}
    windows = np.array([1, 7, 90, 180, 365], dtype=float)
    fig, ax = plt.subplots(figsize=(7.0, 3.7))
    for label, count in counts.items():
        probs = 1 - np.exp(-(count / days) * windows)
        ax.plot(windows, probs, marker="o", label=label, linewidth=2)
    ax.axvline(180, color=GRAY, linestyle="--", linewidth=1.2)
    ax.text(183, 0.05, "primary\n0-180d", fontsize=8, color=GRAY)
    ax.set_xscale("log")
    ax.set_xticks(windows)
    ax.set_xticklabels([str(int(w)) for w in windows])
    ax.set_ylim(0, 1.04)
    ax.set_xlabel("Prospective window after sighting (days, log scale)")
    ax.set_ylabel("P(at least one global earthquake)")
    ax.set_title("Global base-rate saturation by analysis window", fontsize=12, weight="bold")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "baseline_coincidence")


if __name__ == "__main__":
    global_linkage_schematic()
    pipeline_diagram()
    null_model_schematic()
    baseline_heatmap()
    baseline_coincidence()
    bias_dag()
