{pkgs ? import <nixpkgs> {}}:
with pkgs;
  pkgs.mkShell {
    LD_LIBRARY_PATH = lib.makeLibraryPath [pkgs.stdenv.cc.cc];
    packages = with pkgs; [
      python3Packages.uv
    ];
  }
