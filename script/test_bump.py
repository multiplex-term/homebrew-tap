#!/usr/bin/env python3
"""Tests for script/bump.py — run with `python3 -m unittest discover script`.

What these protect: the formula is what every `brew install` resolves, and a
digest paired with the wrong download is a failure nobody sees until an
install aborts on a checksum mismatch.
"""

import unittest

from bump import BumpError, bump, parse_checksums

TARGETS = [
    "aarch64-apple-darwin",
    "x86_64-apple-darwin",
    "aarch64-unknown-linux-musl",
    "x86_64-unknown-linux-musl",
]

# Deliberately distinct digests so a mispairing cannot pass.
DIGESTS = {target: str(index + 1) * 64 for index, target in enumerate(TARGETS)}


def checksum_file(tag="v0.2.0", digests=None):
    digests = digests or DIGESTS
    return "".join(
        f"{digest}  mpx-{tag}-{target}.tar.gz\n" for target, digest in digests.items()
    )


def formula(tag="v0.1.0", version="0.1.0"):
    blocks = "\n".join(
        f'''    url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/{tag}/mpx-{tag}-{target}.tar.gz"
    sha256 "{"0" * 64}"'''
        for target in TARGETS
    )
    return f'''class Mpx < Formula
  version "{version}"
{blocks}
end
'''


class ParseChecksums(unittest.TestCase):
    def test_maps_each_archive_to_its_target(self):
        parsed = parse_checksums(checksum_file(), "v0.2.0")
        self.assertEqual(parsed, DIGESTS)

    def test_rejects_a_digest_from_another_release(self):
        # The guard that matters most: stale artifacts in the working directory
        # would otherwise be published under the new tag's formula.
        with self.assertRaises(BumpError) as caught:
            parse_checksums(checksum_file(tag="v0.1.9"), "v0.2.0")
        self.assertIn("v0.1.9", str(caught.exception))

    def test_rejects_malformed_input(self):
        for bad in ["notadigest  mpx-v0.2.0-x86_64-apple-darwin.tar.gz\n",
                    f"{'a' * 64}  some-other-thing.zip\n",
                    f"{'a' * 64}\n"]:
            with self.subTest(bad=bad), self.assertRaises(BumpError):
                parse_checksums(bad, "v0.2.0")

    def test_rejects_empty(self):
        with self.assertRaises(BumpError):
            parse_checksums("\n\n", "v0.2.0")


class Bump(unittest.TestCase):
    def test_every_digest_lands_under_its_own_url(self):
        result = bump(formula(), "0.2.0", "v0.2.0", DIGESTS)
        lines = result.splitlines()
        for index, line in enumerate(lines):
            if "url " not in line:
                continue
            target = next(t for t in TARGETS if f"-{t}.tar.gz" in line)
            self.assertIn(DIGESTS[target], lines[index + 1], f"{target} mispaired")

    def test_rewrites_version_and_both_places_the_tag_appears(self):
        result = bump(formula(), "0.2.0", "v0.2.0", DIGESTS)
        self.assertIn('version "0.2.0"', result)
        self.assertNotIn("v0.1.0", result)
        self.assertIn("/download/v0.2.0/mpx-v0.2.0-aarch64-apple-darwin.tar.gz", result)

    def test_survives_reordered_blocks(self):
        # Structural, not positional: the formula's platform order is a style
        # choice and must not decide which digest goes where.
        reversed_targets = list(reversed(TARGETS))
        blocks = "\n".join(
            f'''    url "https://github.com/x/y/releases/download/v0.1.0/mpx-v0.1.0-{t}.tar.gz"
    sha256 "{"0" * 64}"'''
            for t in reversed_targets
        )
        source = f'class Mpx < Formula\n  version "0.1.0"\n{blocks}\nend\n'
        result = bump(source, "0.2.0", "v0.2.0", DIGESTS)
        lines = result.splitlines()
        for index, line in enumerate(lines):
            if "url " not in line:
                continue
            target = next(t for t in TARGETS if f"-{t}.tar.gz" in line)
            self.assertIn(DIGESTS[target], lines[index + 1])

    def test_refuses_a_platform_the_formula_forgot(self):
        # A release that ships four archives against a formula naming three
        # means one platform silently stopped being installable.
        trimmed = formula().replace(
            f'''    url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-x86_64-unknown-linux-musl.tar.gz"
    sha256 "{"0" * 64}"
''',
            "",
        )
        with self.assertRaises(BumpError) as caught:
            bump(trimmed, "0.2.0", "v0.2.0", DIGESTS)
        self.assertIn("x86_64-unknown-linux-musl", str(caught.exception))

    def test_refuses_a_platform_the_release_lacks(self):
        partial = {k: v for k, v in DIGESTS.items() if k != "x86_64-apple-darwin"}
        with self.assertRaises(BumpError) as caught:
            bump(formula(), "0.2.0", "v0.2.0", partial)
        self.assertIn("x86_64-apple-darwin", str(caught.exception))

    def test_refuses_a_formula_with_no_version(self):
        with self.assertRaises(BumpError):
            bump('class Mpx < Formula\nend\n', "0.2.0", "v0.2.0", {})

    def test_is_idempotent(self):
        once = bump(formula(), "0.2.0", "v0.2.0", DIGESTS)
        twice = bump(once, "0.2.0", "v0.2.0", DIGESTS)
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
