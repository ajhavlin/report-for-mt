#!/usr/bin/env python3
"""Generate report-native vector PDFs for the binding/hiding performance plots.

The input is the ark-mt benchmark matrix produced by:

    crates/ark-mt/benches/plots/plot_benchmark_matrix.py

Only the Poseidon2 rows are used here because the report's concrete certificate
is about small-field Poseidon2 Merkle commitments.  The generated PDFs are
simple three-panel line plots: prover time, verifier time, and proof size.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIGURES = Path(__file__).resolve().parent
MATRIX = ROOT / "ark-vc/crates/ark-mt/benches/plots/benchmark_matrix.csv"

PAGE_W = 720.0
PAGE_H = 300.0
PLOT_TOP = 92.0
PLOT_H = 145.0
PANEL_W = 188.0
PANEL_GAP = 35.0
LEFT = 48.0
BOTTOM = 44.0

INK = (0.141, 0.176, 0.216)
MUTED = (0.376, 0.424, 0.486)
GRID = (0.851, 0.867, 0.890)
RED = (0.722, 0.251, 0.251)

SERIES = {
    "BabyBear": ((0.231, 0.455, 0.725), "square"),
    "BN254": ((0.435, 0.247, 0.710), "triangle"),
    "Goldilocks": ((0.353, 0.596, 0.471), "diamond"),
}
SERIES_ORDER = ["BabyBear", "BN254", "Goldilocks"]

METRICS = [
    ("prover_ms", "Prover time (ms)"),
    ("verifier_ms", "Verifier time (ms)"),
    ("proof_kb", "Proof size (kB)"),
]


def esc(text: object) -> str:
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def rgb(color: tuple[float, float, float], stroke: bool = False) -> str:
    op = "RG" if stroke else "rg"
    return f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} {op}"


class Canvas:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple[float, float, float] = INK,
        width: float = 0.8,
        dash: str | None = None,
    ) -> None:
        dash_cmd = f"[{dash}] 0 d" if dash else "[] 0 d"
        self.parts.append(
            f"q {rgb(color, True)} {width:.2f} w {dash_cmd} "
            f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S Q"
        )

    def polyline(
        self, points: list[tuple[float, float]], color: tuple[float, float, float]
    ) -> None:
        if len(points) < 2:
            return
        body = [f"{points[0][0]:.2f} {points[0][1]:.2f} m"]
        body.extend(f"{x:.2f} {y:.2f} l" for x, y in points[1:])
        self.parts.append(f"q {rgb(color, True)} 1.4 w [] 0 d {' '.join(body)} S Q")

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: tuple[float, float, float],
    ) -> None:
        self.parts.append(
            f"q {rgb(color)} {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f Q"
        )

    def marker(
        self,
        x: float,
        y: float,
        color: tuple[float, float, float],
        shape: str,
        size: float = 3.5,
    ) -> None:
        if shape == "triangle":
            pts = [
                (x, y + size),
                (x - size, y - size),
                (x + size, y - size),
            ]
        elif shape == "diamond":
            pts = [
                (x, y + size),
                (x - size, y),
                (x, y - size),
                (x + size, y),
            ]
        else:
            self.rect(x - size, y - size, 2 * size, 2 * size, color)
            return
        path = [f"{pts[0][0]:.2f} {pts[0][1]:.2f} m"]
        path.extend(f"{px:.2f} {py:.2f} l" for px, py in pts[1:])
        self.parts.append(f"q {rgb(color)} {' '.join(path)} h f Q")

    def text(
        self,
        x: float,
        y: float,
        value: object,
        size: int = 8,
        color: tuple[float, float, float] = INK,
        font: str = "F1",
        anchor: str = "left",
    ) -> None:
        text_value = esc(value)
        # Approximate centering/right alignment with Helvetica metrics.
        dx = 0.0
        if anchor != "left":
            width = 0.52 * size * len(str(value))
            dx = -width / 2 if anchor == "center" else -width
        self.parts.append(
            f"q {rgb(color)} BT /{font} {size} Tf "
            f"{x + dx:.2f} {y:.2f} Td ({text_value}) Tj ET Q"
        )

    def stream(self) -> bytes:
        return "\n".join(self.parts).encode("ascii")


def nice_max(value: float) -> float:
    value *= 1.08
    if value <= 2:
        step = 0.5
    elif value <= 12:
        step = 2
    elif value <= 30:
        step = 5
    elif value <= 90:
        step = 10
    elif value <= 320:
        step = 50
    else:
        step = 100
    return step * math.ceil(value / step)


def tick_values(max_value: float) -> list[float]:
    return [max_value * i / 4 for i in range(5)]


def fmt_tick(value: float) -> str:
    if value >= 100:
        return f"{value:.0f}"
    if value >= 10:
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return f"{value:.2f}".rstrip("0").rstrip(".")


def read_rows(notion: str) -> list[dict[str, str]]:
    with MATRIX.open(newline="") as fh:
        rows = [
            row
            for row in csv.DictReader(fh)
            if row["notion"] == notion and row["hasher"] == "Poseidon"
        ]
    if not rows:
        raise SystemExit(f"No Poseidon rows found for {notion} in {MATRIX}")
    return rows


def x_ticks(notion: str, xmin: int, xmax: int) -> list[int]:
    if notion == "hiding":
        ticks = [0, 5, 10, 15, xmax]
    else:
        ticks = [1, 5, 9, 13, xmax]
    out: list[int] = []
    for tick in ticks:
        if xmin <= tick <= xmax and tick not in out:
            out.append(tick)
    return out


def draw_panel(
    c: Canvas,
    rows: list[dict[str, str]],
    notion: str,
    metric: str,
    title: str,
    panel_index: int,
) -> None:
    x0 = LEFT + panel_index * (PANEL_W + PANEL_GAP)
    y0 = BOTTOM
    points_by_series = {
        series: sorted(
            [r for r in rows if r["series"] == series],
            key=lambda r: int(r["x_value"]),
        )
        for series in SERIES_ORDER
    }
    xmin = min(int(r["x_value"]) for r in rows)
    xmax = max(int(r["x_value"]) for r in rows)
    ymax = nice_max(max(float(r[metric]) for r in rows))

    c.text(x0, y0 + PLOT_H + 24, title, 9, INK, "F2")
    c.line(x0, y0, x0, y0 + PLOT_H, MUTED, 0.6)
    c.line(x0, y0, x0 + PANEL_W, y0, MUTED, 0.6)
    for tick in tick_values(ymax):
        yy = y0 + (tick / ymax) * PLOT_H
        c.line(x0, yy, x0 + PANEL_W, yy, GRID, 0.45, "1.5 3")
        c.text(x0 - 6, yy - 2.5, fmt_tick(tick), 6, MUTED, anchor="right")

    for tick in x_ticks(notion, xmin, xmax):
        xx = x0 + ((tick - xmin) / max(1, xmax - xmin)) * PANEL_W
        c.line(xx, y0, xx, y0 - 3, MUTED, 0.5)
        c.text(xx, y0 - 12, tick, 6, MUTED, anchor="center")

    x_label = "Salt elements k" if notion == "hiding" else "Digest elements D"
    c.text(x0 + PANEL_W / 2, y0 - 28, x_label, 7, INK, "F2", anchor="center")

    # Highlight the BabyBear 128-bit threshold used in the report.
    threshold = 5 if notion == "hiding" else 9
    if xmin <= threshold <= xmax:
        xx = x0 + ((threshold - xmin) / max(1, xmax - xmin)) * PANEL_W
        c.line(xx, y0, xx, y0 + PLOT_H, RED, 0.8, "3 3")
        if panel_index == 0:
            c.text(xx + 3, y0 + PLOT_H - 8, "BabyBear 128-bit", 6, RED, "F2")

    for series in SERIES_ORDER:
        color, shape = SERIES[series]
        pts: list[tuple[float, float]] = []
        for row in points_by_series[series]:
            xval = int(row["x_value"])
            yval = float(row[metric])
            xx = x0 + ((xval - xmin) / max(1, xmax - xmin)) * PANEL_W
            yy = y0 + (yval / ymax) * PLOT_H
            pts.append((xx, yy))
        c.polyline(pts, color)
        for xx, yy in pts:
            c.marker(xx, yy, color, shape)


def draw_plot(notion: str) -> Canvas:
    rows = read_rows(notion)
    c = Canvas()
    title = f"{notion.capitalize()} - Poseidon2 performance"
    c.text(28, PAGE_H - 30, title, 15, INK, "F2")
    c.text(
        28,
        PAGE_H - 48,
        "Criterion means; n=4,096 leaves, 32 openings, binary tree. Prover = commit + open.",
        7,
        MUTED,
    )
    lx = 28
    for series in SERIES_ORDER:
        color, shape = SERIES[series]
        c.marker(lx, PAGE_H - 66, color, shape, 3.2)
        c.text(lx + 8, PAGE_H - 68.5, series, 7, INK, "F2")
        lx += 82 if series != "Goldilocks" else 98
    c.line(lx + 2, PAGE_H - 66, lx + 15, PAGE_H - 66, RED, 0.8, "3 3")
    c.text(lx + 20, PAGE_H - 68.5, "BabyBear 128-bit threshold", 7, MUTED)

    for idx, (metric, label) in enumerate(METRICS):
        draw_panel(c, rows, notion, metric, label, idx)
    return c


def write_pdf(path: Path, canvas: Canvas) -> None:
    content = canvas.stream()
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W:.0f} {PAGE_H:.0f}] "
            f"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> "
            f"/Contents 6 0 R >>"
        ).encode("ascii")
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects.append(b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{idx} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    out.extend(
        (
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode("ascii")
    )
    path.write_bytes(bytes(out))


def main() -> None:
    for notion in ("hiding", "binding"):
        out = FIGURES / f"{notion}-poseidon-performance.pdf"
        write_pdf(out, draw_plot(notion))
        print(out)


if __name__ == "__main__":
    main()
