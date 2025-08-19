# HINWEIS: Dies ist NUR ein Platzhalter, um die Pipeline-Enden zu zeigen.
# Erzeugt eine fake results.json im angegebenen --report Ordner.
# Ersetze dies durch dein echtes NX Journal, das NXOpen nutzt.

import argparse, json, os, time, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    outdir = pathlib.Path(args.report)
    outdir.mkdir(parents=True, exist_ok=True)

    results = {
        "project": "NX Testreport",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files": {}
    }

    # nur beispielhafte Sammlung von .prt Pfaden
    for p in pathlib.Path(args.root).rglob("*.prt"):
        results["files"].setdefault(str(p), [])
        results["files"][str(p)].append({"id":"LAY-001","name":"Layer-Check","status":"PASS","message":"","duration_ms":400})

    # wenn keine .prt gefunden, fülle eine Demo
    if not results["files"]:
        demo = os.path.join(args.root, "demo.prt")
        results["files"][demo] = [
            {"id":"LAY-001","name":"Layer-Check","status":"PASS","message":"","duration_ms":420},
            {"id":"ATT-005","name":"Attribut isBuyPart","status":"FAIL","message":"Attribut fehlt","duration_ms":310}
        ]

    with open(outdir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Fake results.json geschrieben nach", outdir)

if __name__ == "__main__":
    main()