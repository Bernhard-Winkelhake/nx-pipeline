import pathlib, json, time, shutil

# Wurzelordner mit allen NX-Parts
ROOT_PARTS = pathlib.Path(r"C:\BRS-Nextcloud\Workshop_Construction")

# Basisstruktur NX Quality
BASE     = pathlib.Path(r"C:\nx-quality")
REPORTS  = BASE / "reports"
WEB_DATA = BASE / "web" / "data"


def main():
    # Sicherstellen, dass Ordner existieren
    REPORTS.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    # Zeitstempel-Ordner im reports-Verzeichnis
    stamp  = time.strftime("%Y-%m-%d_%H-%M-%S")
    outdir = REPORTS / stamp
    outdir.mkdir(parents=True, exist_ok=True)

    # JSON-Struktur für Prüf-Report
    files_dict = {}
    for p in ROOT_PARTS.rglob("*.prt"):
        # Jeder Part bekommt 1 Dummy-Check
        files_dict[str(p)] = [{
            "id": "CHK000",
            "name": "Existenzprüfung",
            "status": "PASS",
            "message": f"Datei {p.name} gefunden.",
            "duration_ms": 0
        }]

    payload = {
        "project": "Wokshop_Construction-Space",
        "root": str(ROOT_PARTS),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files": files_dict
    }

    # Speichern im Zeitstempel-Ordner
    out_json = outdir / "prt_file_list.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    # Zusätzlich: aktuelles latest.json im Web-Ordner überschreiben
    latest_json = WEB_DATA / "latest.json"
    shutil.copy2(out_json, latest_json)

    print(f"{len(files_dict)} .prt-Dateien gefunden und als PASS markiert.")
    print(f"Report:  {out_json}")
    print(f"Latest:  {latest_json}")


if __name__ == "__main__":
    main()
