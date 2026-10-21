#!/usr/bin/env bash
# Build the package inside an archlinux:base-devel container and print .SRCINFO.
#
# Usage (from the repository root):
#   docker run --rm -v "$PWD":/work:ro archlinux:base-devel bash /work/scripts/arch-build.sh > .SRCINFO
#
# A full `makepkg -s` resolves every dependency from the Arch repos and runs
# package(), so a renamed dependency or a changed AppImage layout fails here
# instead of being published to the AUR. Build logs go to stderr; stdout carries
# only the generated .SRCINFO.
set -euo pipefail

{
  pacman -Syu --noconfirm --needed sudo
  useradd -m builder
  echo 'builder ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/builder
  install -d -o builder -g builder /home/builder/build
  install -m644 -o builder -g builder /work/PKGBUILD /home/builder/build/PKGBUILD
  su builder -c 'cd /home/builder/build && makepkg --syncdeps --noconfirm --cleanbuild'
  ls -l /home/builder/build/*.pkg.tar.*
} >&2

su builder -c 'cd /home/builder/build && makepkg --printsrcinfo'
