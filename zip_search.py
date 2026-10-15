#!/usr/bin/env python3
"""
Durchsucht alle Dateien in einer Zip-Datei (inklusive aller Unterverzeichnisse
und verschachtelter Zip-Dateien) nach einem String und schreibt die Treffer
in eine Textdatei.

Beispiel:
    python zip_search.py archiv.zip "UNH+" -o ergebnisse.txt
    python zip_search.py archiv.zip "fehler" -i
"""

import argparse
import io
import sys
import zipfile
from datetime import datetime

ENCODINGS = ("utf-8", "cp1252", "latin-1")


def decode(data):
    """Bytes mit der ersten passenden Kodierung in Text umwandeln."""
    for enc in ENCODINGS:
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace")


def search_zip(zf, needle, ignore_case, prefix=""):
    """Liefert (Pfad, Zeilennummer, Zeile) für jeden Treffer in der Zip-Datei."""
    cmp_needle = needle.lower() if ignore_case else needle

    for info in zf.infolist():
        if info.is_dir():
            continue
        path = prefix + info.filename
        try:
            data = zf.read(info)
        except (RuntimeError, zipfile.BadZipFile, NotImplementedError) as e:
            # z.B. passwortgeschützte oder beschädigte Einträge
            yield path, None, f"[Datei konnte nicht gelesen werden: {e}]"
            continue

        # Verschachtelte Zip-Dateien rekursiv durchsuchen
        if info.filename.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as inner:
                    yield from search_zip(inner, needle, ignore_case, path + "/")
                continue
            except zipfile.BadZipFile:
                pass  # doch keine gültige Zip-Datei -> als normale Datei durchsuchen

        text = decode(data)
        for lineno, line in enumerate(text.splitlines(), start=1):
            haystack = line.lower() if ignore_case else line
            if cmp_needle in haystack:
                yield path, lineno, line.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Durchsucht alle Dateien einer Zip-Datei nach einem String."
    )
    parser.add_argument("zipdatei", help="Pfad zur Zip-Datei")
    parser.add_argument("suchbegriff", help="Gesuchter String")
    parser.add_argument(
        "-o", "--output", default="suchergebnisse.txt",
        help="Ausgabedatei (Standard: suchergebnisse.txt)",
    )
    parser.add_argument(
        "-i", "--ignore-case", action="store_true",
        help="Groß-/Kleinschreibung ignorieren",
    )
    args = parser.parse_args()

    try:
        zf = zipfile.ZipFile(args.zipdatei)
    except (FileNotFoundError, zipfile.BadZipFile) as e:
        print(f"Fehler beim Öffnen von '{args.zipdatei}': {e}", file=sys.stderr)
        return 1

    hits = 0
    files_with_hits = set()
    with zf, open(args.output, "w", encoding="utf-8") as out:
        out.write(f"Suche nach:  {args.suchbegriff!r}"
                  f"{' (ohne Groß-/Kleinschreibung)' if args.ignore_case else ''}\n")
        out.write(f"Zip-Datei:   {args.zipdatei}\n")
        out.write(f"Zeitpunkt:   {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        out.write("=" * 70 + "\n\n")

        for path, lineno, line in search_zip(zf, args.suchbegriff, args.ignore_case):
            if lineno is None:
                out.write(f"{path}: {line}\n")
                continue
            hits += 1
            files_with_hits.add(path)
            out.write(f"{path} (Zeile {lineno}): {line}\n")

        out.write("\n" + "=" * 70 + "\n")
        out.write(f"{hits} Treffer in {len(files_with_hits)} Datei(en)\n")

    print(f"{hits} Treffer in {len(files_with_hits)} Datei(en). "
          f"Ergebnisse gespeichert in: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
