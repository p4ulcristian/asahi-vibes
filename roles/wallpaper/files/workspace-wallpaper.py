#!/usr/bin/env python3
"""Per-workspace / per-virtual-screen wallpapers for Hyprland + mirage.

awww (the renamed swww) only does per-OUTPUT wallpapers, so this daemon maps each
output to the wallpaper of the workspace it currently holds:

  * Normal Hyprland: one physical monitor; switching workspaces (Super+1..0,
    gesture, click) swaps its wallpaper.
  * mirage AR mode: each VIRTn virtual screen is pinned to workspace n and they
    are all visible at once on the curved wall, so every screen shows its own
    wallpaper simultaneously.

Wallpapers live in ~/pictures/wallpapers/workspaces/<workspace>.png and fall back
to 1.png when a numbered file is missing.

It listens on Hyprland's event socket (.socket2.sock) directly -- no socat -- and
reacts to:
  * monitoradded  -> a screen appeared (mirage spawning VIRT outputs): wallpaper it
  * workspace     -> normal-mode workspace switch: re-wallpaper the focused monitor

The physical glasses output is deliberately left bare while mirage runs: a
background layer on it would disqualify mirage's zero-copy direct scanout (120Hz).
"""
import json
import os
import socket
import subprocess
import time

WALLDIR = os.path.expanduser("~/pictures/wallpapers/workspaces")
DEFAULT = os.path.join(WALLDIR, "1.png")
TRANSITION = ["--transition-type", "fade", "--transition-duration", "1"]


def run(*args):
    return subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def monitors():
    try:
        out = subprocess.check_output(["hyprctl", "monitors", "-j"])
        return json.loads(out)
    except Exception:
        return []


def mirage_running():
    return run("pgrep", "-x", "mirage").returncode == 0


def wallpaper_for(ws):
    path = os.path.join(WALLDIR, f"{ws}.png")
    return path if os.path.exists(path) else DEFAULT


def should_wallpaper(name):
    # Virtual screens are captured onto the wall -> always wallpaper them.
    # Physical outputs only when not in mirage, to keep direct scanout on the glasses.
    return name.startswith("VIRT") or not mirage_running()


def apply_output(name, ws):
    if not should_wallpaper(name):
        return
    run("awww", "img", "-o", name, *TRANSITION, wallpaper_for(ws))


def apply_all():
    for m in monitors():
        apply_output(m["name"], m["activeWorkspace"]["name"])


def apply_monitor_by_name(name):
    # A freshly created output may not have its mode/workspace bound yet
    # (setup_displays.py creates the output, then binds the workspace ~0.3s later).
    for _ in range(20):
        m = next((m for m in monitors() if m["name"] == name), None)
        if m:
            apply_output(name, m["activeWorkspace"]["name"])
            return
        time.sleep(0.2)


def ensure_daemon():
    if run("awww", "query").returncode != 0:
        subprocess.Popen(["awww-daemon"])
        for _ in range(40):
            if run("awww", "query").returncode == 0:
                break
            time.sleep(0.25)


def event_socket_path():
    sig = os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
    rt = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    return os.path.join(rt, "hypr", sig, ".socket2.sock")


def handle(line):
    name, _, data = line.partition(">>")
    if name == "monitoradded":
        apply_monitor_by_name(data.strip())
    elif name == "workspace":
        # Normal-mode switch: re-wallpaper whichever monitor is focused.
        foc = next((m for m in monitors() if m.get("focused")), None)
        if foc:
            apply_output(foc["name"], data.strip())


def main():
    ensure_daemon()
    apply_all()
    path = event_socket_path()
    while True:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(path)
            with s.makefile("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    handle(line.rstrip("\n"))
        except Exception:
            pass
        time.sleep(2)  # Hyprland restarted or socket dropped; reconnect.


if __name__ == "__main__":
    main()
