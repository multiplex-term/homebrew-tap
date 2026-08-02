# Bumped automatically by multiplex-cli's release workflow, which runs
# script/bump.py against the release's SHA256SUMS. Edit the shape here by
# hand; never hand-edit the URLs or the digests, or the next release will
# quietly overwrite them. The version lives only in the URLs — brew scans it
# from them, and `brew audit` rejects a `version` directive it can scan.
class Mpx < Formula
  desc "Companion CLI for Multiplex — bind a machine to the app from its own terminal"
  homepage "https://multiplexterm.dev"
  license "MIT"

  # Prebuilt binaries rather than a source build: `mpx bind` is usually run on
  # a server the user does not want to install a Rust toolchain on, and the
  # source repository is not public.
  on_macos do
    on_arm do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.1/mpx-v0.1.1-aarch64-apple-darwin.tar.gz"
      sha256 "c7198cd0d8e780078cb829eeb119fb4260e63e3899c56841f8a2c04a9715b588"
    end
    on_intel do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.1/mpx-v0.1.1-x86_64-apple-darwin.tar.gz"
      sha256 "c38255c799dade29196bae1505fb084a357ea995c440f30693aab03c5780e73b"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.1/mpx-v0.1.1-aarch64-unknown-linux-musl.tar.gz"
      sha256 "7c1e1471647bf1a305bc08043cd8b1f8cab370a2dde0f5995edf0ffd850afacb"
    end
    on_intel do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.1/mpx-v0.1.1-x86_64-unknown-linux-musl.tar.gz"
      sha256 "ef753499b2f135bc654a7f8d7f04680e1179114e4db8cf88dad5cae1b8afee77"
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
