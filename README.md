# aur-epic-games-launcher-bin

[![AUR package](https://img.shields.io/aur/version/epic-games-launcher-bin)](https://aur.archlinux.org/packages/epic-games-launcher-bin)
[![Update & Sync](https://github.com/minpeter/aur-epic-games-launcher-bin/actions/workflows/sync.yml/badge.svg)](https://github.com/minpeter/aur-epic-games-launcher-bin/actions/workflows/sync.yml)

Arch Linux AUR packaging repository for the official [Epic Games Store launcher](https://launcher.epicgames.com/) for Linux (Preview).

- **AUR Package:** [`epic-games-launcher-bin`](https://aur.archlinux.org/packages/epic-games-launcher-bin)
- **Official Upstream:** [https://launcher.epicgames.com/](https://launcher.epicgames.com/)

---

## Installation

Using an AUR helper like `yay` or `paru`:

```bash
yay -S epic-games-launcher-bin
# or
paru -S epic-games-launcher-bin
```

Or manually with `makepkg`:

```bash
git clone https://aur.archlinux.org/epic-games-launcher-bin.git
cd epic-games-launcher-bin
makepkg -si
```

---

## Troubleshooting

### Wayland flickering or `Error 71 (Protocol error)` crash
On Wayland (particularly with NVIDIA drivers or certain compositors), WebKitGTK's hardware DMABUF renderer may cause window flickering or crash with `Error 71 (Protocol error) dispatching to Wayland display`.

To work around this, force the shared-memory (SHM) renderer:

```bash
WEBKIT_DMABUF_RENDERER_FORCE_SHM=1 epic-games-launcher
```

You can also export this in your environment or customize your desktop entry:
```bash
cp /usr/share/applications/epic-games-launcher.desktop ~/.local/share/applications/
sed -i 's|^Exec=EpicGamesLauncher|Exec=env WEBKIT_DMABUF_RENDERER_FORCE_SHM=1 EpicGamesLauncher|' ~/.local/share/applications/epic-games-launcher.desktop
```

### Tray / AppIndicator Crash
The launcher requires `libayatana-appindicator` to initialize its system tray indicator. This is included as a mandatory dependency starting with version `0.96.1-1`.

---

## Automation

This repository automatically tracks upstream Linux AppImage releases from Epic Games every 6 hours via GitHub Actions. When a new version is detected:
1. Calculates the new SHA-256 digest
2. Updates `PKGBUILD` and `.SRCINFO`
3. Automatically publishes the update to the [AUR](https://aur.archlinux.org/packages/epic-games-launcher-bin)
