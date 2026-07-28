# Bumped automatically by multiplex-cli's release workflow, which runs
# script/bump.py against the release's SHA256SUMS. Edit the shape here by
# hand; never hand-edit the version or the digests, or the next release will
# quietly overwrite them.
class Mpx < Formula
  desc "Companion CLI for Multiplex — bind a machine to the app from its own terminal"
  homepage "https://multiplexterm.dev"
  version "0.1.0"
  license "MIT"

  # Prebuilt binaries rather than a source build: `mpx bind` is usually run on
  # a server the user does not want to install a Rust toolchain on, and the
  # source repository stays private until the app ships.
  on_macos do
    on_arm do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-aarch64-apple-darwin.tar.gz"
      sha256 "0000000000000000000000000000000000000000000000000000000000000000"
    end
    on_intel do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-x86_64-apple-darwin.tar.gz"
      sha256 "0000000000000000000000000000000000000000000000000000000000000000"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-aarch64-unknown-linux-musl.tar.gz"
      sha256 "0000000000000000000000000000000000000000000000000000000000000000"
    end
    on_intel do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-x86_64-unknown-linux-musl.tar.gz"
      sha256 "0000000000000000000000000000000000000000000000000000000000000000"
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
