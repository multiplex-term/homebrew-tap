#!/usr/bin/env python3
"""Point Formula/mpx.rb at a new mpx release.

Called by multiplex-cli's release workflow with that release's SHA256SUMS.
It lives here, next to the formula, because the formula is what every
`brew install multiplex-term/tap/mpx` resolves: the code that rewrites it
deserves tests (see script/test_bump.py) rather than being regexes buried in
a workflow nobody can run locally.

The rewrite is deliberately structural, not positional. Each `sha256` is
replaced by finding the `url` line that names its target triple and editing
the next `sha256` after it — so reordering the `on_macos`/`on_linux` blocks,
or adding a platform, cannot silently pair a digest with the wrong download.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

SHA_PATTERN = re.compile(r'^(\s*sha256\s+")([0-9a-f]{64})(")\s*$')
VERSION_PATTERN = re.compile(r'^(\s*version\s+")([^"]*)(")\s*$')
ARCHIVE_PATTERN = re.compile(r"^mpx-(?P<tag>v[^-]+)-(?P<target>.+)\.tar\.gz$")


class BumpError(RuntimeError):
    pass


def parse_checksums(text: str, tag: str) -> dict[str, str]:
    """`sha256sum` output → {target triple: digest}."""
    digests: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            raise BumpError(f"unreadable checksum line: {line!r}")
        digest, name = parts
        if len(digest) != 64 or not re.fullmatch(r"[0-9a-f]+", digest):
            raise BumpError(f"not a sha256 digest: {digest!r}")
        match = ARCHIVE_PATTERN.match(name)
        if not match:
            raise BumpError(f"unexpected archive name: {name!r}")
        if match["tag"] != tag:
            raise BumpError(
                f"{name} belongs to {match['tag']}, not the {tag} being published"
            )
        digests[match["target"]] = digest
    if not digests:
        raise BumpError("no checksums given")
    return digests


def bump(formula: str, version: str, tag: str, digests: dict[str, str]) -> str:
    lines = formula.splitlines(keepends=True)
    # Which target the most recent `url` line named, so the next `sha256`
    # knows which digest belongs to it.
    pending: str | None = None
    used: set[str] = set()

    for index, line in enumerate(lines):
        # The formula carries its version only in the URLs — brew scans it
        # from them, and `brew audit` rejects a `version` directive it can
        # scan. A leftover line is still updated when found, never required.
        if match := VERSION_PATTERN.match(line):
            lines[index] = f"{match[1]}{version}{match[3]}\n"
            continue

        if "url " in line and ".tar.gz" in line:
            # The old tag appears in both the release path and the filename.
            lines[index] = re.sub(r"/download/v[^/]+/", f"/download/{tag}/", line)
            lines[index] = re.sub(
                r"mpx-v[^-]+-(.+)\.tar\.gz", rf"mpx-{tag}-\1.tar.gz", lines[index]
            )
            target = re.search(r"mpx-[^-]+-(.+)\.tar\.gz", lines[index])
            if not target:
                raise BumpError(f"could not read a target triple from: {line.strip()!r}")
            pending = target[1]
            continue

        if match := SHA_PATTERN.match(line):
            if pending is None:
                raise BumpError(
                    f"line {index + 1}: sha256 with no url above it to pair with"
                )
            if pending not in digests:
                raise BumpError(
                    f"the release has no archive for {pending} "
                    f"(got: {', '.join(sorted(digests))})"
                )
            lines[index] = f"{match[1]}{digests[pending]}{match[3]}\n"
            used.add(pending)
            pending = None

    # A platform in the release that the formula never mentions is a formula
    # that silently stopped shipping it — louder as an error than as a
    # download nobody notices is missing.
    unused = set(digests) - used
    if unused:
        raise BumpError(
            f"formula never references: {', '.join(sorted(unused))}"
        )
    return "".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="e.g. 0.1.0")
    parser.add_argument("--tag", required=True, help="e.g. v0.1.0")
    parser.add_argument("--checksums", required=True, type=pathlib.Path)
    parser.add_argument("--formula", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)

    if args.tag != f"v{args.version}":
        raise BumpError(f"tag {args.tag} does not match version {args.version}")

    digests = parse_checksums(args.checksums.read_text(), args.tag)
    updated = bump(args.formula.read_text(), args.version, args.tag, digests)
    args.formula.write_text(updated)
    print(f"formula now at {args.version} across {len(digests)} platforms")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BumpError as error:
        print(f"bump: {error}", file=sys.stderr)
        sys.exit(1)
