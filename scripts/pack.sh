#!/bin/sh
# Build the Chrome Web Store zip. Only extension files — no store/ assets.
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p dist
OUT="$ROOT/dist/stop-fable-default-opus.zip"
rm -f "$OUT"
zip -X -r "$OUT" \
  manifest.json \
  content.js \
  popup.html \
  icons \
  -x "*.DS_Store"
python3 - "$OUT" << 'PY'
import json, sys, zipfile
path = sys.argv[1]
with zipfile.ZipFile(path) as z:
    names = z.namelist()
    assert "manifest.json" in names, names
    assert "content.js" in names
    assert "popup.html" in names
    for size in (16, 32, 48, 128):
        assert f"icons/icon{size}.png" in names
    manifest = json.loads(z.read("manifest.json"))
    assert manifest["manifest_version"] == 3
    assert "permissions" not in manifest
print("packed", path)
print("files:")
for n in names:
    print(" ", n)
PY
cp "$OUT" "$ROOT/store/upload/00-stop-fable-default-opus.zip"
echo "Upload $OUT (also copied to store/upload/00-stop-fable-default-opus.zip)."
