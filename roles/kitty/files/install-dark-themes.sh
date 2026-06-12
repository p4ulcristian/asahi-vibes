#!/bin/sh
# Populate ~/.config/kitty/themes with the dark themes from kovidgoyal/kitty-themes,
# for the random-theme-on-launch rotation (see random-theme.sh + kitty.conf geninclude).
set -e
dir="$HOME/.config/kitty/themes"
mkdir -p "$dir"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
curl -fsSL "https://github.com/kovidgoyal/kitty-themes/archive/refs/heads/master.zip" -o "$tmp/themes.zip"
python3 - "$tmp/themes.zip" "$dir" <<'PY'
import zipfile, json, os, sys
zpath, outdir = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(zpath)
root = z.namelist()[0].split('/')[0]
meta = json.loads(z.read(f"{root}/themes.json"))
n = 0
for t in meta:
    if t.get("is_dark"):
        data = z.read(f"{root}/" + t["file"])
        with open(os.path.join(outdir, os.path.basename(t["file"])), "wb") as f:
            f.write(data)
        n += 1
print(f"Installed {n} dark themes to {outdir}")
PY
