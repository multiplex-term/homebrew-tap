# Bumped automatically by mpx-cli's release workflow, which runs
# script/bump.py against the release's SHA256SUMS. Edit the shape here by
# hand; never hand-edit the URLs or the digests, or the next release will
# quietly overwrite them. The version lives only in the URLs — brew scans it
# from them, and `brew audit` rejects a `version` directive it can scan.
class Mpx < Formula
  desc "Companion CLI for Multiplex — bind a machine to the app from its own terminal"
  homepage "https://multiplexterm.dev"
  license "MIT"

  # Prebuilt binaries rather than a source build: `mpx bind` is usually run on
  # a server the user does not want to install a Rust toolchain on.
  on_macos do
    on_arm do
      url "https://github.com/multiplex-term/mpx-cli/releases/download/v0.1.2/mpx-v0.1.2-aarch64-apple-darwin.tar.gz"
      sha256 "a1b307e1abd7e768b3e72173b48a9fc184a258da95af68218ab8f0695f529c05"
    end
    on_intel do
      url "https://github.com/multiplex-term/mpx-cli/releases/download/v0.1.2/mpx-v0.1.2-x86_64-apple-darwin.tar.gz"
      sha256 "11344d15f463a537587007a7adf1bd31f51dfc52db59cd20e7520a7d38a21c5d"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/multiplex-term/mpx-cli/releases/download/v0.1.2/mpx-v0.1.2-aarch64-unknown-linux-musl.tar.gz"
      sha256 "846384bd51065819ad20aab8cd126e0d016e2e78c5e07ba6a2faf88445483368"
    end
    on_intel do
      url "https://github.com/multiplex-term/mpx-cli/releases/download/v0.1.2/mpx-v0.1.2-x86_64-unknown-linux-musl.tar.gz"
      sha256 "2949c98b94ebd44604b844ae83d57861f1645c31ecb185581e98786627fc0784"
    end
  end

  def install
    bin.install "mpx"
    # `multiplex` is the spelled-out alias every install channel carries. The
    # archive ships it as a real copy; link it here so `brew unlink` and
    # upgrades treat the pair as one thing.
    bin.install_symlink bin/"mpx" => "multiplex"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mpx --version")
    # `bind --help` rather than plain `--help`: it is the subcommand the whole
    # tool exists for, and a broken argument tree usually shows up there first.
    assert_match "bind", shell_output("#{bin}/mpx bind --help")
    assert_match version.to_s, shell_output("#{bin}/multiplex --version")
  end
end
