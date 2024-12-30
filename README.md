# bib2forester

## Installation

This script requires the bibtexparser v2 and requests python libraries.

## Usage

This script converts bibtex files to forester trees. It can take bibtex from local .bib files or directly from doi.org.

To take from a local .bib file:

```
python3 bib2forester -b refs.bib DEST
```

To take from a DOI:

```
python3 bib2forester -D XXX/XXXX DEST
```
