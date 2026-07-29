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
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-aarch64-apple-darwin.tar.gz"
      sha256 "84ebcc358fd3840cb55ac6c0493a2356379f60416aa15dd5135bf516c2f56c60"
    end
    on_intel do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-x86_64-apple-darwin.tar.gz"
      sha256 "942659fb1279e96d02f53292b8ec81ceb53907a70b6ac85162f5367dc02dee0b"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-aarch64-unknown-linux-musl.tar.gz"
      sha256 "326eb88235d823cb85687df5190622c50dbfc3e09a158e5bad6a25608c69f6a4"
    end
    on_intel do
      url "https://github.com/multiplex-term/multiplex-cli-releases/releases/download/v0.1.0/mpx-v0.1.0-x86_64-unknown-linux-musl.tar.gz"
      sha256 "b55f23d01d1fb753e213324ffbefb0dea3ab2c70fb15859c38bedff35ce1f155"
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
