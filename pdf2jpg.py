# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software, under the GNU General Public License, version 3 or any later version, and comes with no warranty.  See the LICENSE file with Flyerize_gui.
# pdf2jpg.py: write each page of the PDFs it is given as a JPEG next to the PDF.  Needs: pip install pdf2image
# (and Poppler: on Windows a separate download whose bin folder is on the PATH, on Linux apt install poppler-utils).
# A PDF that already has its .jpg files is skipped.  Delete them to convert again (also after a failure partway through).
import re
import sys
from datetime import datetime as dt
from pathlib import Path
from pdf2image import convert_from_path, pdfinfo_from_path

DPI_SHORT, DPI_LONG, SHORT_UP_TO = 600, 300, 9      # documents of more than 9 pages come out at the lower DPI
TIMEOUT = 300                                       # seconds Poppler gets for one page before it is stopped

def log(msg):
    print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def has_jpgs(path):
    pattern = re.compile(re.escape(path.stem) + r"(_p\d+)?\.jpg", re.I)
    return any(pattern.fullmatch(f.name) for f in path.parent.iterdir())

if len(sys.argv) < 2:
    print("Usage: pdf2jpg.py file.pdf [more.pdf ...]")
    sys.exit(1)

attention = False
for arg in sys.argv[1:]:
    path = Path(arg)
    print("")
    if has_jpgs(path):
        log(f"Skipped {path.name}, it already has .jpg files")
        attention = True
        continue
    try:
        count = int(pdfinfo_from_path(path)["Pages"])
        dpi = DPI_SHORT if count <= SHORT_UP_TO else DPI_LONG
        log(f"Reading {path} ({count} pages at {dpi} DPI)")
        for n in range(1, count + 1):
            page = convert_from_path(path, dpi, first_page=n, last_page=n, timeout=TIMEOUT)[0]
            out = path.with_suffix(".jpg") if count == 1 else path.with_name(f"{path.stem}_p{n:0{len(str(count))}d}.jpg")
            page.save(out, "JPEG", quality=95)
            log(f"{out} written")
    except Exception as e:
        log(f"Failed on {path.name}: {e}")
        attention = True
sys.exit(1 if attention else 0)
