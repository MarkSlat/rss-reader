with import <nixpkgs> {};

mkShell {
  packages = [
    (python312.withPackages (ps: with ps; [
      feedparser
      flask
      numpy
      requests
      sentence-transformers
    ]))
  ];
}