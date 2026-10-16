#!/usr/bin/env python3
"""Check for new Epic Games Launcher releases and update PKGBUILD."""

import argparse
import hashlib
import http.client
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

DOWNLOAD_HOST = "launcher-public-service-prod06.ol.epicgames.com"
DOWNLOAD_PATH = "/launcher/api/installer/download/EpicGamesLauncher-x86_64.AppImage"
URL_PATTERN = re.compile(
    r"Builds/EGLv2/(?P<version>[0-9.]+)(?:%2B|\+)(?P<commit>g[0-9a-f]+)/Linux/EpicGamesLauncher-x86_64\.AppImage"
)


def get_latest_release():
    conn = http.client.HTTPSConnection(DOWNLOAD_HOST, timeout=30)
    conn.request("HEAD", DOWNLOAD_PATH)
    res = conn.getresponse()
    location = res.getheader("Location")
    if not location:
        raise RuntimeError(f"Expected 303 redirect with Location header, got {res.status}")

    match = URL_PATTERN.search(location)
    if not match:
        raise RuntimeError(f"Location header does not match expected pattern: {location}")

    version = match.group("version")
    commit = match.group("commit")
    return version, commit, location


def parse_pkgbuild(pkgbuild_path: Path):
    content = pkgbuild_path.read_text(encoding="utf-8")
    pkgver_m = re.search(r"^pkgver=([^\s]+)", content, re.MULTILINE)
    commit_m = re.search(r"^_commit=([^\s]+)", content, re.MULTILINE)
    pkgrel_m = re.search(r"^pkgrel=([^\s]+)", content, re.MULTILINE)

    if not pkgver_m or not commit_m:
        raise ValueError("Could not parse pkgver or _commit from PKGBUILD")

    return pkgver_m.group(1), commit_m.group(1), int(pkgrel_m.group(1)) if pkgrel_m else 1


def compute_sha256(url: str) -> str:
    print(f"Downloading and calculating sha256: {url}...")
    hasher = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        downloaded = 0
        total = int(resp.headers.get("Content-Length", 0))
        while chunk := resp.read(1024 * 1024):  # 1MB chunks
            hasher.update(chunk)
            downloaded += len(chunk)
            if total > 0:
                percent = (downloaded / total) * 100
                sys.stdout.write(f"\rProgress: {downloaded // (1024*1024)}MB / {total // (1024*1024)}MB ({percent:.1f}%)")
                sys.stdout.flush()
    print("\nDownload complete.")
    return hasher.hexdigest()


def update_pkgbuild(pkgbuild_path: Path, new_ver: str, new_commit: str, new_sha: str):
    content = pkgbuild_path.read_text(encoding="utf-8")
    content = re.sub(r"^pkgver=.*$", f"pkgver={new_ver}", content, flags=re.MULTILINE)
    content = re.sub(r"^_commit=.*$", f"_commit={new_commit}", content, flags=re.MULTILINE)
    content = re.sub(r"^pkgrel=.*$", "pkgrel=1", content, flags=re.MULTILINE)
    new_content, count = re.subn(
        r"sha256sums=\(\s*'[^']+'\s*\)",
        f"sha256sums=('{new_sha}')",
        content,
        flags=re.DOTALL,
    )
    if count == 0:
        raise ValueError("Could not find and replace sha256sums in PKGBUILD")
    content = new_content
    pkgbuild_path.write_text(content, encoding="utf-8")
    print(f"Updated {pkgbuild_path} to {new_ver}-{new_commit} (sha256: {new_sha})")


def set_github_output(name: str, value: str):
    output_file = os.getenv("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pkgbuild", type=Path, default=Path("PKGBUILD"), help="Path to PKGBUILD")
    parser.add_argument("--dry-run", action="store_true", help="Do not update PKGBUILD")
    parser.add_argument("--force", action="store_true", help="Force recalculating hash and rewriting")
    args = parser.parse_args()

    curr_ver, curr_commit, curr_rel = parse_pkgbuild(args.pkgbuild)
    print(f"Current PKGBUILD: version={curr_ver}, commit={curr_commit}, rel={curr_rel}")

    latest_ver, latest_commit, location = get_latest_release()
    print(f"Upstream release: version={latest_ver}, commit={latest_commit}")

    if not args.force and curr_ver == latest_ver and curr_commit == latest_commit:
        print("PKGBUILD is already up to date.")
        set_github_output("updated", "false")
        return 0

    print(f"Update available: {curr_ver}+{curr_commit} -> {latest_ver}+{latest_commit}")
    set_github_output("updated", "true")
    set_github_output("new_version", latest_ver)
    set_github_output("new_commit", latest_commit)

    if args.dry_run:
        print("Dry run requested; stopping before download.")
        return 0

    download_url = f"https://content-download-egs.distro.on.epicgames.com/Builds/EGLv2/{latest_ver}%2B{latest_commit}/Linux/EpicGamesLauncher-x86_64.AppImage"
    new_sha = compute_sha256(download_url)
    set_github_output("new_sha256", new_sha)

    update_pkgbuild(args.pkgbuild, latest_ver, latest_commit, new_sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
