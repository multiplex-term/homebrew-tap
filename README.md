# multiplex-term/tap

Homebrew tap for [`mpx`](https://multiplexterm.dev), the companion CLI for
Multiplex. You run it **on the machine you want to add** to the app; it offers
that machine over a terminal QR, your local network, or (with `--copy`) the
clipboard, and the app enrols its own key into your `authorized_keys`.

```sh
brew install multiplex-term/tap/mpx
mpx bind
```

Both `mpx` and the spelled-out `multiplex` alias land on your PATH.

Prefer no Homebrew? `curl -fsSL https://multiplexterm.dev/install-mpx-cli | sh`
covers macOS and Linux, and installs the same archives.

## What's here

| Path | Why |
| --- | --- |
| `Formula/mpx.rb` | Installs prebuilt binaries for macOS and Linux, arm64 and x86_64 |
| `script/bump.py` | Points the formula at a new release, given that release's `SHA256SUMS` |
| `script/test_bump.py` | Tests for the above |

The formula ships **prebuilt binaries rather than a source build**: `mpx bind`
is usually run on a server nobody wants a Rust toolchain on. Builds come from
[`mpx-cli`](https://github.com/multiplex-term/mpx-cli/releases), the CLI's own
repository. Releases up to v0.1.2 were published to
[`multiplex-cli-releases`](https://github.com/multiplex-term/multiplex-cli-releases)
while that source was closed; they are mirrored under the new URLs, so the
digests below did not change when the formula moved.

(The repository is named `homebrew-tap` while the tap is `multiplex-term/tap`:
that prefix is Homebrew's own convention — `brew install multiplex-term/tap/…`
resolves to the `homebrew-tap` repo, and CI's setup-homebrew action uses the
same rule to register the checkout as a tap.)

## Bumping

Don't. `mpx-cli`'s release workflow runs `script/bump.py` on every tag
and opens a PR here; merging it is the whole job. The digests in that PR come
from the release's own `SHA256SUMS`, so a mismatch means the artifacts and the
formula disagree — investigate rather than merge.

Edit the formula's *shape* by hand freely (test block, dependencies, install
layout). Never hand-edit a `url` or a `sha256`: the next release overwrites
both, so a manual change there is a change that silently disappears. There is
deliberately no `version` line — brew scans the version from the URLs, and
`brew audit` rejects a directive it can scan.

The bump is structural, not positional — each digest is matched to the `url`
line naming its target triple — so reordering the platform blocks is safe. Run
the tests after touching the script:

```sh
python3 -m unittest discover -s script -t script
```
