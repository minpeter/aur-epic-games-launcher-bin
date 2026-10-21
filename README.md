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

This repository automatically tracks upstream Linux AppImage releases from Epic Games every 6 hours via GitHub Actions. Each run:
1. Fails immediately if the `AUR_SSH_PRIVATE_KEY` secret is missing
2. Checks for a new upstream release and, if found, updates `pkgver`, `_commit` and the SHA-256 digest in `PKGBUILD`
3. Compares `PKGBUILD` with the one currently on the [AUR](https://aur.archlinux.org/packages/epic-games-launcher-bin); any difference (new release, manual change, or a previously failed AUR push) triggers a deploy
4. Builds the package with `makepkg --syncdeps` in an `archlinux:base-devel` container (`scripts/arch-build.sh`) and regenerates `.SRCINFO`; a build failure stops the run before anything is published
5. Pushes to the AUR first, then commits `PKGBUILD` and `.SRCINFO` to GitHub

`PKGBUILD` on GitHub is the source of truth: direct edits on the AUR are overwritten by the next run.
