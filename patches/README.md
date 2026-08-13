# Hardware patches

Salvaged from the kernel/Hyprland build trees before they were pruned (2026-08-13).
These are the source of truth for this machine's hardware fixes — the multi-GB
build trees they came from are gone and are regenerable from what's here.

| File | What it does |
|---|---|
| `t8112-j413.dts.patch` | DisplayPort-altmode audio on the front-left USB-C port. Adds the missing `/aliases/sio` entry (m1n1 needs it to load SIO firmware) and enables `sio` + `dpaudio1`. Without it: `apple-sio: SIO did not boot` and no sound over USB-C / AR glasses. |
| `0001-t8112-j413-enable-sio-for-dp-alt-audio.patch` | The same fix as a formatted commit, as consumed by `PKGBUILD`. |
| `hyprland-Monitor.cpp.patch` | Null-guard on `m_activeWorkspace` in `CMonitor::onConnect` — prevents a crash when a monitor connects with no active workspace. |
| `PKGBUILD` | Recipe for the `linux-asahi-fairydust` kernel package. |
| `kernel-config` | The kernel `.config` that build used. |
| `t8112-j413.dtb` | The compiled device tree from that build. |

## The built kernel package

The binary matching the running kernel (`7.0.11.asahi1.fairydust-1`) is **not** in
git — it lives at:

    /var/cache/pacman/pkg/linux-asahi-fairydust-7.0.11.asahi1.fairydust-1-aarch64.pkg.tar.xz

Reinstall or roll back with:

    sudo pacman -U /var/cache/pacman/pkg/linux-asahi-fairydust-*.pkg.tar.xz

Note `paccache`/`pacman -Sc` may prune it eventually; rebuild from `PKGBUILD` if it goes.
