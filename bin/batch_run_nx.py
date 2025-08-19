# -*- coding: utf-8 -*-
"""
NX batch runner that outputs the SAME JSON structure as `list_all_parts.py`:
{
  "project": "...",
  "root": "C:\\...",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "files": {
     "<abs path to .prt>": [
        {"id":"...", "name":"...", "status":"PASS/FAIL/ERROR", "message":"...", "duration_ms": 0}
     ]
  }
}

Runs inside Siemens NX via run_journal.exe.

Fixed locations (adjust if needed):
- Framework src:    C:/nx-quality/bin/framework/src
- Parts root:       C:/BRS-Nextcloud/Workshop_Construction
- Reports base dir: C:/nx-quality/web/data (we write 'latest.json' here)
- Additionally we also write a timestamped copy under C:/nx-quality/reports/<stamp>/prt_checks.json
"""

import sys, os, json, time, datetime, argparse, shutil, traceback
from pathlib import Path

# ---------- FIXED LOCATIONS ----------
FRAMEWORK_SRC = Path("C:/nx-quality/bin/nx-testpipeline/src")
#ROOT_PARTS    = Path("C:/BRS-Nextcloud/Workshop_Construction")
ROOT_PARTS    = Path("C:/nx-quality/bin/nx-testpipeline")
WEB_DATA_DIR  = Path("C:/nx-quality/web/data")
REPORTS_DIR   = Path("C:/nx-quality/reports")

# Ensure import path for the framework
if str(FRAMEWORK_SRC) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_SRC))

# Import framework checks (strict-boolean)
from checks.plane_check import (
    check_datum_planes_on_expected_layer,
    get_all_datum_planes,
    DATUM_PLANES_LAYER_EXPECTED,
)
from checks.sketch_check import (
    check_sketches_on_expected_layer,
    get_all_sketches,
    SKETCH_LAYER_EXPECTED,
)
HAS_HOLES_CHECK = False
try:
    from checks.solidbody_check import (
        check_holes_on_expected_layer,
        HOLE_LAYER_EXPECTED,
    )
    HAS_HOLES_CHECK = True
except Exception:
    HAS_HOLES_CHECK = False

# Buy-part check (prefer popup wrapper if present)
try:
    from checks.buypart_check import validate_buy_part_with_popup as _buy_check
except Exception:
    try:
        from checks.buypart_check import validate_buy_part as _buy_check
    except Exception:
        _buy_check = None

from utils import notify as notify_module

# NXOpen (must be available when run via run_journal.exe)
import NXOpen

def monkeypatch_notify_collector(collected):
    """Replace utils.notify.popup so that messages are appended to `collected` lists."""
    class _Ctx:
        def __enter__(self):
            self._orig = notify_module.popup
            def _collect(title, message, level="info"):
                collected.append({"title": str(title), "message": str(message), "level": str(level)})
            notify_module.popup = _collect
        def __exit__(self, exc_type, exc, tb):
            notify_module.popup = self._orig
    return _Ctx()

def open_part(part_path: Path):
    session = NXOpen.Session.GetSession()
    base_part, part_load_status = session.Parts.OpenActiveDisplay(str(part_path), NXOpen.DisplayPartOption.ReplaceExisting)
    session.Parts.SetWork(base_part)
    try:
        part_load_status.Dispose()
    except Exception:
        pass
    return base_part

def close_work_part():
    try:
        part = NXOpen.Session.GetSession().Parts.Work
        part.Close(NXOpen.BasePartCloseOption.SkipSave, None)
    except Exception:
        pass

def save_work_part_if_modified():
    try:
        part = NXOpen.Session.GetSession().Parts.Work
        if part.IsModified:
            part.Save(NXOpen.BasePartSaveComponents.TrueValue, NXOpen.BasePartCloseAfterSave.FalseValue)
    except Exception:
        pass

def run_check_bool(check_id, name, func_bool, msg_builder=None, *, save_after=False):
    """Run a single check function returning bool.
       If True -> PASS, False -> FAIL. Exceptions -> FAIL with message.
    """
    t0 = time.perf_counter()
    status = "PASS"
    message = ""
    try:
        result = bool(func_bool())
        status = "PASS" if result else "FAIL"
        if msg_builder is not None:
            message = msg_builder(result)
    except Exception as e:
        status = "FAIL"
        message = f"{name} exception: {e}"
    dur_ms = int((time.perf_counter() - t0) * 1000)
    if save_after:
        save_work_part_if_modified()
    return {"id": check_id, "name": name, "status": status, "message": message, "duration_ms": dur_ms}

def checks_for_current_part(run_holes=False, save_changes=False):
    """Execute checks and return a LIST of standardized results dicts."""
    results = []
    collected_msgs = []  # for buy-part popups

    # --- Datum planes ---
    try:
        count_planes = len(get_all_datum_planes())
    except Exception:
        count_planes = None
    def planes_msg(ok: bool):
        prefix = "OK" if ok else "NOT OK"
        if count_planes is None:
            return f"{prefix}: datum planes on layer {DATUM_PLANES_LAYER_EXPECTED} (count unknown)."
        return f"{prefix}: {count_planes} datum planes on layer {DATUM_PLANES_LAYER_EXPECTED} or none present."
    results.append(
        run_check_bool("CHK_PLANE", "Datum planes on expected layer",
                       check_datum_planes_on_expected_layer, planes_msg, save_after=save_changes)
    )

    # --- Sketches ---
    try:
        count_sketches = len(get_all_sketches())
    except Exception:
        count_sketches = None
    def sketches_msg(ok: bool):
        prefix = "OK" if ok else "NOT OK"
        if count_sketches is None:
            return f"{prefix}: sketches on layer {SKETCH_LAYER_EXPECTED} (count unknown)."
        return f"{prefix}: {count_sketches} sketches on layer {SKETCH_LAYER_EXPECTED} or none present."
    results.append(
        run_check_bool("CHK_SKETCH", "Sketches on expected layer",
                       check_sketches_on_expected_layer, sketches_msg, save_after=save_changes)
    )

    # --- Holes (optional) ---
    if run_holes and HAS_HOLES_CHECK:
        def holes_msg(ok: bool):
            return ("OK" if ok else "NOT OK") + f": hole bodies on layer {HOLE_LAYER_EXPECTED} or none present."
        results.append(
            run_check_bool("CHK_HOLES", "Hole bodies on expected layer",
                           check_holes_on_expected_layer, holes_msg, save_after=save_changes)
        )

    # --- Buy-part attribute ---
    if _buy_check is not None:
        with monkeypatch_notify_collector(collected_msgs):
            t0 = time.perf_counter()
            try:
                ok = bool(_buy_check())
                status = "PASS" if ok else "FAIL"
                dur_ms = int((time.perf_counter() - t0) * 1000)
                if collected_msgs:
                    lines = [f"[{m.get('level','info')}] {m.get('title','')}: {m.get('message','')}" for m in collected_msgs]
                    message = " | ".join(lines)
                else:
                    message = "Buy-part check finished."
                results.append({"id":"CHK_BUYPART","name":"Buy-part attribute","status":status,"message":message,"duration_ms":dur_ms})
            except Exception as e:
                results.append({"id":"CHK_BUYPART","name":"Buy-part attribute","status":"FAIL","message":f"Exception: {e}","duration_ms":0})
    else:
        results.append({"id":"CHK_BUYPART","name":"Buy-part attribute","status":"ERROR","message":"Check function not available","duration_ms":0})

    return results

def discover_prt_files(root: Path):
    return sorted(p for p in root.rglob("*.prt"))

def ensure_dirs(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Run NX checks and emit list_all_parts-style JSON.")
    parser.add_argument("-root", dest="root", default=str(ROOT_PARTS), help="Root folder containing .prt files (default is fixed)")
    parser.add_argument("-holes", dest="holes", action="store_true", help="Also run hole-to-layer check")
    parser.add_argument("-save", dest="save", action="store_true", help="Save modified parts after checks")
    parser.add_argument("-project", dest="project", default="Wokshop_Construction-Space", help="Project field in JSON")
    args = parser.parse_args()

    root = Path(args.root)

    prt_files = discover_prt_files(root)
    if not prt_files:
        print("No .prt files found under:", str(root))
        return

    ensure_dirs(WEB_DATA_DIR)
    ensure_dirs(REPORTS_DIR)

    # Build payload
    files_dict = {}
    for prt in prt_files:
        try:
            open_part(prt)
            checks = checks_for_current_part(run_holes=args.holes, save_changes=args.save)
            files_dict[str(prt)] = checks
        except Exception as e:
            # On fatal open/processing error, still emit an error entry for this file
            files_dict[str(prt)] = [{
                "id": "CHK_FATAL",
                "name": "Processing",
                "status": "ERROR",
                "message": f"Failed to process: {e}",
                "duration_ms": 0
            }]
        finally:
            close_work_part()

    payload = {
        "project": args.project,
        "root": str(root),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files": files_dict
    }

    # Write to latest.json in WEB_DATA_DIR
    latest = WEB_DATA_DIR / "latest.json"
    with latest.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Also keep a timestamped copy in reports
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    outdir = REPORTS_DIR / stamp
    ensure_dirs(outdir)
    out_json = outdir / "prt_checks.json"
    shutil.copy2(str(latest), str(out_json))

    print("Wrote:", str(latest))
    print("Backup:", str(out_json))
    print("Files processed:", len(prt_files))

if __name__ == "__main__":
    main()
