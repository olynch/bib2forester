{
  lib,
  python3Packages,
  poetry
}:

python3Packages.buildPythonApplication {
  pname = "bib2forester";
  version = "0.2.1";
  src = ./.;

  # do not run tests
  
  doCheck = false;
  
  # specific to buildPythonPackage, see its reference
  
  pyproject = true;

  dependencies = with python3Packages; [
    requests
    bibtexparser_2
  ];
  
  build-system = with python3Packages; [
    poetry-core
  ];
}
