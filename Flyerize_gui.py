# SPDX-License-Identifier: GPL-3.0-or-later
"""flyerize_gui: straighten a banner in a photo, one file at a time.

Usage: flyerize_gui.py [image file]
Search an image (of a banner on a fence or flyer hanging on a
corkboard) and try to adjust for curves and bends along the edges,
cropping result to a rectangle.  Corners and sides are adjustable,
full directory mode enabled (processing only one image at a time.)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import datetime
import json
import os
import re
import sys
import tempfile
import time
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, simpledialog, ttk

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageTk

try:
    import pi_heif
    pi_heif.register_heif_opener()
    HEIF_OK = True
except Exception:       # the package is optional: without it, HEIC photos are not offered
    HEIF_OK = False

try:
    import winreg
except ImportError:      # not Windows
    winreg = None

SUFFIX = "~"
SIDES = ("top", "right", "bottom", "left")
SIDE_ENDS = {"top": (0, 1), "right": (1, 2), "bottom": (3, 2), "left": (0, 3)}   # corner indices, A then B
CORNER_NAMES = ("TL", "TR", "BR", "BL")
BEND_T_MIN, BEND_T_MAX = 0.25, 0.75     # keeps the curve moving one way along the side
WORK_SIZE = 1000
VERSION = "v0.1.14"
DISCUSSIONS_URL = "https://github.com/somewiktadmin/Flyerize_gui/discussions"
DONATE_URL = "https://www.paypal.com/qrcodes/managed/33ecc1cb-c786-4fba-ad4a-17242f92e108?utm_source=consapp_onscreen"
# The picture below is a QR code for DONATE_URL. If the address above ever changes, make a new picture for it.
QR_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAVcAAAFXCAIAAACZU5pPAAAHLElEQVR42u3dQY7bMBBFwSjQ/a882XkRTAZE2t2f"
    "tKrWE1umnQcJBMnr6+vrF/Bgvw0BqACgAoAKACoAqACgAoAKACoAqACgAoAKACoAqACgAoAKACoAqACgAoAKACoA"
    "qACgAoAKACoAqACgAsAHuTte9Lqu3T5n8TjG4ifKHgaZ/Tq+/ezfXtL6KI19HZ/3S3YvAKgAoAKACgAqAKgA8HKP"
    "vdPYbNnY7E7H7OPYa3a8e3HoipdUnP/reKNTfsnuBcATAaACgAoAKgCoAPBMd/bts2v1iu/ecfHrr9kxX5V99/VL"
    "Kr57duiy4+leAFABQAUAFQBUAFAB4OU2BH/JTuAV3z372YsrGtdlF0S6FwBUAFABQAUAFQBUAPgMZgr/VpwU7DiB"
    "7+htTtc9+SxJ9wKACgAqAKgAoAKACgDzwjOFnzc9U5wUXP/L4rl62bP6OhYadoz8Q37J7gXAEwGgAoAKACoAqADw"
    "THMzhWNbaBaN7cDZ8e5Zxd1Hx/7yIb9k9wKACgAqAKgAoAKACgA/u5686eIps1CnbMu54XjiXgBQAUAFABUAVABQ"
    "AeBfrux019jyrA1PCixe/NiBiNlvc8PPnv19uhcAVABQAUAFABUAVAB4l7k1hdllZOtTPsUZo7GZrY6L33BAxoau"
    "Q/Y4RvcCgAoAKgCoAKACgAoAP7s23EJzw0Vs69fZ8Zqn7P/5edOHHbOk7gUAFQBUAFABQAUAFQA2cR29qm/DWb3i"
    "a66/0dG7ZWaHrviry/5orSkEPBEAKgCoAKACgAoA77LjTOG6U87Vy45S8TqzG3iO/Rg2/M2PXad7AfBEAKgAoAKA"
    "CgAqADzT2buPjl3S+msWZae7spuXjg1y1oY7mroXAE8EgAoAKgCoAKACwDPdHS96ynRX8TXHPvuGx92dcnTiht/m"
    "hl+xewHwRACoAKACgAoAKgA8073hNXVMumR3oRxbRtaxAu+ULTTXL35sPDecJXUvAKgAoAKACgAqAKgA8HJtuF7t"
    "6IPxsqOU3dlywy9uw7WP2UlB9wKACgAqAKgAoAKACgAvjz6ncN0pe2Bmja2WG5slzR5FOfZTdC8AnggAFQBUAFAB"
    "QAWAZ3JO4cRrdmxiuT7y2VEa+0Qd/7zj521NIeCJAFABQAUAFQBUANjEteFqueIbbbgp6LoNlw+OrdXLLjQcmyXd"
    "cJ9S9wLgiQBQAUAFABUAVAB4pnvsnbIr8LKruzrm/zrGc+xYvo7vff2Sxr7i4u/TvQCgAoAKACoAqACgAkCruZnC"
    "9QmSsfmq7ATe+nV2/POOLTTHRmlsPLP/O9wLACoAqACgAoAKACoAtLo3vKax4+6ypw8WrzP72bOb1q5f0ikHN1pT"
    "CHgiAFQAUAFABQAVAOZdp6zuyl5n9vjA7EajHRc/tkNs9sjMjm/TOYWAJwJABQAVAFQAUAHgXa4NZ+CKr7kuO1u2"
    "4XgW3yj7dWSPoiz+Pq0pBDwRACoAqACgAoAKAPPuo68+u1Po+iWN7auZPadw7OvI7n3aMfLrl2RNIeCJAFABQAUA"
    "FQBUAHiXlpnCjgmnsam+b3VMz2S30DzlnMLiGx29o+nYQkP3AuCJAFABQAUAFQBUAHima8PlWR2vmZ1sy56Wd8qA"
    "OKfwvZ/dvQCgAoAKACoAqACgAsDPdtx99JSj6U45FDA7IB2LQTsWRI69ZvboRPcCgAoAKgCoAKACgAoAL+E1hd8a"
    "W1s2dtRfxz8fk52OHdufdmx3XGsKAU8EgAoAKgCoAKACwCbm1hSesuBs/eKLf9kxs1UcpQ2/zbFfXccazQ3XfboX"
    "AFQAUAFABQAVAFQAeDl799GxScGxFY3FAcl+R2OHLK5/cR3GVjS6FwBUAFABQAUAFQBUAGh1H331YxtjFt9obEVj"
    "x3gWPWSWtGNA7D4KeCIAVABQAUAFABUAWl3ZxUzhDx/dgXPD4+6y03LZIzOzCyLHrtO9AKACgAoAKgCoAKACwEvL"
    "msJTzqvbcElix8h3zC11zIHZZNW9AKACgAoAKgCoAKACwKS53UfH5kI6jjnsWPKVncAbG/nidOzYXF3HeGaPt3Qv"
    "AKgAoAKACgAqAKgA8LPwOYUd+3+OXdLYNNLYjOb6a3asFDxl+rD4+8xuNOpeAFABQAUAFQBUAFAB4OU2BClji+3W"
    "p/qye7SODV125Du+I/cCgAoAKgCoAKACgAoA/8FM4ZLs4sWOi+9Y6tcxINnNS8cOWXROIeCJAFABQAUAFQBUAJgX"
    "ninMTpB0zBgVP9GGBw1mB6Q41Te2/2dxpjC7RtO9AHgiAFQAUAFABQAVAJ5pbqZwbAld8ZI2XD6YncDr2EJzXXGq"
    "r/jZx75NawoBTwSACgAqAKgAoALAvCs7RQG4FwBUAFABQAUAFQBUAFABQAUAFQBUAFABQAUAFQBUAFABQAUAFQBU"
    "AFABQAUAFQBUAFABQAUAFQBUAFAB4I3+AMDouJ+yaIfjAAAAAElFTkSuQmCC"
)
# The coffee nag shows once for each number below. After the list it repeats every COFFEE_EVERY operations.
# Shipped schedule: 50, 500, 1000, then every 1000. The testing schedule was 5, 10, 15, 20, 25, 50, 75, 100, then every 25.
COFFEE_FIXED = (50, 500, 1000)
COFFEE_EVERY = 1000
# How to fill the part of a straightened picture that lies outside the original photo (a corner pulled past the edge).
FILL_CHOICES = (
    ("reflect", "Mirror the edge: a mirrored strip of the photo fills the empty corner"),
    ("replicate", "Repeat the edge: the outermost pixels are stretched into the empty corner"),
    ("black", "Black: leave the empty corner black"),
)
FILL_BORDERS = {"reflect": cv2.BORDER_REFLECT_101, "replicate": cv2.BORDER_REPLICATE, "black": cv2.BORDER_CONSTANT}
LOG_MAX_BYTES = 1024 * 1024      # at this size the log is renamed to Flyerize_gui.log.old and a new one starts
REG_PATH = r"Software\Flyerize_gui"
HELP_TEXT = (
    "Flyerize_gui straightens photos of flyers, banners and sheets of paper.  It makes a first guess at where the four "
    "edges are, and you adjust from there.  The result is a flat, upright rectangle saved as a new picture next to your photo.",
    "Drag the red corner dots until they sit on the corners of the flyer, and drag the purple dot on a side if the paper "
    "curves.  With the whole photo in view you can also drag across empty space to draw a rectangle, a Z or a slash, and "
    "Flyerize_gui will propose the corners for you.  Press PREVIEW to look at the result, then Save New.",
    "You can also hand it a whole folder, for example from the Send To menu, and it lines up every image in it.  Skip to "
    "Next moves ahead, Back steps back, and Move \u00b1nnn jumps a number of photos at once, backward if the number is "
    "negative.  Turn on Auto and each save carries you straight on to the next photo.",
    "Questions, bug reports and ideas are welcome at " + DISCUSSIONS_URL + ".  The README on the project page has a quick "
    "start and a cheat sheet of every key.  Press F1 at any time to see this panel again.",
)
IMAGE_TYPES = [("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff *.webp"), ("All files", "*.*")]

LINE_COLOR = "#ffd400"
BEND_COLOR = "#9b30ff"
CORNER_COLOR = "#ff0000"
GRID_COLOR = "#00e676"
AUTO_FILL = "#c8f7c5"
GRID_MODES = (("Off", (), 0), ("Crosshairs", (0.5,), 1), ("Thirds", (1 / 3, 2 / 3), 2),
              ("Fifths", (0.2, 0.4, 0.6, 0.8), 4), ("Tenths", tuple(i / 10 for i in range(1, 10)), 9))
MAG_ZOOM_DEFAULT = 6.0   # starting zoom of the corner magnifier (1.0 is one photo pixel per screen pixel)
ZOOM_MIN = 0.25          # how far out the magnifier and the expanded corner view may zoom
ZOOM_MAX = 48.0
BW_LIGHT_ABOVE, BW_DARK_BELOW = 160, 96          # BW/WB: tuned values
BW_LIGHT_TO, BW_DARK_TO = 96 + 7, 160 - 7
GHOST_PROMPT = " Either zorro or rectangle pattern was detected. \n Assigning all new corner x,y values."
LINE_HIT = 8             # how close (screen pixels) a click must be to a side line to grab it
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}
if HEIF_OK:
    IMAGE_EXTS |= {".heic", ".heif"}
    IMAGE_TYPES[0] = ("Images", IMAGE_TYPES[0][1] + " *.heic *.heif")


# ===== corner detection (first version) =====

def order_corners(p):
    c = p.mean(axis=0)
    ang = np.arctan2(p[:, 1] - c[1], p[:, 0] - c[0])
    p = p[np.argsort(ang)]
    start = int(np.argmin(p[:, 0] + p[:, 1]))
    return np.roll(p, -start, axis=0)   # TL, TR, BR, BL


def quad_from_contour(cnt):
    per = cv2.arcLength(cnt, True)
    for eps in np.arange(0.01, 0.09, 0.005):
        ap = cv2.approxPolyDP(cnt, eps * per, True)
        if len(ap) == 4:
            return ap.reshape(4, 2).astype(np.float32)
    return None


def angles_ok(q):
    for i in range(4):
        a, b, c = q[i - 1], q[i], q[(i + 1) % 4]
        v1, v2 = a - b, c - b
        cosang = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
        if not (-0.6 < cosang < 0.6):
            return False
    return True


def candidate_masks(small):
    h, w = small.shape[:2]
    m_ = max(h, w)
    hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV)
    gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_RGB2GRAY), (5, 5), 0)

    def ell(f):
        k = max(3, int(m_ * f)) | 1
        return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))

    out = []
    sat = ((hsv[..., 1] > 80) & (hsv[..., 2] > 20)).astype(np.uint8) * 255
    sat = cv2.morphologyEx(sat, cv2.MORPH_CLOSE, ell(0.005))
    sat = cv2.morphologyEx(sat, cv2.MORPH_OPEN, ell(0.012))
    out.append(sat)
    _, ot = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    for m in (ot, 255 - ot):
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, ell(0.012), iterations=2)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, ell(0.012))
        out.append(m)
    return out


def evaluate(cnt, sh, sw):
    area = cv2.contourArea(cnt)
    frac = area / (sh * sw)
    if frac < 0.04 or frac > 0.97:
        return None
    q = quad_from_contour(cnt)
    if q is None or not cv2.isContourConvex(q.astype(np.float32).reshape(-1, 1, 2)):
        return None
    q = order_corners(q)
    if not angles_ok(q):
        return None
    qa = cv2.contourArea(q)
    fill = min(area, qa) / max(area, qa)
    margin = 0.01 * max(sh, sw)
    touching = np.sum((q[:, 0] < margin) | (q[:, 0] > sw - margin) | (q[:, 1] < margin) | (q[:, 1] > sh - margin))
    area_term = min(1.0, 0.5 + frac / 0.2)
    return fill * area_term * (1.0 - 0.15 * touching), q


def detect_corners(img):
    """Best four-sided shape as TL, TR, BR, BL in full-size pixels, or None."""
    H, W = img.shape[:2]
    sc = min(1.0, WORK_SIZE / max(H, W))
    small = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA) if sc < 1 else img
    sh, sw = small.shape[:2]
    best = None
    for m in candidate_masks(small):
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in cs:
            ev = evaluate(cnt, sh, sw)
            if ev is not None and (best is None or ev[0] > best[0]):
                best = ev
    return None if best is None else best[1] / sc


def initial_corners(img):
    """Detected corners, with any corner past the halfway line reset to the image corner."""
    H, W = img.shape[:2]
    image_corners = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], dtype=np.float64)
    q = detect_corners(img)
    if q is None:
        return image_corners
    q = q.astype(np.float64)
    bad = [q[0, 0] > W / 2 or q[0, 1] > H / 2,      # TL
           q[1, 0] < W / 2 or q[1, 1] > H / 2,      # TR
           q[2, 0] < W / 2 or q[2, 1] < H / 2,      # BR
           q[3, 0] > W / 2 or q[3, 1] < H / 2]      # BL
    for i in range(4):
        if bad[i]:
            q[i] = image_corners[i]
    return fix_dangling(q, W, H)


def inset_corners(W, H, fraction=0.05):
    """The neutral starting rectangle, a little in from the picture edges."""
    ix, iy = round(W * fraction), round(H * fraction)
    return np.array([[ix, iy], [W - 1 - ix, iy], [W - 1 - ix, H - 1 - iy], [ix, H - 1 - iy]], dtype=np.float64)


def fix_dangling(q, W, H):
    """A corner sitting on a picture corner is only believable when both of its sides run along the picture edges.
    Otherwise estimate it from the other three (completing the parallelogram). If two or more corners fail, the
    guesses are not trustworthy, so fall back to the neutral inset rectangle. This is for corners the program
    proposes, never for corners the user placed."""
    q = np.array(q, dtype=np.float64)
    border = [(0, 0), (W - 1, 0), (W - 1, H - 1), (0, H - 1)]
    # for each corner: the neighbor on its horizontal side and the y that neighbor must have,
    # then the neighbor on its vertical side and the x that neighbor must have
    need = [((1, 0), (3, 0)), ((0, 0), (2, W - 1)), ((3, H - 1), (1, W - 1)), ((2, H - 1), (0, 0))]
    bad = []
    for i in range(4):
        if (q[i, 0], q[i, 1]) != border[i]:
            continue
        (hn, hy), (vn, vx) = need[i]
        if not (q[hn, 1] == hy and q[vn, 0] == vx):
            bad.append(i)
    if not bad:
        return q
    if len(bad) > 1:
        return inset_corners(W, H)
    i = bad[0]
    est = q[(i + 1) % 4] + q[(i + 3) % 4] - q[(i + 2) % 4]
    q[i] = [min(max(round(est[0]), 0), W - 1), min(max(round(est[1]), 0), H - 1)]
    return q


# ===== side curves =====

def side_frame(corners, side):
    i, j = SIDE_ENDS[side]
    A, B = corners[i], corners[j]
    e = B - A
    L = np.linalg.norm(e)
    nrm = np.array([-e[1], e[0]]) / L if L > 1e-9 else np.array([0.0, 1.0])
    return A, e, nrm


def side_points(corners, side, bend, n=60):
    """Points along a side: a quadratic Bezier curve from one corner to the other that passes through the bend dot
    at its middle. Sliding the dot along the side leans the bulge toward it."""
    A, e, nrm = side_frame(corners, side)
    t, d = bend
    s = np.linspace(0, 1, n)
    along = 2 * s * (1 - s) * (2 * t - 0.5) + s * s      # equals s when the dot is centered
    across = 4 * d * s * (1 - s)
    return A[None, :] + along[:, None] * e[None, :] + across[:, None] * nrm[None, :]


def bend_dot(corners, side, bend):
    A, e, nrm = side_frame(corners, side)
    t, d = bend
    return A + t * e + d * nrm


def bend_from_point(corners, side, p):
    A, e, nrm = side_frame(corners, side)
    ee = float(e @ e)
    t = float((p - A) @ e) / ee if ee > 1e-9 else 0.5
    return min(BEND_T_MAX, max(BEND_T_MIN, t)), float((p - A) @ nrm)


# ===== the warp (Coons-style blend) =====

def output_size(corners):
    TL, TR, BR, BL = corners
    w = int(round((np.linalg.norm(TR - TL) + np.linalg.norm(BR - BL)) / 2))
    h = int(round((np.linalg.norm(BL - TL) + np.linalg.norm(BR - TR)) / 2))
    return max(2, w), max(2, h)


def canvas_info(img_shape, corners, crop):
    """Output canvas: (w, h, ox, oy, cw, ch, Hm). The box is [0,w-1] x [0,h-1] in the rectified frame."""
    H_, W_ = img_shape[:2]
    w, h = output_size(corners)
    dst = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    Hm = cv2.getPerspectiveTransform(np.asarray(corners, dtype=np.float32), dst)
    if crop:
        return w, h, 0, 0, w, h, Hm
    img_c = np.float32([[0, 0], [W_ - 1, 0], [W_ - 1, H_ - 1], [0, H_ - 1]]).reshape(-1, 1, 2)
    pts = np.vstack([cv2.perspectiveTransform(img_c, Hm).reshape(-1, 2), dst])
    ox, oy = int(np.floor(pts[:, 0].min())), int(np.floor(pts[:, 1].min()))
    cw = int(np.ceil(pts[:, 0].max())) - ox + 1
    ch = int(np.ceil(pts[:, 1].max())) - oy + 1
    return w, h, ox, oy, cw, ch, Hm


def build_maps(img_shape, corners, bends, crop):
    """For every output pixel, where to read in the source photo. Each output pixel is blended from the
    four side curves: a column's vertical position comes from the top and bottom curves, and a row's
    horizontal position from the left and right curves, all in the perspective-corrected frame.
    Outside the box the blend simply continues, so the whole photo can be transformed."""
    w, h, ox, oy, cw, ch, Hm = canvas_info(img_shape, corners, crop)
    Hinv = np.linalg.inv(Hm)
    curves = {}
    for side in SIDES:
        pts = side_points(corners, side, bends[side], 400).astype(np.float32)
        curves[side] = cv2.perspectiveTransform(pts.reshape(-1, 1, 2), Hm).reshape(-1, 2)

    def by_x(c):
        o = np.argsort(c[:, 0])
        return c[o, 0], c[o, 1]

    def by_y(c):
        o = np.argsort(c[:, 1])
        return c[o, 1], c[o, 0]

    tx, ty = by_x(curves["top"])
    bx, by = by_x(curves["bottom"])
    ly, lx = by_y(curves["left"])
    ry, rx = by_y(curves["right"])
    px = (np.arange(cw) + ox).astype(np.float32)
    py = (np.arange(ch) + oy).astype(np.float32)
    u = px / (w - 1)
    v = py / (h - 1)
    yT = np.interp(px, tx, ty).astype(np.float32)
    yB = np.interp(px, bx, by).astype(np.float32)
    xL = np.interp(py, ly, lx).astype(np.float32)
    xR = np.interp(py, ry, rx).astype(np.float32)
    Xr = xL[:, None] + u[None, :] * (xR - xL)[:, None]
    Yr = yT[None, :] + v[:, None] * (yB - yT)[None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        den = Hinv[2, 0] * Xr + Hinv[2, 1] * Yr + Hinv[2, 2]
        mx = (Hinv[0, 0] * Xr + Hinv[0, 1] * Yr + Hinv[0, 2]) / den
        my = (Hinv[1, 0] * Xr + Hinv[1, 1] * Yr + Hinv[1, 2]) / den
    mx = np.nan_to_num(mx, nan=-1e6, posinf=-1e6, neginf=-1e6).astype(np.float32)
    my = np.nan_to_num(my, nan=-1e6, posinf=-1e6, neginf=-1e6).astype(np.float32)
    return mx, my


def grid_lines(corners, bends, fractions, n=48):
    """Lines of constant output column and row, carried back into the photo through the same blend as build_maps, so they
    bend where the result bends. fractions are positions across the result (0 to 1, the edges themselves are left out).
    Returns (vertical, horizontal): lists of n x 2 arrays of photo points."""
    w, h, ox, oy, cw, ch, Hm = canvas_info((1, 1), corners, True)
    Hinv = np.linalg.inv(Hm)
    curves = {}
    for side in SIDES:
        pts = side_points(corners, side, bends[side], 400).astype(np.float32)
        curves[side] = cv2.perspectiveTransform(pts.reshape(-1, 1, 2), Hm).reshape(-1, 2)

    def by_x(c):
        o = np.argsort(c[:, 0])
        return c[o, 0], c[o, 1]

    def by_y(c):
        o = np.argsort(c[:, 1])
        return c[o, 1], c[o, 0]

    tx, ty = by_x(curves["top"])
    bx, by = by_x(curves["bottom"])
    ly, lx = by_y(curves["left"])
    ry, rx = by_y(curves["right"])

    def to_photo(Xr, Yr):
        with np.errstate(divide="ignore", invalid="ignore"):
            den = Hinv[2, 0] * Xr + Hinv[2, 1] * Yr + Hinv[2, 2]
            return np.stack([(Hinv[0, 0] * Xr + Hinv[0, 1] * Yr + Hinv[0, 2]) / den,
                             (Hinv[1, 0] * Xr + Hinv[1, 1] * Yr + Hinv[1, 2]) / den], axis=1)

    s = np.linspace(0.0, 1.0, n)
    vertical, horizontal = [], []
    for f in fractions:
        px = f * (w - 1)                               # a vertical line: one column, running down through the rows
        py = s * (h - 1)
        xL, xR = np.interp(py, ly, lx), np.interp(py, ry, rx)
        yT0, yB0 = np.interp(px, tx, ty), np.interp(px, bx, by)
        vertical.append(to_photo(xL + f * (xR - xL), yT0 + s * (yB0 - yT0)))
        py0 = f * (h - 1)                              # a horizontal line: one row, running across the columns
        px = s * (w - 1)
        xL0, xR0 = np.interp(py0, ly, lx), np.interp(py0, ry, rx)
        yT, yB = np.interp(px, tx, ty), np.interp(px, bx, by)
        horizontal.append(to_photo(xL0 + s * (xR0 - xL0), yT + f * (yB - yT)))
    return vertical, horizontal


def render(img, corners, bends, crop, interp=cv2.INTER_CUBIC, fill="reflect"):
    mx, my = build_maps(img.shape, corners, bends, crop)
    return cv2.remap(img, mx, my, interp, borderMode=FILL_BORDERS.get(fill, cv2.BORDER_REFLECT_101), borderValue=(0, 0, 0))


def render_preview(img, corners, bends, crop, max_px=1400, max_canvas=20e6, fill="reflect"):
    """A smaller, quicker version of render() for looking at the result."""
    H, W = img.shape[:2]
    s = min(1.0, max_px / max(H, W))
    while True:
        small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1 else img
        c2 = np.asarray(corners, dtype=np.float64) * s
        b2 = {k: (t, d * s) for k, (t, d) in bends.items()}
        _, _, _, _, cw, ch, _ = canvas_info(small.shape, c2, crop)
        if cw * ch <= max_canvas or s < 0.02:
            return render(small, c2, b2, crop, cv2.INTER_LINEAR, fill)
        s *= 0.6


# ===== files =====

def is_heic(path):
    return os.path.splitext(path)[1].lower() in (".heic", ".heif")


def load_image(path):
    pil = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return np.array(pil), pil


# Deprecated 2026-10-23: nothing calls this. Names now come from the filename box and new_file_candidates.
def output_path(path):
    stem, ext = os.path.splitext(path)
    return stem + SUFFIX + (ext if ext.lower() in (".png", ".bmp") else ".jpg")


def save_output(arr, pil_in, src_path, out_path):
    res = Image.fromarray(arr)
    if out_path.lower().endswith(".jpg"):
        try:
            res.save(out_path, quality=95, exif=pil_in.getexif())
        except Exception:
            res.save(out_path, quality=95)
    else:
        res.save(out_path)
    st = os.stat(src_path)
    os.utime(out_path, (st.st_atime, st.st_mtime))


# ===== output options, file names, the outline picture, and recognizing a drawn stroke =====

def apply_output_options(arr, rot, mirror, bw=False):
    """BW/WB (very light pixels become dark gray and very dark pixels become light gray), then rotate
    counter-clockwise by rot degrees (0, 90, 180 or 270), then optionally mirror left to right."""
    out = arr
    if bw:
        out = arr.copy()
        light = (arr[..., 0] > BW_LIGHT_ABOVE) & (arr[..., 1] > BW_LIGHT_ABOVE) & (arr[..., 2] > BW_LIGHT_ABOVE)
        dark = (arr[..., 0] < BW_DARK_BELOW) & (arr[..., 1] < BW_DARK_BELOW) & (arr[..., 2] < BW_DARK_BELOW)
        out[light] = BW_LIGHT_TO
        out[dark] = BW_DARK_TO
    if rot:
        out = np.rot90(out, (rot // 90) % 4)
    if mirror:
        out = out[:, ::-1]
    return np.ascontiguousarray(out)


# Deprecated 2026-10-23: nothing calls this. The DBG button builds its own name.
def outline_path(path):
    return os.path.splitext(path)[0] + "~dbg.jpg"


# Deprecated 2026-10-23: nothing calls this. Numbering now comes from new_file_candidates.
def numbered_path(base):
    """The first free name of the form name~cr~2.jpg, name~cr~3.jpg and so on."""
    stem, ext = os.path.splitext(base)
    n = 2
    while os.path.exists("%s~%d%s" % (stem, n, ext)):
        n += 1
    return "%s~%d%s" % (stem, n, ext)


def outline_image(img, corners, bends, trace=None, grid_fractions=()):
    """The photo with the chosen outline drawn on it, like the old debug picture. trace is an optional list of
    photo points: the stroke that made the outline. grid_fractions, when given, adds the grid lines as the main view shows them."""
    out = img.copy()
    H, W = out.shape[:2]
    th = max(2, max(H, W) // 500)
    if trace is not None and len(trace) > 1:
        pts = np.round(np.asarray(trace, dtype=float)).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(out, [pts], False, (255, 255, 255), max(1, th // 2), cv2.LINE_AA)
        cv2.circle(out, tuple(int(v) for v in pts[0, 0]), th * 2, (255, 255, 255), -1, cv2.LINE_AA)
    if grid_fractions:
        try:
            vertical, horizontal = grid_lines(corners, bends, grid_fractions, 96)
        except (ValueError, np.linalg.LinAlgError, cv2.error):
            vertical, horizontal = [], []
        for pts in vertical + horizontal:
            if np.all(np.isfinite(pts)):
                gp = np.round(np.clip(pts, -1e6, 1e6)).astype(np.int32).reshape(-1, 1, 2)
                cv2.polylines(out, [gp], False, (0, 0, 0), th + 2, cv2.LINE_AA)
                cv2.polylines(out, [gp], False, (0, 230, 118), max(1, th // 2), cv2.LINE_AA)
    for side in SIDES:
        pts = side_points(corners, side, bends[side], 80)
        cv2.polylines(out, [np.round(pts).astype(np.int32).reshape(-1, 1, 2)], False, (255, 212, 0), th, cv2.LINE_AA)
    for name, p in zip(CORNER_NAMES, corners):
        c = (int(round(p[0])), int(round(p[1])))
        cv2.circle(out, c, th * 3, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(out, c, th * 2, (255, 0, 0), -1, cv2.LINE_AA)
        pos = (c[0] + th * 5, c[1] - th * 5)
        cv2.putText(out, name, pos, cv2.FONT_HERSHEY_SIMPLEX, th * 0.55, (0, 0, 0), th + 2, cv2.LINE_AA)
        cv2.putText(out, name, pos, cv2.FONT_HERSHEY_SIMPLEX, th * 0.55, (255, 255, 255), th, cv2.LINE_AA)
    return out


def rdp(P, eps):
    """Ramer-Douglas-Peucker: keep only the points that matter. P is an (n, 2) array."""
    if len(P) < 3:
        return P
    a, b = P[0], P[-1]
    ab = b - a
    L = float(np.linalg.norm(ab))
    if L < 1e-9:
        d = np.linalg.norm(P - a, axis=1)
    else:
        d = np.abs(ab[0] * (P[:, 1] - a[1]) - ab[1] * (P[:, 0] - a[0])) / L
    i = int(np.argmax(d))
    if d[i] > eps:
        left, right = rdp(P[:i + 1], eps), rdp(P[i:], eps)
        return np.vstack([left[:-1], right])
    return np.vstack([a, b])


def order_quad(v):
    """Four points to TL, TR, BR, BL by where they are."""
    v = np.asarray(v, dtype=float)
    by_y = v[np.argsort(v[:, 1])]
    top = by_y[:2][np.argsort(by_y[:2, 0])]
    bottom = by_y[2:][np.argsort(by_y[2:, 0])]
    return np.array([top[0], top[1], bottom[1], bottom[0]])


def recognize_stroke(points):
    """A drawn rectangle (a closed loop of four sides) or a Z (top, diagonal, bottom) both give four corners.
    Returns TL, TR, BR, BL in the same coordinates as the stroke, or None."""
    P = np.asarray(points, dtype=float)
    if len(P) < 8:
        return None
    diag = float(np.linalg.norm(P.max(axis=0) - P.min(axis=0)))
    if diag < 30:
        return None
    closed = np.linalg.norm(P[0] - P[-1]) < 0.2 * diag
    verts = None
    for frac in (0.04, 0.06, 0.08, 0.10, 0.13, 0.17):
        keep = rdp(P, frac * diag)
        v = keep[:-1] if closed else keep
        while len(v) > 4:
            # an extra vertex lying on a straight run (a loop that started mid side, or a split point on a straight
            # side): drop the straightest one. The two ends of an open stroke are never dropped.
            dev = []
            for i in range(len(v)):
                if not closed and i in (0, len(v) - 1):
                    dev.append(1e18)
                    continue
                a, b, c = v[i - 1], v[i], v[(i + 1) % len(v)]
                ac = c - a
                dev.append(abs(ac[0] * (b[1] - a[1]) - ac[1] * (b[0] - a[0])) / (np.linalg.norm(ac) + 1e-9))
            v = np.delete(v, int(np.argmin(dev)), axis=0)
        if not closed and len(v) == 2:
            lo, hi = v.min(axis=0), v.max(axis=0)      # a straight slash from corner to corner: an upright rectangle
            return np.array([[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]])
        if len(v) == 4:
            verts = v
            break
    if verts is None:
        return None
    q = order_quad(verts)
    if not (cv2.isContourConvex(q.astype(np.float32).reshape(-1, 1, 2)) and angles_ok(q)):
        return None
    return q


# ===== zoomable photo view =====

class ZoomView(tk.Canvas):
    """A canvas that shows a photo with mouse-wheel zoom (about the pointer) and drag-to-pan."""
    MIN_SCALE, MAX_SCALE = 0.02, 16.0

    def __init__(self, parent, img, on_change=None, **kw):
        super().__init__(parent, highlightthickness=0, **kw)
        self.img = img
        self.on_change = on_change
        self.scale, self.off, self.fit_mode = 1.0, np.zeros(2), True
        self.pan_origin = None
        self.cache = (None, None)
        self.bind("<Configure>", self.on_configure)
        self.bind("<MouseWheel>", lambda e: self.zoom_step(1 if e.delta > 0 else -1, e.x, e.y))
        self.bind("<Button-4>", lambda e: self.zoom_step(1, e.x, e.y))
        self.bind("<Button-5>", lambda e: self.zoom_step(-1, e.x, e.y))

    def size(self):
        return max(self.winfo_width(), 50), max(self.winfo_height(), 50)

    def fit(self):
        H, W = self.img.shape[:2]
        cw, ch = self.size()
        s = min((cw - 40) / W, (ch - 40) / H)
        self.scale = s
        self.off = np.array([(cw - W * s) / 2, (ch - H * s) / 2])
        self.fit_mode = True
        self.render()

    def on_configure(self, e):
        if self.fit_mode:
            self.fit()
        else:
            self.render()

    def set_scale(self, s, ax=None, ay=None):
        s = min(max(s, self.MIN_SCALE), self.MAX_SCALE)
        cw, ch = self.size()
        a = np.array([cw / 2 if ax is None else ax, ch / 2 if ay is None else ay], dtype=np.float64)
        p = (a - self.off) / self.scale          # the photo point under the anchor stays put
        self.scale = s
        self.off = a - p * s
        self.fit_mode = False
        self.render()

    def zoom_step(self, direction, ax, ay):
        self.set_scale(self.scale * (1.25 if direction > 0 else 0.8), ax, ay)

    def to_canvas(self, p):
        return self.off[0] + p[0] * self.scale, self.off[1] + p[1] * self.scale

    def to_image(self, ex, ey):
        return np.array([(ex - self.off[0]) / self.scale, (ey - self.off[1]) / self.scale])

    def pan_start(self, e):
        self.pan_origin = (e.x, e.y, self.off.copy())

    def pan_move(self, e):
        if self.pan_origin is None:
            return
        x0, y0, off0 = self.pan_origin
        self.off = off0 + np.array([e.x - x0, e.y - y0])
        self.fit_mode = False
        self.render()

    def pan_end(self):
        self.pan_origin = None

    def render(self):
        cw, ch = self.winfo_width(), self.winfo_height()
        if cw < 20 or ch < 20:
            return
        H, W = self.img.shape[:2]
        s, (ox, oy) = self.scale, self.off
        if s <= 1.0:
            key = round(s, 6)
            if self.cache[0] != key:
                small = cv2.resize(self.img, (max(1, int(round(W * s))), max(1, int(round(H * s)))),
                                   interpolation=cv2.INTER_AREA)
                self.cache = (key, small)
            small = self.cache[1]
            frame = np.full((ch, cw, 3), 32, np.uint8)
            x0, y0 = int(round(ox)), int(round(oy))
            sx, sy, dx, dy = max(0, -x0), max(0, -y0), max(0, x0), max(0, y0)
            w_, h_ = min(small.shape[1] - sx, cw - dx), min(small.shape[0] - sy, ch - dy)
            if w_ > 0 and h_ > 0:
                frame[dy:dy + h_, dx:dx + w_] = small[sy:sy + h_, sx:sx + w_]
        else:
            M = np.float32([[s, 0, ox], [0, s, oy]])
            frame = cv2.warpAffine(self.img, M, (cw, ch), flags=cv2.INTER_NEAREST if s >= 4 else cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=(32, 32, 32))
        self.photo = ImageTk.PhotoImage(Image.fromarray(frame))
        self.delete("photo")
        self.create_image(0, 0, anchor="nw", image=self.photo, tags="photo")
        self.tag_lower("photo")
        if self.on_change:
            self.on_change()


# ===== inner panels (they cover the main view, so nothing opens in a random place) =====

class CornerEditor(tk.Frame):
    """The large corner view (the picture takes 75 percent of the window), opened from the magnifier's Expand button."""

    def __init__(self, app, idx):
        super().__init__(app.root)
        self.app, self.idx = app, idx
        self.zoom = float(app.settings.get("mag_zoom", MAG_ZOOM_DEFAULT))
        self.updating = False
        self.columnconfigure(0, weight=3, uniform="cols")
        self.columnconfigure(1, weight=1, uniform="cols")
        self.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        panel = tk.Frame(self)
        panel.grid(row=0, column=1, sticky="nsew", padx=14, pady=14)
        tk.Label(panel, text="Corner %s" % CORNER_NAMES[idx], font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        tk.Button(panel, text="OK", width=14, height=2, font=("TkDefaultFont", 11, "bold"),
                  command=app.close_panel).pack(fill="x", pady=(10, 4))
        self.xvar, self.yvar, self.zvar = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for label, var, lo, hi, step, cmd in (("X", self.xvar, -100000, 100000, 1, self.on_spin),
                                              ("Y", self.yvar, -100000, 100000, 1, self.on_spin),
                                              ("Zoom %", self.zvar, int(ZOOM_MIN * 100), int(ZOOM_MAX * 100), 25, self.on_zoom_spin)):
            row = tk.Frame(panel)
            row.pack(fill="x", pady=(12, 0))
            tk.Label(row, text=label, width=8, anchor="w").pack(side="left")
            sb = tk.Spinbox(row, from_=lo, to=hi, increment=step, width=8, textvariable=var, format="%.0f", command=cmd)
            sb.pack(side="left")
            sb.bind("<Return>", lambda e, c=cmd: c())
            sb.bind("<FocusOut>", lambda e, c=cmd: c())
        tk.Label(panel, anchor="w", justify="left", wraplength=200, fg="#555555",
                 text="Click the picture to place the corner. Mouse wheel zooms. Esc also closes.").pack(fill="x", pady=(16, 0))
        self.canvas.bind("<Configure>", lambda e: self.render())
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", lambda e: self.zoom_by(1.25 if e.delta > 0 else 0.8))
        self.canvas.bind("<Button-4>", lambda e: self.zoom_by(1.25))
        self.canvas.bind("<Button-5>", lambda e: self.zoom_by(0.8))
        self.set_vars()
        self.place(in_=app.canvas, x=0, y=0, relwidth=1, relheight=1)

    def point(self):
        return self.app.corners[self.idx]

    def set_vars(self):
        self.updating = True
        self.xvar.set("%d" % round(self.point()[0]))
        self.yvar.set("%d" % round(self.point()[1]))
        self.zvar.set("%d" % round(self.zoom * 100))
        self.updating = False

    def on_spin(self):
        if self.updating:
            return
        try:
            x, y = int(round(float(self.xvar.get()))), int(round(float(self.yvar.get())))
        except ValueError:
            return
        self.app.corners[self.idx] = [x, y]
        self.app.after_edit()
        self.render()

    def on_zoom_spin(self):
        if self.updating:
            return
        try:
            z = float(self.zvar.get()) / 100.0
        except ValueError:
            return
        self.zoom = min(ZOOM_MAX, max(ZOOM_MIN, z))
        self.set_vars()
        self.render()

    def on_click(self, e):
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        x, y = self.point()
        self.app.corners[self.idx] = [round(x + (e.x - cw / 2) / self.zoom), round(y + (e.y - ch / 2) / self.zoom)]
        self.set_vars()
        self.app.after_edit()
        self.render()

    def zoom_by(self, f):
        self.zoom = min(ZOOM_MAX, max(ZOOM_MIN, self.zoom * f))
        self.set_vars()
        self.render()

    def render(self):
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cw < 20 or ch < 20:
            return
        self.photo = render_corner_view(self.app.img, self.point(), self.zoom, cw, ch)
        c = self.canvas
        c.delete("all")
        c.create_image(0, 0, anchor="nw", image=self.photo)
        c.create_line(0, ch / 2, cw, ch / 2, fill="#ff4040")
        c.create_line(cw / 2, 0, cw / 2, ch, fill="#ff4040")
        c.create_oval(cw / 2 - 9, ch / 2 - 9, cw / 2 + 9, ch / 2 + 9, fill=CORNER_COLOR, outline="white", width=2)


def render_corner_view(img, point, zoom, cw, ch):
    """The photo around a point, enlarged, as a Tk image with that point at the middle."""
    x, y = point
    M = np.float32([[zoom, 0, cw / 2 - x * zoom], [0, zoom, ch / 2 - y * zoom]])
    if zoom >= 4:
        patch = cv2.warpAffine(img, M, (cw, ch), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    elif zoom >= 1:
        patch = cv2.warpAffine(img, M, (cw, ch), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    else:
        # zooming out: shrink the whole photo first so fine detail averages instead of turning grainy
        small = cv2.resize(img, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_AREA)
        M2 = np.float32([[1, 0, cw / 2 - x * zoom], [0, 1, ch / 2 - y * zoom]])
        patch = cv2.warpAffine(small, M2, (cw, ch), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return ImageTk.PhotoImage(Image.fromarray(patch))


class PreviewPanel(tk.Frame):
    """The corrected result, zoomable, over the main view."""

    def __init__(self, app, out):
        super().__init__(app.root)
        self.app = app
        self.view = ZoomView(self, out, on_change=self.draw_grid, bg="#202020")
        self.view.pack(fill="both", expand=True)
        v = self.view
        v.bind("<ButtonPress-1>", v.pan_start)
        v.bind("<B1-Motion>", v.pan_move)
        v.bind("<ButtonRelease-1>", lambda e: v.pan_end())
        bar = tk.Frame(self)
        bar.pack(fill="x", pady=4)
        tk.Label(bar, text="Preview.  Wheel zooms, drag to pan.  Esc goes back.").pack(side="left", padx=8)
        tk.Button(bar, text="Back", width=8, command=app.close_panel).pack(side="right", padx=8)
        tk.Button(bar, text="Fit", width=6, command=v.fit).pack(side="right")
        self.place(in_=app.canvas, x=0, y=0, relwidth=1, relheight=1)

    def update_image(self, out):
        self.view.img, self.view.cache = out, (None, None)
        self.view.fit()

    def draw_grid(self):
        """Straight lines over the corrected picture, at the same fractions the main view draws curved through the photo.
        Only when the result is cropped to the lines, because then the picture is exactly the box the fractions refer to."""
        v = self.view
        v.delete("grid")
        fractions = GRID_MODES[self.app.grid_mode][1]
        if not fractions or not self.app.crop.get():
            return
        H, W = v.img.shape[:2]
        for f in fractions:
            for a, b in (((f * (W - 1), 0), (f * (W - 1), H - 1)), ((0, f * (H - 1)), (W - 1, f * (H - 1)))):
                x0, y0 = v.to_canvas(a)
                x1, y1 = v.to_canvas(b)
                v.create_line(x0, y0, x1, y1, fill="#000000", width=3, tags="grid")
                v.create_line(x0, y0, x1, y1, fill=GRID_COLOR, width=1, tags="grid")


class Magnifier(tk.Frame):
    """Docked zoomed view of the selected corner: crosshair, editable X and Y (whole pixels), zoom, nudge arrows,
    and an Expand button. It stays up until the corner is deselected."""
    VIEW_W, VIEW_H = 280, 200

    def __init__(self, app):
        super().__init__(app.root, bd=2, relief="ridge")
        self.app, self.idx = app, 0
        self.zoom = float(app.settings.get("mag_zoom", MAG_ZOOM_DEFAULT))
        self.updating = False
        head = tk.Frame(self)
        head.pack(fill="x", padx=6, pady=(4, 0))
        self.title_label = tk.Label(head, anchor="w", font=("TkDefaultFont", 10, "bold"))
        self.title_label.pack(side="left")
        tk.Button(head, text="Expand", command=lambda: app.open_expanded(self.idx)).pack(side="right")
        self.canvas = tk.Canvas(self, width=self.VIEW_W, height=self.VIEW_H, bg="black", highlightthickness=0)
        self.canvas.pack(padx=6, pady=4)
        self.xvar, self.yvar, self.zvar = tk.StringVar(), tk.StringVar(), tk.StringVar()
        row1 = tk.Frame(self)
        row1.pack(fill="x", padx=6)
        self.spin(row1, "X", self.xvar, -100000, 100000, 1, self.on_spin)
        self.spin(row1, "Y", self.yvar, -100000, 100000, 1, self.on_spin)
        row2 = tk.Frame(self)
        row2.pack(fill="x", padx=6, pady=(4, 6))
        self.spin(row2, "Zoom %", self.zvar, int(ZOOM_MIN * 100), int(ZOOM_MAX * 100), 25, self.on_zoom_spin)
        for text, dx, dy in (("\u25C0", -1, 0), ("\u25B6", 1, 0), ("\u25B2", 0, -1), ("\u25BC", 0, 1)):
            tk.Button(row2, text=text, width=2, command=lambda dx=dx, dy=dy: self.nudge(dx, dy)).pack(side="left", padx=1)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", lambda e: self.zoom_by(1.25 if e.delta > 0 else 0.8))
        self.canvas.bind("<Button-4>", lambda e: self.zoom_by(1.25))
        self.canvas.bind("<Button-5>", lambda e: self.zoom_by(0.8))

    def spin(self, parent, label, var, lo, hi, step, cmd):
        tk.Label(parent, text=label).pack(side="left", padx=(0, 2))
        sb = tk.Spinbox(parent, from_=lo, to=hi, increment=step, width=6, textvariable=var, format="%.0f", command=cmd)
        sb.pack(side="left", padx=(0, 8))
        sb.bind("<Return>", lambda e: cmd())
        sb.bind("<FocusOut>", lambda e: cmd())
        return sb

    def set_corner(self, idx):
        self.idx = idx
        self.title_label.config(text="Corner %s" % CORNER_NAMES[idx])
        self.set_vars()
        self.render()

    def point(self):
        return self.app.corners[self.idx]

    def set_vars(self):
        self.updating = True
        self.xvar.set("%d" % round(self.point()[0]))
        self.yvar.set("%d" % round(self.point()[1]))
        self.zvar.set("%d" % round(self.zoom * 100))
        self.updating = False

    def on_spin(self):
        if self.updating:
            return
        try:
            x, y = int(round(float(self.xvar.get()))), int(round(float(self.yvar.get())))
        except ValueError:
            return
        self.app.corners[self.idx] = [x, y]
        self.app.after_edit(skip_magnifier=True)
        self.render()

    def on_zoom_spin(self):
        if self.updating:
            return
        try:
            z = float(self.zvar.get()) / 100.0
        except ValueError:
            return
        self.zoom = min(ZOOM_MAX, max(ZOOM_MIN, z))
        self.set_vars()
        self.render()

    def nudge(self, dx, dy):
        p = self.point()
        self.app.corners[self.idx] = [p[0] + dx, p[1] + dy]
        self.app.after_edit()

    def on_click(self, e):
        x, y = self.point()
        self.app.corners[self.idx] = [round(x + (e.x - self.VIEW_W / 2) / self.zoom), round(y + (e.y - self.VIEW_H / 2) / self.zoom)]
        self.app.after_edit()

    def zoom_by(self, f):
        self.zoom = min(ZOOM_MAX, max(ZOOM_MIN, self.zoom * f))
        self.set_vars()
        self.render()

    def render(self):
        self.photo = render_corner_view(self.app.img, self.point(), self.zoom, self.VIEW_W, self.VIEW_H)
        c = self.canvas
        c.delete("all")
        c.create_image(0, 0, anchor="nw", image=self.photo)
        c.create_line(0, self.VIEW_H / 2, self.VIEW_W, self.VIEW_H / 2, fill="#ff4040")
        c.create_line(self.VIEW_W / 2, 0, self.VIEW_W / 2, self.VIEW_H, fill="#ff4040")
        c.create_oval(self.VIEW_W / 2 - 8, self.VIEW_H / 2 - 8, self.VIEW_W / 2 + 8, self.VIEW_H / 2 + 8,
                      fill=CORNER_COLOR, outline="white", width=2)


# ===== settings, file names, backups and the queue =====

HDS7_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})[ _T](\d{2}-\d{2}-)(\d{2})(.*)$")
RECENTS_MAX = 500
BACKUP_LIMIT = 999         # numbered backup names (.trashed_name~2 and so on). Normal files stop at ~99.
QUEUE_POLL_MS = 3000       # how often a running window looks for files added by Send To
LOCK_FRESH_SECONDS = 10    # a running window refreshes its lock more often than this

SETTINGS_DEFAULTS = {
    "undo_method": "trashed",       # trashed (.trashed_name.ext), originals (.originals folder) or recycle
    "naming_mode": "standard",      # standard (name~1) or hds7 (the seconds count up)
    "auto_advance": False,          # in full directory mode, move on to the next photo after each save
    "confirm_overwrite": True,      # ask before Overwrite!, which has no backup and no undo
    "confirm_actions": True,        # ask before applying a gesture, Reset, Zero or 5%, and before leaving a photo with unsaved changes
    "jpeg_quality": 95,
    "fill_mode": "reflect",         # reflect, replicate or black: what fills a corner that lies outside the photo
    "no_subsampling": True,         # keeps color sharp around text
    "mag_zoom": 6.0,
    "show_recents": True,
    "help_shown": False,            # the first-run help has been shown (the registry keeps its own copy)
    "ops_count": 0,                 # operations done: saves, renames, deletes and DBG pictures (the registry keeps a copy)
    "coffee_shown": 0,              # the last coffee nag number that was shown (the registry keeps a copy)
    "coffee_paid": False,           # honor system: ticked after a coffee was sent, no more nags
    "recents": [],
}


def settings_path():
    override = os.environ.get("FLYERIZE_GUI_SETTINGS")
    if override:
        return override
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "Flyerize_gui", "settings.json")


def load_settings():
    s = dict(SETTINGS_DEFAULTS)
    try:
        with open(settings_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in SETTINGS_DEFAULTS:
            if k in data:
                s[k] = data[k]
    except (OSError, ValueError):
        pass
    s["recents"] = list(s["recents"])[:RECENTS_MAX]
    return s


def save_settings(s):
    try:
        os.makedirs(os.path.dirname(settings_path()), exist_ok=True)
        with open(settings_path(), "w", encoding="utf-8") as f:
            json.dump(s, f, indent=1)
    except OSError:
        pass


def log_path():
    return os.path.join(os.path.dirname(settings_path()), "Flyerize_gui.log")


def write_log(fields):
    """Append one tab-separated line to the log. When the log has reached LOG_MAX_BYTES it is first renamed to
    Flyerize_gui.log.old, replacing any older .old file, and a fresh log starts. A failed write is ignored."""
    path = log_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            if os.path.getsize(path) >= LOG_MAX_BYTES:
                os.replace(path, path + ".old")
        except OSError:
            pass
        with open(path, "a", encoding="utf-8") as f:
            f.write("\t".join(fields) + "\n")
    except OSError:
        pass


def log_event(action, src, dst=None):
    """One line in the log: a readable time, the action, the file it came from and the file it made (if any).
    The fields are separated by tabs, because paths contain spaces. A failed write is ignored."""
    fields = [time.strftime("[%Y-%m-%d %H:%M:%S]"), action, os.path.abspath(src)]
    if dst:
        fields.append(dst if dst.startswith("(") else os.path.abspath(dst))
    write_log(fields)


def run_kind():
    return "exe" if getattr(sys, "frozen", False) else "script"


def log_note(action, *fields):
    """A log line with no file paths of its own: a readable time, the action, then the fields as given."""
    write_log([time.strftime("[%Y-%m-%d %H:%M:%S]"), action] + list(fields))


def log_start():
    """The first log line of every run: the program, which kind it is (exe or script), where its files really are,
    and whether Windows looks to be redirecting them (Microsoft Store Python). The registry key is named too,
    followed by the three numbers the program reads back from it (help, ops, coffee), because regedit cannot show
    the private copy that a redirected run keeps."""
    asked = os.path.abspath(settings_path())
    real = os.path.realpath(asked)
    redirected = os.path.normcase(real) != os.path.normcase(asked) or "WindowsApps" in sys.executable
    fields = [time.strftime("[%Y-%m-%d %H:%M:%S]"), "START", VERSION, "exe" if getattr(sys, "frozen", False) else "script",
              sys.executable, "settings=" + real, "redirected=" + ("yes" if redirected else "no"), "registry=HKCU\\" + REG_PATH,
              "help=" + reg_text("help"), "ops=" + reg_text("ops"), "coffee=" + reg_text("coffee")]
    write_log(fields)


def as_int(v):
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return 0


def reg_get(name):
    """A number kept in the registry: 0 if it was never written, None if the registry cannot be read at all.
    None is treated as 'show nothing', because the registry exists to make a doubled message less likely."""
    if winreg is None:
        return 0
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
            return int(winreg.QueryValueEx(k, name)[0])
    except FileNotFoundError:
        return 0
    except (OSError, ValueError):
        return None


def reg_text(name):
    v = reg_get(name)
    return "unreadable" if v is None else str(v)


def reg_set(name, value):
    """Write a number to the registry and read it back. True only if the registry now holds exactly that number."""
    if winreg is None:
        return True
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
            winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, int(value))
    except OSError:
        return False
    return reg_get(name) == int(value)


def settings_file_has(key, value):
    """Read the settings file again from disk and check that it holds this value."""
    try:
        with open(settings_path(), "r", encoding="utf-8") as f:
            return json.load(f).get(key) == value
    except (OSError, ValueError):
        return False


def coffee_milestone(count):
    """The highest coffee nag number at or below this count, or 0 if none has been reached."""
    if count < COFFEE_FIXED[0]:
        return 0
    top = COFFEE_FIXED[-1]
    if count <= top:
        return max(m for m in COFFEE_FIXED if m <= count)
    return top + ((count - top) // COFFEE_EVERY) * COFFEE_EVERY


def temp_dir():
    return os.environ.get("FLYERIZE_GUI_TEMP") or tempfile.gettempdir()


def user_name():
    return os.environ.get("USERNAME") or os.environ.get("USER") or "user"


def queue_file():
    return os.path.join(temp_dir(), "flyerize_gui_queue_%s.txt" % user_name())


def lock_file():
    return os.path.join(temp_dir(), "flyerize_gui_running_%s.lock" % user_name())


def touch_lock():
    try:
        with open(lock_file(), "w") as f:
            f.write("%d %f" % (os.getpid(), time.time()))
    except OSError:
        pass


def clear_lock():
    try:
        os.remove(lock_file())
    except OSError:
        pass


def running_instance():
    """True if a Flyerize_gui window is open and has refreshed its lock recently."""
    try:
        return time.time() - os.path.getmtime(lock_file()) < LOCK_FRESH_SECONDS
    except OSError:
        return False


def forward_to_running(paths):
    """Hand files to the window that is already open. It picks them up within a few seconds."""
    with open(queue_file(), "a", encoding="utf-8") as f:
        for p in paths:
            f.write(p + "\n")


def read_queue():
    """Take whatever has been forwarded, and empty the file."""
    try:
        with open(queue_file(), "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        open(queue_file(), "w").close()
        return lines
    except OSError:
        return []


def collect_paths(args):
    """Image files from the arguments. A folder contributes every image in it, outputs and edits of edits included,
    on purpose: no guessing. Only dot files (backups) are left out."""
    paths = []
    for a in args:
        if os.path.isdir(a):
            for n in sorted(os.listdir(a)):
                p = os.path.join(a, n)
                if os.path.isfile(p) and not n.startswith(".") and os.path.splitext(n)[1].lower() in IMAGE_EXTS:
                    paths.append(p)
        elif os.path.isfile(a):
            paths.append(a)
    return paths


def output_ext(path):
    ext = os.path.splitext(path)[1].lower()
    return ext if ext in (".png", ".bmp") else ".jpg"


def earliest_time(path, pil=None):
    """The earliest of the photo's EXIF date taken, file created and file modified times, in local time."""
    times = []
    try:
        st = os.stat(path)
        times += [datetime.datetime.fromtimestamp(st.st_ctime), datetime.datetime.fromtimestamp(st.st_mtime)]
    except OSError:
        pass
    try:
        exif = pil.getexif() if pil is not None else None
        raw = None
        if exif is not None:
            raw = exif.get_ifd(0x8769).get(36867) or exif.get(306)
        if raw:
            times.append(datetime.datetime.strptime(str(raw).strip()[:19], "%Y:%m:%d %H:%M:%S"))
    except Exception:
        pass
    return min(times) if times else datetime.datetime.now()


def split_numbers(stem):
    """name~1~4~7~2 becomes ('name', 14). Every trailing ~nn counts as one of our numbers."""
    total = 0
    while True:
        m = re.match(r"^(.*)~(\d+)$", stem)
        if not m:
            return stem, total
        stem, total = m.group(1), total + int(m.group(2))


def folded_name(path, naming_mode):
    """The name a photo starts with in the box. A name with no ~nn is left alone. Otherwise the numbers are folded
    together, so name~1~4~7~2 starts as name~14, and in HDS-7 naming they are added to the seconds."""
    stem = os.path.splitext(os.path.basename(path))[0]
    ext = output_ext(path)
    base, total = split_numbers(stem)
    if total == 0:
        return stem + ext
    if naming_mode == "hds7":
        m = HDS7_NAME.match(base)
        if m and int(m.group(3)) + total <= 99:
            return "%s %s%02d%s%s" % (m.group(1), m.group(2), int(m.group(3)) + total, m.group(4), ext)
    return "%s~%d%s" % (base, total, ext)


def new_file_candidates(path, naming_mode, when=None, ext_override=None):
    """The names a new file may take, in order. Standard: name~1 to name~99. HDS-7: the seconds count up by one
    to 99 (a name that does not follow HDS-7 gets an HDS-7 date prefix first). No overflow: when they run out,
    the user renames something outside this program."""
    d, name = os.path.split(path)
    stem = os.path.splitext(name)[0]
    ext = ext_override or output_ext(path)
    base, total = split_numbers(stem)
    if naming_mode == "hds7":
        m = HDS7_NAME.match(base)
        if m:
            date, hm, sec, rest = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            for s in range(sec + total if total else sec + 1, 100):
                yield os.path.join(d, "%s %s%02d%s%s" % (date, hm, s, rest, ext))      # a space between date and time on output
            return
        when = when or datetime.datetime.now()
        pre = when.strftime("%Y-%m-%d %H-%M-")
        for s in range(when.second + 1, 100):
            yield os.path.join(d, "%s%02d %s%s" % (pre, s, stem, ext))
        return
    for n in range(max(total, 1), 100):
        yield os.path.join(d, "%s~%d%s" % (base, n, ext))


def unique_path(path, limit=BACKUP_LIMIT):
    """The path itself if it is free, else name~2, name~3 and so on up to name~limit. None when they are all taken."""
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    for n in range(2, limit + 1):
        candidate = "%s~%d%s" % (stem, n, ext)
        if not os.path.exists(candidate):
            return candidate
    return None


def send_to_recycle_bin(path):
    """Windows only. Returns True if the file went to the Recycle Bin. Drives without a bin (network shares, USB
    sticks) report failure, and the caller falls back to a backup file."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", ctypes.c_wchar_p),
                        ("pTo", ctypes.c_wchar_p), ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", wintypes.BOOL),
                        ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", ctypes.c_wchar_p)]

        op = SHFILEOPSTRUCTW()
        op.wFunc = 3                       # FO_DELETE
        op.pFrom = os.path.abspath(path) + "\0"
        op.fFlags = 0x40 | 0x10 | 0x4 | 0x400   # allow undo, no confirmation, silent, no error UI
        result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
        return result == 0 and not op.fAnyOperationsAborted and not os.path.exists(path)
    except Exception:
        return False


def make_undo_copy(path, method):
    """Move the original out of the way so the crop can take its place. Returns where it went."""
    d, name = os.path.split(path)
    if method == "recycle" and send_to_recycle_bin(path):
        return "the Recycle Bin"
    if method == "originals":
        folder = os.path.join(d, ".originals")
        os.makedirs(folder, exist_ok=True)
        dest = unique_path(os.path.join(folder, name))
    else:
        dest = unique_path(os.path.join(d, ".trashed_" + name))
    if dest is None:
        raise OSError("Every numbered backup name is taken (up to ~%d). Remove some of the old backups outside Flyerize_gui "
                      "and try again. Nothing was changed." % BACKUP_LIMIT)
    os.replace(path, dest)
    return dest


def write_image(arr, pil_in, out_path, quality=95, no_subsampling=True, times=None):
    res = Image.fromarray(arr)
    if out_path.lower().endswith((".jpg", ".jpeg")):
        kw = {"quality": int(quality)}
        if no_subsampling:
            kw["subsampling"] = 0
        try:
            res.save(out_path, exif=pil_in.getexif(), **kw)
        except Exception:
            res.save(out_path, **kw)
    else:
        res.save(out_path)
    if times:
        os.utime(out_path, times)


def shorten_middle(text, n):
    if len(text) <= n or n < 12:
        return text
    keep = n - 3
    return text[:keep // 2] + "..." + text[len(text) - (keep - keep // 2):]


# ===== settings panel and recent crops =====

class SettingsPanel(tk.Frame):
    """Settings, over the main view. Changes apply and are saved at once."""

    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        s = app.settings
        body = tk.Frame(self)
        body.place(relx=0.5, rely=0.5, anchor="center")
        head = tk.Frame(body)
        head.pack(anchor="w", pady=(0, 6))
        tk.Label(head, text="Settings", font=("TkDefaultFont", 13, "bold")).pack(side="left")
        tk.Label(head, text="Here, let me give you enough rope...", font=("TkDefaultFont", 10, "italic")).pack(side="left", padx=(14, 0), anchor="s")
        tk.Label(body, text="Overwrite! replaces the original with no backup and no undo, and saves space only as far as your crop\n"
                            "is smaller. Uploaded copies and deleted folders keep the old picture. Turn the question off if you're sure.",
                 justify="left").pack(anchor="w", pady=(0, 2))
        self.confirm_overwrite = tk.BooleanVar(value=s["confirm_overwrite"])
        tk.Checkbutton(body, text="Ask before Overwrite!", variable=self.confirm_overwrite, command=self.commit).pack(anchor="w", pady=(0, 6))
        self.undo = tk.StringVar(value=s["undo_method"])
        self.naming = tk.StringVar(value=s["naming_mode"])
        self.confirm_actions = tk.BooleanVar(value=s["confirm_actions"])
        self.show_recents = tk.BooleanVar(value=s.get("show_recents", True))
        self.coffee_paid = tk.BooleanVar(value=bool(s.get("coffee_paid", False)))
        self.quality = tk.StringVar(value=str(s["jpeg_quality"]))
        self.fill_text = tk.StringVar(value=dict(FILL_CHOICES).get(s.get("fill_mode", "reflect"), FILL_CHOICES[0][1]))
        self.sharp = tk.BooleanVar(value=s["no_subsampling"])
        self.zoom = tk.StringVar(value="%d" % round(float(s["mag_zoom"]) * 100))

        def group(title, var, options):
            f = tk.LabelFrame(body, text=title, padx=10, pady=4)
            f.pack(fill="x", pady=4)
            for value, label in options:
                tk.Radiobutton(f, text=label, variable=var, value=value, anchor="w", command=self.commit).pack(fill="x")

        group("Where backups go (Replace and Delete)", self.undo, [("trashed", ".trashed_name.ext beside the photo"),
                                                   ("originals", ".originals folder beside the photo"),
                                                   ("recycle", "Recycle Bin (Windows, local drives)")])
        group("Names of new files", self.naming, [("standard", "name~1, name~2, and so on (up to 99)"),
                                                  ("hds7", "HDS-7 date and time, the seconds count up (up to 99); a name with none gets one in front")])
        tk.Checkbutton(body, text="Ask before applying a gesture, Reset, Zero or 5%, and before leaving a photo with unsaved changes",
                       variable=self.confirm_actions, command=self.commit).pack(anchor="w")
        tk.Checkbutton(body, text="Show the recent crops list on the right", variable=self.show_recents, command=self.commit).pack(anchor="w")
        tk.Checkbutton(body, text="I have sent a coffee (turns off the coffee nags)", variable=self.coffee_paid, command=self.commit).pack(anchor="w")
        row = tk.Frame(body)
        row.pack(anchor="w", pady=(6, 0))
        tk.Label(row, text="JPEG quality").pack(side="left")
        sb = tk.Spinbox(row, from_=50, to=100, width=5, textvariable=self.quality, command=self.commit)
        sb.pack(side="left", padx=6)
        sb.bind("<Return>", lambda e: self.commit())
        sb.bind("<FocusOut>", lambda e: self.commit())
        tk.Label(row, text="Empty corner fill").pack(side="left", padx=(24, 0))
        fill_box = ttk.Combobox(row, textvariable=self.fill_text, values=[t for _, t in FILL_CHOICES], state="readonly", width=64)
        fill_box.pack(side="left", padx=6)
        fill_box.bind("<<ComboboxSelected>>", lambda e: self.commit())
        tk.Checkbutton(body, text="Keep color sharp around text (no chroma subsampling)", variable=self.sharp, command=self.commit).pack(anchor="w")
        row = tk.Frame(body)
        row.pack(anchor="w", pady=(6, 0))
        tk.Label(row, text="Magnifier zoom %").pack(side="left")
        sb = tk.Spinbox(row, from_=int(ZOOM_MIN * 100), to=int(ZOOM_MAX * 100), increment=25, width=6, textvariable=self.zoom, command=self.commit)
        sb.pack(side="left", padx=6)
        sb.bind("<Return>", lambda e: self.commit())
        sb.bind("<FocusOut>", lambda e: self.commit())
        tk.Button(body, text="Close", width=12, height=2, command=app.close_panel).pack(pady=(10, 0))
        self.place(in_=app.canvas, x=0, y=0, relwidth=1, relheight=1)

    def commit(self):
        s = self.app.settings
        s["undo_method"], s["naming_mode"] = self.undo.get(), self.naming.get()
        s["no_subsampling"] = bool(self.sharp.get())
        s["confirm_actions"] = bool(self.confirm_actions.get())
        s["confirm_overwrite"] = bool(self.confirm_overwrite.get())
        s["show_recents"] = bool(self.show_recents.get())
        s["coffee_paid"] = bool(self.coffee_paid.get())
        s["fill_mode"] = next((k for k, t in FILL_CHOICES if t == self.fill_text.get()), "reflect")
        try:
            s["jpeg_quality"] = min(100, max(50, int(float(self.quality.get()))))
            s["mag_zoom"] = min(ZOOM_MAX, max(ZOOM_MIN, float(self.zoom.get()) / 100.0))
        except ValueError:
            pass
        save_settings(s)
        self.app.sync_recents_visibility()


# ===== main window =====

def segment_distance(px, py, ax, ay, bx, by):
    """Distance from a point to a line segment."""
    dx, dy = bx - ax, by - ay
    ll = dx * dx + dy * dy
    t = 0.0 if ll == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / ll))
    return ((px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2) ** 0.5


CORNER_KEYS = {"1": 0, "2": 1, "3": 3, "4": 2}      # 1 TL, 2 TR, 3 BL, 4 BR
WASD = {"a": (-1, 0), "d": (1, 0), "w": (0, -1), "s": (0, 1)}
ARROWS = {"Left": (-1, 0), "Right": (1, 0), "Up": (0, -1), "Down": (0, 1)}


class Tooltip:
    """A small hint that appears when the pointer rests on a widget."""

    def __init__(self, widget, text, delay=600):
        self.widget, self.text, self.delay = widget, text, delay
        self.tip, self.after_id = None, None
        widget.bind("<Enter>", self.schedule, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def schedule(self, event=None):
        self.hide()
        self.after_id = self.widget.after(self.delay, self.show)

    def show(self):
        self.after_id = None
        if self.tip is not None:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry("+%d+%d" % (x, y))
        tk.Label(self.tip, text=self.text, justify="left", wraplength=340, bg="#FFFFE0", fg="#000000",
                 relief="solid", borderwidth=1, padx=6, pady=3).pack()

    def hide(self, event=None):
        if self.after_id is not None:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class App:
    HIT = 14      # how close (screen pixels) a click must be to a corner or purple dot
    SLOP = 4      # how far the pointer must move before a click becomes a drag

    def __init__(self, root, paths):
        self.root, self.paths = root, list(paths)
        self.settings = load_settings()
        self.index, self.path = 0, self.paths[0]
        self.img = np.zeros((10, 10, 3), np.uint8)
        self.pil, self.photo_when = None, None
        self.corners = np.zeros((4, 2))
        self.bends = {s: (0.5, 0.0) for s in SIDES}
        self.rot = 0
        self.crop = tk.BooleanVar(value=True)
        self.mirror = tk.BooleanVar(value=False)
        self.bw = tk.BooleanVar(value=False)
        self.zoom_var = tk.StringVar(value="100")
        self.auto = tk.BooleanVar(value=bool(self.settings["auto_advance"]))
        self.added = 0                          # results added after this photo by Save New
        self.grid_mode = 0                      # index into GRID_MODES, changed with the G key
        self.result_entries = set()             # list entries that are Save New results: Next and Auto skip them
        self.finish_shown = False               # the end-of-list dialog has been shown for this list
        self.selected = None
        self.targets, self.press, self.drag, self.moved, self.stroke = [], None, None, False, []
        self.panel, self.mag, self.mag_side, self.ghost_bar, self.ghost_label = None, None, None, None, None
        self.recents_panel = None
        self.ghost, self.trace = None, None
        self.last_written = self.last_outline = None
        self.saved = None
        self.help_win = self.coffee_win = self.coffee_img = None
        self.first_run_session = False
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry("%dx%d" % (int(sw * 0.8), int(sh * 0.8)))      # a normal window: the OS decides where it opens
        root.minsize(900, 520)
        mid = tk.Frame(root)
        mid.pack(fill="both", expand=True)
        self.recents_frame = tk.Frame(mid, width=220)
        self.recents_frame.pack_propagate(False)
        tk.Label(self.recents_frame, text="Recent crops", anchor="w", font=("TkDefaultFont", 9, "bold")).pack(fill="x", padx=4, pady=(4, 0))
        holder = tk.Frame(self.recents_frame)
        holder.pack(fill="both", expand=True, padx=4, pady=4)
        self.recents_box = tk.Listbox(holder, activestyle="none", font=("TkDefaultFont", 8), exportselection=False)
        rsb = tk.Scrollbar(holder, command=self.recents_box.yview)
        self.recents_box.config(yscrollcommand=rsb.set)
        rsb.pack(side="right", fill="y")
        self.recents_box.pack(side="left", fill="both", expand=True)
        self.recents_box.bind("<ButtonRelease-1>", self.pick_recent)
        self.recents_entries = []
        if self.settings["show_recents"]:
            self.recents_frame.pack(side="right", fill="y")
        self.canvas = ZoomView(mid, self.img, on_change=self.on_view_change, bg="#202020")
        self.canvas.pack(side="left", fill="both", expand=True)
        bar1 = tk.Frame(root)
        bar1.pack(fill="x", padx=8, pady=(6, 0))
        self.preview_btn = tk.Button(bar1, text="PREVIEW", width=9, command=self.on_preview)
        self.preview_btn.pack(side="left", padx=(0, 10))
        tk.Label(bar1, text=VERSION, fg="#666666").pack(side="right")      # sits right above EXIT
        sb = tk.Spinbox(bar1, from_=2, to=1600, increment=10, width=6, textvariable=self.zoom_var, format="%.0f",
                        command=self.on_zoom_spin)
        sb.pack(side="left", padx=(2, 0))
        sb.bind("<Return>", lambda e: (self.on_zoom_spin(), self.canvas.focus_set()))
        sb.bind("<FocusOut>", lambda e: self.on_zoom_spin())
        tk.Button(bar1, text="Fit", width=4, command=self.canvas.fit).pack(side="left", padx=2)
        tk.Button(bar1, text="Reset", width=6, command=self.propose_reset).pack(side="left", padx=(12, 2))
        tk.Button(bar1, text="Zero", width=6, command=self.propose_zero).pack(side="left", padx=2)
        tk.Button(bar1, text="5%", width=4, command=self.propose_inset).pack(side="left", padx=2)
        gridbox = tk.Frame(bar1)
        gridbox.pack(side="left", padx=(12, 2))
        self.grid_box = tk.Label(gridbox, text="", width=2, relief="sunken", bd=2, bg="white", fg="black", font=("TkDefaultFont", 9, "bold"))
        self.grid_box.pack(side="left")
        grid_text = tk.Label(gridbox, text="Grid")
        grid_text.pack(side="left", padx=(4, 0))
        for part in (gridbox, self.grid_box, grid_text):
            part.bind("<Button-1>", lambda e: self.cycle_grid(1))
            part.bind("<Button-3>", lambda e: self.cycle_grid(-1))
            Tooltip(part, "Grid lines for lining things up: 1 is a crosshair, 2 is thirds, 4 is fifths, 9 is tenths. "
                          "Click or press G for the next one, right-click or Shift+G for the previous one.")
        self.update_grid_box()
        tk.Checkbutton(bar1, text="Crop to lines", variable=self.crop).pack(side="left", padx=(12, 2))
        self.rot_btn = tk.Button(bar1, text="Rotate CCW: 0", width=13, command=self.rotate)
        self.rot_btn.pack(side="left", padx=2)
        tk.Checkbutton(bar1, text="Mirror", variable=self.mirror).pack(side="left", padx=2)
        tk.Checkbutton(bar1, text="BW/WB", variable=self.bw).pack(side="left", padx=2)
        tk.Button(bar1, text="DBG", command=self.on_dbg).pack(side="left", padx=2)
        hints = {
            "Zoom %": "How far the main view is zoomed, in percent. The mouse wheel zooms too, about the pointer.",
            "Fit": "Zooms the main view to show the whole photo.",
            "Reset": "Finds the corners again automatically, and clears the bends, rotation, mirror and BW/WB. Ctrl-R does the same.",
            "Zero": "Puts the four corners at the corners of the photo, with straight sides. The 0 key does the same.",
            "5%": "Puts the four corners 5 percent in from the photo's edges, with straight sides. The 5 key does the same.",
            "Crop to lines": "On cuts the result at your four sides. Off keeps the whole photo, straightened.",
            "Mirror": "Flips the result left to right. It changes only the preview and the saved result, not the main view.",
            "BW/WB": "Experimental: invert bright and dark. Very light pixels become dark gray and very dark pixels become light gray. It changes only the preview and the saved result, not the main view.",
            "DBG": "Writes a copy of the original with the crop lines (and gridlines) drawn on it.",
        }
        for w in bar1.winfo_children():
            try:
                label = w.cget("text")
            except tk.TclError:
                continue
            if label in hints:
                Tooltip(w, hints[label])
        Tooltip(sb, hints["Zoom %"])
        Tooltip(self.rot_btn, "Turns the result counter-clockwise in 90 degree steps. The number is the current turn. It changes only the preview and the saved result, not the main view.")
        bar2 = tk.Frame(root)
        bar2.pack(fill="x", padx=8, pady=6)
        self.auto_chk = tk.Checkbutton(bar2, text="Auto", variable=self.auto, command=self.on_auto)
        self.auto_chk.pack(side="left", padx=(0, 2))
        self.prev_btn = tk.Button(bar2, text="Back", width=8, command=self.on_back)
        self.prev_btn.pack(side="left", padx=(12, 2))
        self.go_btn = tk.Button(bar2, text="Move \u00b1nnn", width=11, command=self.on_go)
        self.go_btn.pack(side="left", padx=2)
        self.next_btn = tk.Button(bar2, text="Skip to Next", width=12, command=self.on_skip)
        self.next_btn.pack(side="left", padx=2)
        self.save_btn = tk.Button(bar2, text="Save New", width=11, command=lambda: self.do_save("new"))
        self.save_btn.pack(side="left", padx=(12, 2))
        self.replace_btn = tk.Button(bar2, text="Replace", width=10, command=lambda: self.do_save("replace_undo"))
        self.replace_btn.pack(side="left", padx=2)
        self.overwrite_btn = tk.Button(bar2, text="Overwrite!", width=12, command=lambda: self.do_save("replace_perm"))
        self.overwrite_btn.pack(side="left", padx=2)
        self.rename_btn = tk.Button(bar2, text="Rename", width=9, command=self.on_rename)
        self.rename_btn.pack(side="left", padx=2)
        self.delete_btn = tk.Button(bar2, text="Delete", width=8, command=self.on_delete)
        self.delete_btn.pack(side="left", padx=2)
        self.btn_bg, self.btn_fg = self.save_btn.cget("bg"), self.save_btn.cget("fg")
        Tooltip(self.save_btn, "Saves the result as a new file and leaves the original alone. If the name is taken, a number is added. Alt+S does the same.")
        Tooltip(self.replace_btn, "Saves the result under the name in the box and backs up whatever file has that name, or the original if the name is free. Settings says where the backup goes. Alt+A does the same.")
        Tooltip(self.overwrite_btn, "Replaces this photo with the result. There is no backup and this cannot be undone. It is gray while the name box has been edited, and for HEIC photos. Alt+D does the same.")
        Tooltip(self.delete_btn, "Moves this photo aside as a backup and goes to the next one. Nothing is asked, and Settings says where the backup goes. The Delete key does the same.")
        Tooltip(self.rename_btn, "Renames this file to the name in the box without rewriting the picture. The file keeps its own extension, and a taken name gets a number. Alt+R does the same.")
        Tooltip(self.auto_chk, "In full directory mode, automatically advances to the next image after each file is saved.")
        Tooltip(self.prev_btn, "Goes back one photo. Files saved with Save New are in the list, so you can go back to them. Alt+B or Ctrl+B does the same, and Ctrl+Shift+Alt+B jumps back 100.")
        Tooltip(self.go_btn, "Jumps ahead by a number of photos, or back with a negative number. Alt+M does the same.")
        Tooltip(self.next_btn, "Goes to the next original photo without saving anything. Alt+N or Ctrl+N does the same, and Ctrl+Shift+Alt+N jumps ahead 100.")
        settings_btn = tk.Button(bar2, text="Settings", width=8, command=self.open_settings)
        settings_btn.pack(side="left", padx=(10, 2))
        exit_btn = tk.Button(bar2, text="EXIT", width=7, command=self.on_exit)
        exit_btn.pack(side="right")
        Tooltip(self.preview_btn, "Shows the corrected result over the main view. Click again, or press Esc, to go back. Alt+V does the same.")
        Tooltip(settings_btn, "Opens the settings: where backups go, how files are numbered, JPEG quality and more.")
        Tooltip(exit_btn, "Closes Flyerize_gui. If there are unsaved changes it asks first, unless that is turned off in Settings.")
        bar3 = tk.Frame(root)
        bar3.pack(fill="x", padx=8, pady=(0, 6))
        tk.Label(bar3, text="New name:").pack(side="left", anchor="n", pady=2)
        self.new_name = tk.StringVar()
        self.new_name.trace_add("write", lambda *a: self.update_overwrite_state())
        self.name_baseline = ""                 # what the program last put in the box. Anything else is typing.
        self.name_entry = tk.Entry(bar3, textvariable=self.new_name, width=46)
        self.name_entry.pack(side="left", anchor="n", padx=(4, 12))
        self.name_entry.bind("<Return>", lambda e: self.canvas.focus_set())
        Tooltip(self.name_entry, "The name the next save will use. Edit it before pressing Save New, Replace, Overwrite! or Rename.")
        self.status = tk.Label(bar3, anchor="nw", justify="left", fg="#FFD700", bg="#000000", padx=6, pady=2, height=3)
        self.status.pack(side="left", fill="x", expand=True)

        self.canvas.bind("<Button-1>", self.on_down)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_up)
        self.canvas.bind("<Button-3>", self.on_right)
        root.bind("<Escape>", lambda e: self.on_escape())
        root.bind("<Key>", self.on_key)
        root.bind("<Control-r>", lambda e: self.propose_reset())
        root.bind("<Control-R>", lambda e: self.propose_reset())
        root.bind("<Control-Key>", self.on_ctrl_key)
        root.bind("<Alt-Key>", self.on_alt_key)
        root.bind("<Control-Alt-Key>", self.on_ctrl_alt_key)
        root.bind("<Delete>", self.on_delete_key)
        root.bind("<F1>", lambda e: self.show_help())
        root.protocol("WM_DELETE_WINDOW", self.on_exit)
        touch_lock()
        log_start()
        self.load(0)
        self.poll_id = root.after(QUEUE_POLL_MS, self.poll_queue)
        root.after(600, self.first_run_check)

    def say(self, text):
        n = max(30, self.status.winfo_width() // 7) if self.status.winfo_width() > 50 else 110
        self.status.config(text="\n".join(shorten_middle(line, n) for line in text.split("\n")))

    # one photo at a time

    def set_title(self):
        n = len(self.paths)
        self.root.title("Flyerize_gui  -  %s%s" % ("(%d of %d)  -  " % (self.index + 1, n) if n > 1 else "", os.path.abspath(self.path)))
        self.next_btn.config(state="normal" if self.next_index() is not None else "disabled")
        self.prev_btn.config(state="normal" if n > 1 else "disabled")
        self.go_btn.config(state="normal" if n > 1 else "disabled")
        self.auto_chk.config(state="normal" if n > 1 else "disabled")
        self.update_auto_look()

    def load(self, index):
        self.index, self.path = index, self.paths[index]
        self.img, self.pil = load_image(self.path)
        self.photo_when = earliest_time(self.path, self.pil)      # read now, before any replacing changes the file
        H, W = self.img.shape[:2]
        self.corners = np.round(np.array(initial_corners(self.img), dtype=np.float64))
        self.bends = {s: (0.5, 0.0) for s in SIDES}
        self.rot = 0
        self.mirror.set(False)
        self.bw.set(False)
        self.rot_btn.config(text="Rotate CCW: 0")
        self.last_written = self.last_outline = None
        self.added = 0
        self.ghost, self.trace, self.selected = None, None, None
        self.close_panel()
        self.hide_ghost_bar()
        self.hide_magnifier()
        self.canvas.img, self.canvas.cache = self.img, (None, None)
        self.canvas.fit()
        # nothing is saved yet, so the baseline is the untouched picture: corners on the border, sides straight
        self.saved = self.snapshot([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], {s: (0.5, 0.0) for s in SIDES}, True, 0, False, False)
        self.set_title()
        self.refresh_name()
        self.refresh_recents()
        self.canvas.focus_set()
        self.say("Wheel zooms. Drag a corner, a side line (Shift frees it) or a purple dot. Keys 1 to 4 pick a corner. Draw a rectangle, a Z or a slash to start.")

    def is_result(self, i):
        return os.path.normcase(os.path.abspath(self.paths[i])) in self.result_entries

    def next_index(self):
        """The next original photo after this one. The results added by Save New are skipped. None if there is none."""
        j = self.index + 1
        while j < len(self.paths) and self.is_result(j):
            j += 1
        return j if j < len(self.paths) else None

    def next_file(self):
        j = self.next_index()
        if j is not None:
            self.load(j)

    def go_to(self, dest):
        """Leave this photo for the list entry dest (a path), asking about unsaved changes first. The position is looked
        up after that, because saving may have added results to the list."""
        if not self.leave_ok():
            return
        self.load(self.paths.index(dest))

    def on_back(self):
        """Back one photo. From the first photo it wraps around to the last one."""
        n = len(self.paths)
        if n > 1:
            self.go_to(self.paths[(self.index - 1) % n])

    def go_by(self, count):
        """Jump count photos. A negative count goes back and wraps around past the first photo to the end of the list
        (from photo 30 of 500, back 100 lands on 430). Going ahead stops at the last photo."""
        n = len(self.paths)
        if n < 2:
            return
        j = (self.index + count) % n if count < 0 else min(n - 1, self.index + count)
        if j != self.index:
            self.go_to(self.paths[j])

    def on_go(self):
        n = len(self.paths)
        count = simpledialog.askinteger("Move", "How many photos to jump? A negative number goes back.\n"
                                        "You are on %d of %d, so the range is %d to +%d." % (self.index + 1, n, -self.index, n - 1 - self.index),
                                        parent=self.root, minvalue=-self.index, maxvalue=n - 1 - self.index)
        if count:
            self.go_to(self.paths[self.index + count])

    def snapshot(self, corners=None, bends=None, crop=None, rot=None, mirror=None, bw=None):
        """Everything that affects the output, for spotting unsaved changes."""
        corners = self.corners if corners is None else corners
        bends = self.bends if bends is None else bends
        crop = self.crop.get() if crop is None else crop
        rot = self.rot if rot is None else rot
        mirror = self.mirror.get() if mirror is None else mirror
        bw = self.bw.get() if bw is None else bw
        return (tuple(tuple(c) for c in np.round(np.asarray(corners, dtype=float), 3).tolist()),
                tuple(sorted((k, round(t, 4), round(d, 3)) for k, (t, d) in bends.items())),
                bool(crop), int(rot), bool(mirror), bool(bw))

    # files added by Send To while this window is open

    def poll_queue(self):
        try:
            touch_lock()
            lines = read_queue()
            if lines:
                added = [p for p in collect_paths(lines) if p not in self.paths]
                log_note("QUEUE_IN", VERSION, run_kind(), "items=%d" % len(lines), "added=%d" % len(added),
                         "queue=" + os.path.abspath(queue_file()))
                if added:
                    self.paths.extend(added)
                    self.set_title()
                    self.say("Added %d file(s) to the queue." % len(added))
        except Exception:
            pass
        self.poll_id = self.root.after(QUEUE_POLL_MS, self.poll_queue)

    # drawing

    def on_view_change(self):
        self.zoom_var.set("%.0f" % (self.canvas.scale * 100))
        self.redraw_overlay()
        if self.selected is not None and self.mag is not None:
            self.position_magnifier()

    def on_zoom_spin(self):
        try:
            p = float(self.zoom_var.get())
        except ValueError:
            return
        self.canvas.set_scale(p / 100.0)

    def redraw_overlay(self):
        c = self.canvas
        c.delete("ov")
        self.targets = []
        if self.grid_mode:
            self.draw_grid_main()
        for side in SIDES:
            pts = side_points(self.corners, side, self.bends[side], 60)
            flat = [v for p in pts for v in c.to_canvas(p)]
            c.create_line(*flat, fill=LINE_COLOR, width=2, tags="ov")
        if self.ghost is not None:
            flat = [v for p in self.ghost["quad"] for v in c.to_canvas(p)]
            c.create_polygon(*flat, outline="#ffffff", fill="", dash=(6, 4), width=2, tags="ov")
            for p in self.ghost["quad"]:
                x, y = c.to_canvas(p)
                c.create_oval(x - 6, y - 6, x + 6, y + 6, outline="#ff9500", width=2, tags="ov")
        for side in SIDES:
            x, y = c.to_canvas(bend_dot(self.corners, side, self.bends[side]))
            c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=BEND_COLOR, outline="white", width=2, tags="ov")
            self.targets.append(("bend", side, x, y))
        for i, name in enumerate(CORNER_NAMES):
            x, y = c.to_canvas(self.corners[i])
            if i == self.selected:
                c.create_oval(x - 13, y - 13, x + 13, y + 13, outline="#00e5ff", width=3, tags="ov")
            c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=CORNER_COLOR, outline="white", width=2, tags="ov")
            c.create_text(x + 12, y - 12, text=name, fill="white", anchor="sw", font=("TkDefaultFont", 10, "bold"), tags="ov")
            self.targets.append(("corner", i, x, y))

    def draw_grid_main(self):
        """Grid lines through the photo, drawn under the sides. They follow the bends, because they are carried through the
        same blend that makes the result."""
        try:
            vertical, horizontal = grid_lines(self.corners, self.bends, GRID_MODES[self.grid_mode][1])
        except (ValueError, np.linalg.LinAlgError, cv2.error):
            return
        c = self.canvas
        for pts in vertical + horizontal:
            flat = [v for p in pts for v in c.to_canvas(p)]
            if len(flat) >= 4 and np.all(np.isfinite(flat)):
                c.create_line(*flat, fill="#000000", width=3, tags="ov")
                c.create_line(*flat, fill=GRID_COLOR, width=1, tags="ov")

    def update_grid_box(self):
        count = GRID_MODES[self.grid_mode][2]
        self.grid_box.config(text=str(count) if count else "", bg=GRID_COLOR if count else "white")

    def cycle_grid(self, direction):
        self.grid_mode = (self.grid_mode + direction) % len(GRID_MODES)
        self.update_grid_box()
        self.redraw_overlay()
        if isinstance(self.panel, PreviewPanel):
            self.panel.draw_grid()
        name, _, count = GRID_MODES[self.grid_mode]
        self.say("Grid: off." if count == 0 else "Grid: %s, %d line%s each way." % (name.lower(), count, "" if count == 1 else "s"))

    def after_edit(self, skip_magnifier=False):
        """Something changed the corners: redraw, and keep the magnifier in step."""
        self.redraw_overlay()
        if self.selected is not None and self.mag is not None:
            if not skip_magnifier:
                self.mag.set_vars()
                self.mag.render()
            self.position_magnifier()

    # selecting a corner and the docked magnifier

    def select(self, i):
        self.selected = i
        if self.mag is None:
            self.mag = Magnifier(self)
        self.mag.set_corner(i)
        self.position_magnifier(fresh=True)
        self.redraw_overlay()

    def deselect(self):
        if self.selected is None:
            return
        self.selected = None
        self.hide_magnifier()
        self.redraw_overlay()

    def hide_magnifier(self):
        if self.mag is not None:
            self.mag.place_forget()
        self.mag_side = None

    def position_magnifier(self, fresh=False):
        """Dock the magnifier in the half of the view away from the selected corner. It only moves if the corner
        comes close to it, so it does not jump about while you drag."""
        m = self.mag
        self.root.update_idletasks()
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        mw, mh = m.winfo_reqwidth(), m.winfo_reqheight()
        sx, sy = self.canvas.to_canvas(self.corners[self.selected])
        if fresh or self.mag_side is None:
            self.mag_side = (sx < cw / 2, sy < ch / 2)      # dock right if the corner is left, bottom if it is in the top

        def rect(right, bottom):
            x0 = cw - 8 - mw if right else 8
            y0 = ch - 8 - mh if bottom else 8
            return x0, y0, x0 + mw, y0 + mh

        def covers(r):
            return r[0] - 30 <= sx <= r[2] + 30 and r[1] - 30 <= sy <= r[3] + 30

        right, bottom = self.mag_side
        r = rect(right, bottom)
        if covers(r):
            right = not right
            r = rect(right, bottom)
            if covers(r):
                bottom = not bottom
                r = rect(right, bottom)
            self.mag_side = (right, bottom)
        m.place(in_=self.canvas, x=r[0], y=r[1], anchor="nw")

    # keys

    def typing(self, e):
        """True when a text box has the keyboard."""
        return e.widget.winfo_class() in ("Entry", "Spinbox", "TCombobox", "TSpinbox", "Listbox")

    def on_ctrl_key(self, e):
        """Ctrl+N is Skip to Next and Ctrl+B is Back (Ctrl+B is left alone while a text box has the keyboard, where it moves
        the cursor). Every other Ctrl combination goes on to on_key, because Ctrl is the times 100 step for the arrows,
        WASD, plus and minus, so Ctrl+S and Ctrl+D must stay nudges. Ctrl+R has its own binding."""
        k = e.keysym.lower()
        shift = bool(e.state & 0x1)         # the Shift key itself, not Caps Lock
        if k == "n" and not shift:
            self.on_skip()
        elif k == "b" and not shift and not self.typing(e):
            self.on_back()
        else:
            return self.on_key(e)
        return "break"

    def on_alt_key(self, e):
        """The Alt shortcuts. S Save New, A Replace (amend), D Overwrite!, R Rename, B Back, N Skip to Next, M Move, V preview.
        B and D are left alone while a text box has the keyboard, because there they move the cursor or delete a word.
        Any other Alt combination goes on to on_key."""
        k = e.keysym.lower()
        if k == "s":
            self.do_save("new")
        elif k == "a":
            self.do_save("replace_undo")
        elif k == "d" and not self.typing(e):
            self.do_save("replace_perm")
        elif k == "r":
            self.on_rename()
        elif k == "b" and not self.typing(e):
            self.on_back()
        elif k == "n":
            self.on_skip()
        elif k == "m":
            self.on_go()
        elif k == "v":
            self.on_preview()
        else:
            return self.on_key(e)
        return "break"

    def on_ctrl_alt_key(self, e):
        """Ctrl+Shift+Alt+N jumps 100 photos ahead and Ctrl+Shift+Alt+B 100 back. Shift is required so layouts that use
        Ctrl+Alt as AltGr cannot trigger it by accident. Anything else goes on to on_key."""
        k = e.keysym.lower()
        if (e.state & 0x1) and k in ("n", "b"):
            self.go_by(100 if k == "n" else -100)
            return "break"
        return self.on_key(e)

    def on_delete_key(self, e):
        """The Delete key does what the Delete button does, but not while a text box has the keyboard (there it deletes a
        character) and not while a panel covers the picture."""
        if self.typing(e) or self.panel is not None:
            return None
        self.on_delete()
        return "break"

    def on_key(self, e):
        w = self.root.focus_get()
        if w is not None and w.winfo_class() in ("Entry", "Spinbox", "TCombobox", "TSpinbox", "Listbox"):
            return
        k = e.keysym
        ctrl, shift = bool(e.state & 0x4), bool(e.state & 0x1)
        step = 100 if ctrl else 10 if shift else 1
        if k in CORNER_KEYS:
            self.select(CORNER_KEYS[k])
        elif k == "0":
            self.propose_zero()
        elif k == "5":
            self.propose_inset()
        elif k in ("g", "G"):
            self.cycle_grid(-1 if shift else 1)
        elif k in ("KP_Add", "plus", "equal"):
            self.grow_all(step)
        elif k in ("KP_Subtract", "minus", "underscore"):
            self.grow_all(-step)
        elif k in ARROWS or k.lower() in WASD:
            dx, dy = ARROWS[k] if k in ARROWS else WASD[k.lower()]
            if self.selected is None:
                self.say("Pick a corner first with the keys 1 to 4, or click one.")
                return
            p = self.corners[self.selected]
            self.corners[self.selected] = [p[0] + dx * step, p[1] + dy * step]
            self.after_edit()

    def grow_all(self, amount):
        """Move all four sides outward (positive) or inward (negative) by amount image pixels, each measured at a right
        angle to its side, so a tilted shape keeps its shape. Bends keep their place along the side and their size."""
        c = np.asarray(self.corners, dtype=np.float64)
        centre = c.mean(axis=0)
        sides = []
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            d = c[b] - c[a]
            length = float(np.hypot(d[0], d[1]))
            if length < 1e-9:
                return
            nrm = np.array([d[1], -d[0]]) / length
            if np.dot(nrm, (c[a] + c[b]) / 2.0 - centre) < 0:
                nrm = -nrm
            sides.append((c[a] + nrm * amount, d))      # a point on the moved side, and the side's direction
        new = np.zeros((4, 2))
        for k in range(4):
            p1, d1 = sides[(k - 1) % 4]       # the side that ends at corner k
            p2, d2 = sides[k]                 # the side that starts at corner k
            det = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(det) < 1e-9:
                self.say("Two sides are parallel at a corner, so they cannot be moved together.")
                return
            t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / det
            new[k] = p1 + d1 * t
        new = np.round(new)
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            if np.dot(new[b] - new[a], c[b] - c[a]) <= 0:
                self.say("It cannot shrink any further.")
                return
        self.corners = new
        self.after_edit()

    # mouse

    def hit(self, e):
        """What is under the pointer: a purple dot, a corner, or a side line. Dots win ties, then corners."""
        best, best_d = None, self.HIT
        for kind, key, x, y in self.targets:
            d = ((e.x - x) ** 2 + (e.y - y) ** 2) ** 0.5
            if d < best_d or (d <= best_d and kind == "bend" and (best is None or best[0] != "bend")):
                best, best_d = (kind, key), d
        if best is not None:
            return best
        for side in SIDES:
            pts = [self.canvas.to_canvas(p) for p in side_points(self.corners, side, self.bends[side], 40)]
            for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
                if segment_distance(e.x, e.y, ax, ay, bx, by) <= LINE_HIT:
                    return ("line", side)
        return None

    def on_down(self, e):
        self.canvas.focus_set()      # keys 1 to 4, 0, 5 and the arrows go to the picture, not to a box clicked earlier
        self.press, self.moved, self.drag = (e.x, e.y), False, None
        h = self.hit(e)
        if h is None:
            self.drag = ("blank",)
            self.stroke = [(e.x, e.y)]
            if not self.canvas.fit_mode:
                self.canvas.pan_start(e)
            return
        kind, key = h
        if kind == "bend":
            self.drag = ("bend", key)
        elif kind == "corner":
            self.select(key)
            self.drag = ("corner", key)
        else:
            i, j = SIDE_ENDS[key]
            self.drag = ("line", key, self.canvas.to_image(e.x, e.y), self.corners[i].copy(), self.corners[j].copy())

    def on_motion(self, e):
        if self.press is None or self.drag is None:
            return
        if not self.moved:
            if abs(e.x - self.press[0]) + abs(e.y - self.press[1]) <= self.SLOP:
                return
            self.moved = True
        kind = self.drag[0]
        if kind == "blank":
            if self.canvas.fit_mode:
                self.stroke.append((e.x, e.y))
                self.draw_stroke()
            else:
                self.canvas.pan_move(e)
        elif kind == "bend":
            self.bends[self.drag[1]] = bend_from_point(self.corners, self.drag[1], self.canvas.to_image(e.x, e.y))
            self.redraw_overlay()
        elif kind == "corner":
            p = self.canvas.to_image(e.x, e.y)
            self.corners[self.drag[1]] = [round(p[0]), round(p[1])]
            self.after_edit()
        elif kind == "line":
            _, side, start, c0, c1 = self.drag
            d = self.canvas.to_image(e.x, e.y) - start
            if not (e.state & 0x1):                      # locked to the screen axis unless Shift is held
                if side in ("left", "right"):
                    d[1] = 0.0
                else:
                    d[0] = 0.0
            i, j = SIDE_ENDS[side]
            self.corners[i], self.corners[j] = np.round(c0 + d), np.round(c1 + d)
            self.after_edit()

    def on_up(self, e):
        d, moved = self.drag, self.moved
        self.drag, self.press = None, None
        self.canvas.pan_end()
        self.canvas.delete("stroke")
        if d is None or d[0] != "blank":
            return
        if not moved:
            self.deselect()
        elif self.canvas.fit_mode:
            self.finish_stroke()
        self.stroke = []

    def on_right(self, e):
        h = self.hit(e)
        if h is not None and h[0] == "bend":
            self.bends[h[1]] = (0.5, 0.0)
            self.redraw_overlay()

    # drawing a rectangle or a Z to start (only while the whole photo is in view)

    def draw_stroke(self):
        self.canvas.delete("stroke")
        flat = [v for p in self.stroke for v in p]
        if len(flat) >= 4:
            self.canvas.create_line(*flat, fill="#ff9500", width=3, tags="stroke")

    def finish_stroke(self):
        q = recognize_stroke(self.stroke)
        H, W = self.img.shape[:2]
        if q is not None:
            pts = []
            for x, y in q:
                p = self.canvas.to_image(x, y)
                pts.append([min(max(round(p[0]), 0), W - 1), min(max(round(p[1]), 0), H - 1)])
            quad = fix_dangling(np.array(pts, dtype=np.float64), W, H)
            if cv2.contourArea(quad.astype(np.float32)) < 0.01 * W * H:
                q = None
        if q is None:
            self.say("Not recognized. Draw a rectangle (one closed loop), a Z, or a straight slash from corner to corner.")
            return
        step = max(1, len(self.stroke) // 200)
        stroke_img = [tuple(self.canvas.to_image(x, y)) for x, y in self.stroke[::step]]
        self.propose(quad, GHOST_PROMPT, stroke=stroke_img)
        self.say("Straight sides only: applying clears any bends.")

    # proposals: a ghost outline with Apply and Cancel. Gestures, Zero, 5% and Reset all use it.

    def propose(self, quad, text, stroke=None, action=None):
        self.ghost = {"quad": np.array(quad, dtype=np.float64), "stroke": stroke, "action": action}
        if not self.settings["confirm_actions"]:
            self.apply_ghost()
            return
        self.show_ghost_bar(text)
        self.redraw_overlay()

    def propose_zero(self):
        H, W = self.img.shape[:2]
        self.propose(borderCorners_array(W, H), "Set all four corners to the image border?  Sides become straight.")

    def propose_inset(self):
        H, W = self.img.shape[:2]
        self.propose(inset_corners(W, H), "Set all four corners 5% in from the image border?  Sides become straight.")

    def propose_reset(self):
        self.say("Finding corners again...")
        self.root.update_idletasks()
        if not self.settings["confirm_actions"]:
            self.reset_current()
            self.after_edit()
            return
        self.propose(np.round(np.array(initial_corners(self.img), dtype=np.float64)),
                     "Start this file over and detect the corners again?  Rotate, mirror and BW/WB are cleared too.",
                     action=self.reset_current)

    def reset_current(self):
        self.corners = np.round(np.array(initial_corners(self.img), dtype=np.float64))
        self.bends = {s: (0.5, 0.0) for s in SIDES}
        self.rot = 0
        self.mirror.set(False)
        self.bw.set(False)
        self.rot_btn.config(text="Rotate CCW: 0")
        self.trace = None
        self.deselect()

    def show_ghost_bar(self, text):
        if self.ghost_bar is None:
            self.ghost_bar = tk.Frame(self.root, bd=2, relief="ridge")
            self.ghost_label = tk.Label(self.ghost_bar, font=("TkDefaultFont", 10, "bold"), justify="left")
            self.ghost_label.pack(side="left", padx=8, pady=4)
            tk.Button(self.ghost_bar, text="Apply", width=8, command=self.apply_ghost).pack(side="left", padx=2, pady=4)
            tk.Button(self.ghost_bar, text="Cancel", width=8, command=self.cancel_ghost).pack(side="left", padx=(2, 8), pady=4)
        self.ghost_label.config(text=text)
        self.ghost_bar.place(in_=self.canvas, relx=0.5, rely=1.0, y=-14, anchor="s")

    def hide_ghost_bar(self):
        if self.ghost_bar is not None:
            self.ghost_bar.place_forget()

    def apply_ghost(self):
        g = self.ghost
        if g is None:
            return
        self.ghost = None
        self.hide_ghost_bar()
        if g["action"] is not None:
            g["action"]()
            self.after_edit()
            return
        self.corners = np.array(g["quad"], dtype=np.float64)
        self.bends = {s: (0.5, 0.0) for s in SIDES}
        self.trace = (g["stroke"], self.corners.copy()) if g["stroke"] else None
        self.after_edit()

    def cancel_ghost(self):
        self.ghost = None
        self.hide_ghost_bar()
        self.redraw_overlay()

    # panels, recents and keys

    def open_expanded(self, i):
        self.close_panel()
        self.panel = CornerEditor(self, i)

    def open_settings(self):
        self.close_panel()
        self.panel = SettingsPanel(self)

    def close_panel(self):
        if self.panel is not None:
            try:
                self.panel.destroy()
            except tk.TclError:
                pass
            self.panel = None
            self.preview_btn.config(text="PREVIEW", relief="raised")
            self.redraw_overlay()
            if self.selected is not None and self.mag is not None:
                self.mag.set_vars()
                self.mag.render()

    def refresh_recents(self):
        W, H = self.img.shape[1], self.img.shape[0]
        entries = list(self.settings["recents"])
        entries.sort(key=lambda e: 0 if list(e.get("size", [])) == [W, H] else 1)      # photos of the same size first
        self.recents_entries = entries
        self.recents_box.delete(0, "end")
        for e in entries:
            c = e["c"]
            self.recents_box.insert("end", "%dx%d  %d,%d to %d,%d" % (e["size"][0], e["size"][1], c[0], c[1], c[4], c[5]))

    def pick_recent(self, event):
        i = self.recents_box.nearest(event.y)
        if 0 <= i < len(self.recents_entries):
            self.apply_recent(self.recents_entries[i])
            self.canvas.focus_set()

    def sync_recents_visibility(self):
        if self.settings["show_recents"]:
            self.recents_frame.pack(side="right", fill="y", before=self.canvas)
        else:
            self.recents_frame.pack_forget()

    def apply_recent(self, entry):
        c = entry["c"]
        self.corners = np.array([[c[0], c[1]], [c[2], c[3]], [c[4], c[5]], [c[6], c[7]]], dtype=np.float64)
        self.bends = {s: (0.5, 0.0) for s in SIDES}
        self.after_edit()

    def add_recent(self):
        c = [int(round(v)) for p in self.corners for v in p]
        recents = [e for e in self.settings["recents"] if e["c"] != c]
        recents.insert(0, {"c": c, "size": [int(self.img.shape[1]), int(self.img.shape[0])]})
        self.settings["recents"] = recents[:RECENTS_MAX]
        save_settings(self.settings)
        self.refresh_recents()

    def on_escape(self):
        if self.panel is not None:
            self.close_panel()
        elif self.ghost is not None:
            self.cancel_ghost()
        elif self.selected is not None:
            self.deselect()

    def rotate(self):
        self.rot = (self.rot + 90) % 360
        self.rot_btn.config(text="Rotate CCW: %d" % self.rot)

    def busy(self, on):
        self.root.config(cursor="watch" if on else "")
        self.root.update_idletasks()

    def on_preview(self):
        if isinstance(self.panel, PreviewPanel):          # the button is a toggle: a second click hides the preview
            self.close_panel()
            return
        self.busy(True)
        try:
            out = render_preview(self.img, self.corners, self.bends, self.crop.get(), max_px=2000, fill=self.settings.get("fill_mode", "reflect"))
            out = apply_output_options(out, self.rot, self.mirror.get(), self.bw.get())
        except (MemoryError, ValueError, cv2.error) as ex:
            self.busy(False)
            messagebox.showerror("Preview failed", "Could not make the preview: %s" % ex)
            return
        self.busy(False)
        if isinstance(self.panel, PreviewPanel):
            self.panel.update_image(out)
        else:
            self.close_panel()
            self.panel = PreviewPanel(self, out)
        self.preview_btn.config(text="HIDE", relief="sunken")

    # saving

    def set_name(self, text):
        """Put a name in the box. Whatever the program puts there is the baseline, and only a difference from it counts as typing."""
        self.new_name.set(text)
        self.name_baseline = text
        self.update_overwrite_state()

    def update_overwrite_state(self):
        """Overwrite! is available only while the box still holds the name the program put there. Typing a different
        name turns it off, and typing that name back turns it on again. It is always off for a HEIC photo, so the
        original (which cannot be saved again as HEIC) is never deleted."""
        btn = getattr(self, "overwrite_btn", None)
        if btn is not None:
            on = self.new_name.get() == self.name_baseline and not is_heic(getattr(self, "path", ""))
            btn.config(state="normal" if on else "disabled")

    def refresh_name(self):
        """The box starts at the original's name, with any ~nn numbers folded together (see folded_name). All three save
        buttons read it: Save New adds a number when the name is taken, and Replace and Overwrite! give the result that name."""
        self.set_name(folded_name(self.path, self.settings["naming_mode"]))

    def typed_name(self):
        """The new file name from the box, with an extension added if it has none. None if it is unusable."""
        t = os.path.basename(self.new_name.get().strip())
        if not t or any(ch in t for ch in '<>:"|?*'):
            messagebox.showerror("New name", "Please give the new file a name without any of these characters:  < > : \" | ? *")
            return None
        if os.path.splitext(t)[1].lower() not in (".jpg", ".jpeg", ".png", ".bmp"):
            t += output_ext(self.path)
        return t

    def ask_existing(self, name):
        """The file exists. Returns 'overwrite', 'number' (save as the next free name) or 'cancel'."""
        win = tk.Toplevel(self.root)
        win.title("File exists")
        win.transient(self.root)
        result = {"v": "cancel"}

        def choose(v):
            result["v"] = v
            win.destroy()

        tk.Label(win, text="%s already exists." % name, padx=24, pady=16).pack()
        row = tk.Frame(win)
        row.pack(padx=20, pady=(0, 16))
        for label, v in (("Overwrite", "overwrite"), ("Add a number", "number"), ("Cancel", "cancel")):
            tk.Button(row, text=label, width=13, command=lambda v=v: choose(v)).pack(side="left", padx=4)
        win.protocol("WM_DELETE_WINDOW", win.destroy)
        self.center_over_root(win)
        try:
            win.grab_set()
        except tk.TclError:
            pass
        self.root.wait_window(win)
        return result["v"]

    def confirm_permanent(self, message):
        """Overwrite! with no undo. Returns (go ahead, do not ask again this session)."""
        win = tk.Toplevel(self.root)
        win.title("Overwrite with no undo")
        win.transient(self.root)
        result = {"ok": False}
        dont = tk.BooleanVar(value=False)

        def choose(ok):
            result["ok"] = ok
            win.destroy()

        tk.Label(win, text=message + "\n\nThis cannot be undone.", padx=24, pady=16).pack()
        tk.Checkbutton(win, text="Do not ask again (Settings can turn this back on)", variable=dont).pack(padx=20)
        row = tk.Frame(win)
        row.pack(padx=20, pady=16)
        tk.Button(row, text="Overwrite!", width=13, command=lambda: choose(True)).pack(side="left", padx=4)
        tk.Button(row, text="Cancel", width=13, command=lambda: choose(False)).pack(side="left", padx=4)
        win.protocol("WM_DELETE_WINDOW", win.destroy)
        self.center_over_root(win)
        try:
            win.grab_set()
        except tk.TclError:
            pass
        self.root.wait_window(win)
        return result["ok"], bool(dont.get())

    def center_over_root(self, win):
        win.update_idletasks()
        r = self.root
        win.geometry("+%d+%d" % (r.winfo_rootx() + (r.winfo_width() - win.winfo_width()) // 2,
                                 r.winfo_rooty() + (r.winfo_height() - win.winfo_height()) // 3))

    def effective(self, key, reg_name):
        """The larger of the settings file's number and the registry's number. None if the registry cannot be read."""
        r = reg_get(reg_name)
        if r is None:
            return None
        return max(as_int(self.settings.get(key)), r)

    def first_run_check(self):
        """Show the help once and only once. Both places are written and read back before it is shown, and if either
        cannot be confirmed it is not shown at all. F1 always works."""
        shown = self.effective("help_shown", "help")
        if shown is None or shown:
            return
        self.settings["help_shown"] = True
        save_settings(self.settings)
        if not (settings_file_has("help_shown", True) and reg_set("help", 1)):
            return
        self.first_run_session = True
        self.show_help()

    def count_operation(self):
        """Called after every save, rename, delete and DBG picture that worked."""
        cur = self.effective("ops_count", "ops")
        n = (cur if cur is not None else as_int(self.settings.get("ops_count"))) + 1
        self.settings["ops_count"] = n
        save_settings(self.settings)
        reg_set("ops", n)
        self.root.after(300, lambda: self.maybe_coffee(n))

    def maybe_coffee(self, n):
        s = self.settings
        if s.get("coffee_paid") or self.first_run_session or self.help_win is not None or self.coffee_win is not None:
            return
        m = coffee_milestone(n)
        shown = self.effective("coffee_shown", "coffee")
        if shown is None or m <= shown:
            return
        s["coffee_shown"] = m
        save_settings(s)
        if not (settings_file_has("coffee_shown", m) and reg_set("coffee", m)):
            return
        self.show_coffee(n)

    def show_coffee(self, n):
        """The coffee nag. Modal. Its checkbox is the honor system and stops the nags for good."""
        if self.coffee_win is not None:
            return
        win = tk.Toplevel(self.root)
        win.title("Buy me a coffee?")
        win.transient(self.root)
        self.coffee_win = win
        tk.Label(win, text="Buy me a coffee?", font=("TkDefaultFont", 13, "bold")).pack(padx=26, pady=(16, 4))
        tk.Label(win, text="Flyerize_gui has now done %d jobs for you.  If it has saved you time, a $5 coffee would be "
                           "very welcome." % n, wraplength=380, justify="left").pack(padx=26, pady=(0, 8))
        try:
            self.coffee_img = tk.PhotoImage(data=QR_PNG)
        except tk.TclError:
            self.coffee_img = None
        if self.coffee_img is not None:
            tk.Label(win, text="Scan with your phone:").pack()
            tk.Label(win, image=self.coffee_img, bd=0).pack(pady=4)
        link = tk.Label(win, text="Click here to open PayPal in your browser", fg="#0645ad", cursor="hand2",
                        font=("TkDefaultFont", 10, "underline"))
        link.pack(pady=(0, 8))
        link.bind("<Button-1>", lambda e: webbrowser.open(DONATE_URL))
        paid = tk.BooleanVar(value=False)
        tk.Checkbutton(win, text="I sent one, so stop asking.", variable=paid).pack(pady=(0, 6))

        def close(e=None):
            if paid.get():
                self.settings["coffee_paid"] = True
                save_settings(self.settings)
            self.coffee_win = None
            win.destroy()

        btn = tk.Button(win, text="Close", width=13, command=close)
        btn.pack(pady=(0, 16))
        btn.focus_set()
        win.bind("<Escape>", close)
        win.bind("<Return>", close)
        win.protocol("WM_DELETE_WINDOW", close)
        self.center_over_root(win)
        try:
            win.grab_set()
        except tk.TclError:
            pass
        self.root.wait_window(win)

    def show_help(self):
        """The Help panel (F1). Modal, so it waits until closed. Escape, Return or Close all close it."""
        if self.help_win is not None:
            return
        win = tk.Toplevel(self.root)
        win.title("Flyerize_gui Help")
        win.transient(self.root)
        self.help_win = win
        txt = tk.Text(win, width=72, height=18, wrap="word", relief="flat", padx=22, pady=16, cursor="arrow",
                      bg=win.cget("bg"), spacing3=10)
        txt.pack(fill="both", expand=True)
        txt.tag_configure("link", foreground="#0645ad", underline=True)
        txt.tag_bind("link", "<Button-1>", lambda e: webbrowser.open(DISCUSSIONS_URL))
        txt.tag_bind("link", "<Enter>", lambda e: txt.config(cursor="hand2"))
        txt.tag_bind("link", "<Leave>", lambda e: txt.config(cursor="arrow"))
        for i, para in enumerate(HELP_TEXT):
            pos = para.find(DISCUSSIONS_URL)
            if pos < 0:
                txt.insert("end", para)
            else:
                txt.insert("end", para[:pos])
                txt.insert("end", DISCUSSIONS_URL, "link")
                txt.insert("end", para[pos + len(DISCUSSIONS_URL):])
            if i < len(HELP_TEXT) - 1:
                txt.insert("end", "\n")
        txt.config(state="disabled")

        def close(e=None):
            self.help_win = None
            win.destroy()

        btn = tk.Button(win, text="Close", width=13, command=close)
        btn.pack(pady=(0, 16))
        btn.focus_set()
        win.bind("<Escape>", close)
        win.bind("<Return>", close)
        win.protocol("WM_DELETE_WINDOW", close)
        self.center_over_root(win)
        try:
            win.grab_set()
        except tk.TclError:
            pass
        self.root.wait_window(win)

    def plan_save(self, mode):
        """Work out which files to write. mode is new, replace_undo or replace_perm. Returns a dict with crop,
        backup (a file to move aside first) and remove (a file to delete first), or None if cancelled.
        The box names the file that gets the result. Save New adds a number when that name is taken. Replace and
        Overwrite! write exactly that name: a file already there is backed up (Replace) or overwritten (Overwrite!),
        and when the name is free, the original is backed up (Replace) or removed (Overwrite!) instead."""
        s = self.settings
        naming = s["naming_mode"]
        typed = self.typed_name()
        if typed is None:
            return None
        target = os.path.join(os.path.dirname(self.path), typed)
        if mode in ("replace_undo", "replace_perm"):
            original = self.path if os.path.exists(self.path) else None
            backup = remove = None
            if os.path.exists(target):
                if mode == "replace_undo":
                    backup = target
            elif original is not None:
                if mode == "replace_undo":
                    backup = original
                else:
                    remove = original
            if mode == "replace_perm" and s["confirm_overwrite"]:
                if os.path.exists(target):
                    message = "%s will be overwritten by the result." % os.path.basename(target)
                elif remove is not None:
                    message = "%s will be deleted and the result saved as %s." % (os.path.basename(remove), os.path.basename(target))
                else:
                    message = None
                if message is not None:
                    ok, dont = self.confirm_permanent(message)
                    if not ok:
                        return None
                    if dont:
                        s["confirm_overwrite"] = False
                        save_settings(s)
            return {"crop": target, "backup": backup, "remove": remove}
        stem_here = os.path.splitext(typed)[0]
        number_mode = "hds7" if (naming == "hds7" and HDS7_NAME.match(stem_here)) else "standard"
        cands = list(new_file_candidates(target, number_mode, self.photo_when))

        def taken(c):
            return os.path.exists(c)

        if taken(target):
            free = next((c for c in cands if not taken(c)), None)
            if free is None:
                messagebox.showerror("No free name", "Every numbered name is taken. Rename or move some of the saved files "
                                     "outside Flyerize_gui, or copy the original and start again.")
                return None
            target = free
        return {"crop": target, "backup": None, "remove": None}

    def on_generate(self, mode="new"):
        """Save. Returns True if saved, False if cancelled or it failed."""
        plan = self.plan_save(mode)
        if plan is None:
            self.say("Not saved.")
            return False
        s = self.settings
        times = None
        try:
            st = os.stat(self.path)
            times = (st.st_atime, st.st_mtime)
        except OSError:
            pass
        crop = plan["crop"]
        tmp = os.path.join(os.path.dirname(crop), ".flyerize_gui_tmp_" + os.path.basename(crop))
        self.busy(True)
        try:
            out = apply_output_options(render(self.img, self.corners, self.bends, self.crop.get(), fill=self.settings.get("fill_mode", "reflect")), self.rot,
                                       self.mirror.get(), self.bw.get())
            write_image(out, self.pil, tmp, s["jpeg_quality"], s["no_subsampling"], times)   # written first, so a failure loses nothing
            note = ""
            if plan["backup"] is not None:
                where = make_undo_copy(plan["backup"], s["undo_method"])
                log_event("BACKUP", plan["backup"], "(Recycle Bin)" if where == "the Recycle Bin" else where)
                note = "\nBacked up: %s" % (where if where == "the Recycle Bin" else os.path.relpath(where, os.path.dirname(crop)))
            elif plan["remove"] is not None:
                os.remove(plan["remove"])
                log_event("REMOVE", plan["remove"])
            os.replace(tmp, crop)
        except MemoryError:
            self.cleanup(tmp)
            self.busy(False)
            messagebox.showerror("Too large", "The output is too large to build in memory.")
            return False
        except Exception as ex:
            self.cleanup(tmp)
            self.busy(False)
            messagebox.showerror("Could not save", str(ex))
            return False
        self.busy(False)
        self.last_written = crop
        self.saved = self.snapshot()
        self.add_recent()
        self.say("Saved to: %s\n%s  (%d x %d)%s" % (os.path.dirname(os.path.abspath(crop)), os.path.basename(crop), out.shape[1], out.shape[0], note))
        self.set_name(os.path.basename(crop))
        self.note_result(mode, crop)
        log_event({"new": "SAVE_NEW", "replace_undo": "REPLACE", "replace_perm": "OVERWRITE"}.get(mode, mode.upper()), self.path, crop)
        self.count_operation()
        return True

    def on_dbg(self):
        """Write the outline picture (the original photo with the lines drawn on it) as name~dbg.jpg beside the photo.
        There is only ever one per photo: pressing again simply overwrites it, with no backup. It is not a save: no
        result is written, and the unsaved-changes state is left alone."""
        s = self.settings
        target = os.path.splitext(self.path)[0] + "~dbg.jpg"
        times = None
        try:
            st = os.stat(self.path)
            times = (st.st_atime, st.st_mtime)
        except OSError:
            pass
        self.busy(True)
        try:
            arr = outline_image(self.img, self.corners, self.bends, self.trace_for_outline(), GRID_MODES[self.grid_mode][1])
            write_image(arr, self.pil, target, s["jpeg_quality"], s["no_subsampling"], times)
        except MemoryError:
            self.cleanup(target)
            self.busy(False)
            messagebox.showerror("Too large", "The picture is too large to build in memory.")
            return
        except Exception as ex:
            self.cleanup(target)
            self.busy(False)
            messagebox.showerror("Could not save", str(ex))
            return
        self.busy(False)
        self.last_outline = target
        self.say("Saved to: %s\n%s  (%d x %d)" % (os.path.dirname(os.path.abspath(target)), os.path.basename(target), arr.shape[1], arr.shape[0]))
        log_event("DBG", self.path, target)
        self.count_operation()

    def note_result(self, mode, crop):
        """Keep the file list in step with what was written. Save New adds the new file right after this photo (and after
        the results already added for it), where only Previous and Go nnn land. If this photo's own file has moved away
        (Replace or Overwrite! under a new name), its entry follows the result."""
        if mode == "new":
            self.paths.insert(self.index + 1 + self.added, crop)
            self.added += 1
            self.result_entries.add(os.path.normcase(os.path.abspath(crop)))
        if not os.path.exists(self.paths[self.index]):
            self.paths[self.index] = crop
        self.set_title()

    @staticmethod
    def cleanup(path):
        try:
            os.remove(path)
        except OSError:
            pass

    def trace_for_outline(self):
        if self.trace is not None and np.array_equal(self.trace[1], self.corners):
            return self.trace[0]
        return None

    def do_save(self, mode):
        """A save button was pressed. With Auto on, a successful save moves on to the next photo."""
        if mode == "replace_perm" and is_heic(self.path):
            self.say("Overwrite! is off for HEIC photos, so the original is never deleted.  Use Save New or Replace.")
            return
        if mode == "replace_perm" and self.new_name.get() != self.name_baseline:
            self.say("Overwrite! is off while the name box has been edited.  Retype the original name, or use Save New or Replace.")
            return
        originals = sum(1 for j in range(len(self.paths)) if not self.is_result(j))
        was_last = originals > 10 and not self.finish_shown and not self.is_result(self.index) and self.next_index() is None
        ok = self.on_generate(mode)
        if ok and self.auto.get() and self.next_index() is not None:
            self.next_file()
        elif ok and was_last:
            self.finish_shown = True
            self.root.after(200, lambda: self.show_finished(originals))

    def show_finished(self, originals):
        """The last photo of a long list was just saved. Congratulate, and offer another folder."""
        win = tk.Toplevel(self.root)
        win.title("All done")
        win.transient(self.root)
        result = {"v": "stay"}

        def choose(v):
            result["v"] = v
            win.destroy()

        tk.Label(win, text="That was the last of the %d photos.  Nicely done." % originals, padx=28, pady=18).pack()
        row = tk.Frame(win)
        row.pack(padx=20, pady=(0, 16))
        for label, v in (("Choose another folder", "folder"), ("Stay right here", "stay"), ("Exit", "exit")):
            tk.Button(row, text=label, width=20 if v == "folder" else 14, command=lambda v=v: choose(v)).pack(side="left", padx=4)
        win.protocol("WM_DELETE_WINDOW", lambda: choose("stay"))
        win.bind("<Escape>", lambda e: choose("stay"))
        self.center_over_root(win)
        try:
            win.grab_set()
        except tk.TclError:
            pass
        self.root.wait_window(win)
        if result["v"] == "folder":
            self.choose_folder()
        elif result["v"] == "exit":
            self.on_exit()

    def choose_folder(self):
        """Replace the list with the images in a folder the user picks."""
        if not self.leave_ok():
            return
        here = os.path.dirname(os.path.abspath(self.path))
        folder = filedialog.askdirectory(parent=self.root, title="Choose a folder of photos", initialdir=os.path.dirname(here) or here)
        if not folder:
            return
        folder = os.path.normpath(folder)
        paths = collect_paths([folder])
        if not paths:
            messagebox.showerror("Not found", "No images found in: %s" % folder)
            return
        self.paths = paths
        self.result_entries = set()
        self.finish_shown = False
        self.load(0)

    def on_auto(self):
        self.settings["auto_advance"] = bool(self.auto.get())
        save_settings(self.settings)
        self.update_auto_look()
        self.canvas.focus_set()

    def update_auto_look(self):
        """While Auto is on, the save buttons it affects wear an arrow and a pale green fill. The buttons that move
        you around keep their normal look, because they stay fully valid."""
        on = bool(self.auto.get()) and len(self.paths) > 1
        for btn, label in ((self.save_btn, "Save New"), (self.replace_btn, "Replace"),
                           (self.overwrite_btn, "Overwrite!"), (self.rename_btn, "Rename")):
            btn.config(text=label + " \u2192" if on else label, bg=AUTO_FILL if on else self.btn_bg, fg="black" if on else self.btn_fg)

    def on_rename(self):
        """Rename this photo's file to the name in the box without rewriting the picture. The file keeps its own
        extension. A name that is taken gets a number, as everywhere else, so no file is ever overwritten."""
        typed = self.typed_name()
        if typed is None:
            return
        old = self.paths[self.index]
        if not os.path.exists(old):
            messagebox.showerror("Rename", "%s is not there any more." % os.path.basename(old))
            return
        ext = os.path.splitext(old)[1]
        stem = os.path.splitext(typed)[0]
        target = os.path.join(os.path.dirname(old), stem + ext)
        if target == old:
            self.say("That is already this file's name.")
            return
        if os.path.exists(target) and os.path.normcase(os.path.abspath(target)) != os.path.normcase(os.path.abspath(old)):
            naming = self.settings["naming_mode"]
            number_mode = "hds7" if (naming == "hds7" and HDS7_NAME.match(stem)) else "standard"
            target = next((c for c in new_file_candidates(target, number_mode, self.photo_when, ext) if not os.path.exists(c)), None)
            if target is None:
                messagebox.showerror("No free name", "Every numbered name is taken. Rename or move some of the files outside Flyerize_gui.")
                return
        try:
            os.rename(old, target)
        except OSError as ex:
            messagebox.showerror("Could not rename", str(ex))
            return
        log_event("RENAME", old, target)
        key_old = os.path.normcase(os.path.abspath(old))
        if key_old in self.result_entries:
            self.result_entries.discard(key_old)
            self.result_entries.add(os.path.normcase(os.path.abspath(target)))
        self.paths[self.index] = target
        self.path = target
        self.set_name(os.path.basename(target))
        self.set_title()
        self.say("Renamed to: %s\nThe picture itself was not rewritten." % os.path.basename(target))
        self.count_operation()
        if self.auto.get() and self.next_index() is not None:
            self.on_skip()

    def on_delete(self):
        """Move this photo aside the way Replace backs up an original, take it out of the list and go on to the next.
        Nothing is asked."""
        target = self.paths[self.index]
        name = os.path.basename(target)
        where = None
        try:
            if os.path.exists(target):
                where = make_undo_copy(target, self.settings["undo_method"])
        except OSError as ex:
            messagebox.showerror("Could not delete", str(ex))
            return
        if where is not None:
            log_event("DELETE", target, "(Recycle Bin)" if where == "the Recycle Bin" else where)
            self.count_operation()
        del self.paths[self.index]
        self.result_entries.discard(os.path.normcase(os.path.abspath(target)))
        if not self.paths:
            messagebox.showinfo("Flyerize_gui", "%s was the last photo in the list. Flyerize_gui will close." % name)
            self.saved = self.snapshot()      # nothing to ask about on the way out
            self.on_exit()
            return
        j = self.index
        while j < len(self.paths) and self.is_result(j):
            j += 1
        self.load(j if j < len(self.paths) else len(self.paths) - 1)
        self.say("Deleted: %s\nMoved to: %s" % (name, "nowhere (it was already gone)" if where is None else
                                                  where if where == "the Recycle Bin" else os.path.basename(where)))

    def leave_ok(self):
        """Called before leaving a photo (Next, Previous, Go nnn, Exit). True if it is fine to go on. Unsaved changes are the
        corners (including the ones offered when the photo opened, because the straightening only exists once saved) and
        a file name typed in the box that no save or rename has used.
        With the confirm setting on, ask. With it off, keep the corners in the recents list and go on."""
        corners_changed = self.snapshot() != self.saved
        name_changed = self.new_name.get() != self.name_baseline
        if not corners_changed and not name_changed:
            return True
        if self.settings["confirm_actions"]:
            if corners_changed:
                answer = messagebox.askyesnocancel("Save changes?",
                                                   "The straightened result has not been saved.\n\nSave it first?")
                if answer is None:
                    return False
                if answer and not self.on_generate():
                    return False
                return True
            return messagebox.askokcancel("Unused name", "You typed a new file name that has not been used.\n\nLeave this photo anyway?")
        if corners_changed:
            self.add_recent()
        return True

    def on_skip(self):
        if self.leave_ok():
            self.next_file()

    def on_exit(self):
        if not self.leave_ok():
            return
        try:
            self.root.after_cancel(self.poll_id)
        except Exception:
            pass
        clear_lock()
        self.root.destroy()


def borderCorners_array(W, H):
    return np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], dtype=np.float64)


def main():
    args = sys.argv[1:]
    if args and running_instance():
        forward_to_running([os.path.abspath(a) for a in args])      # a window is open: add these to its queue and leave
        log_note("HANDOFF", VERSION, run_kind(), "items=%d" % len(args), "queue=" + os.path.abspath(queue_file()))
        return
    root = tk.Tk()
    if not args:
        root.withdraw()
        path = filedialog.askopenfilename(title="Choose a photo or scan", filetypes=IMAGE_TYPES)
        root.deiconify()
        if not path:
            return
        paths = [path]
    else:
        paths = collect_paths(args)
        if not paths:
            messagebox.showerror("Not found", "No images found in: %s" % " ".join(args))
            return
    try:
        App(root, paths)
    except Exception as ex:
        messagebox.showerror("Could not open", "%s\n\n%s" % (os.path.basename(paths[0]), ex))
        return
    root.mainloop()


if __name__ == "__main__":
    main()
