## 0.2.0

### DOI import

We now accept both DOI urls of the form `https://doi.org/XXX/XXXX` as well as
raw DOIs `XXX/XXXX`; it can be easier to get the DOI url because you can just
right click and then select "copy link".

### Author trees

This will now create an person tree for each author in the imported bibtex if no
person tree exists. Use the `-P` flag to pass in the directory where people go
(for instance, `trees/people`).

## 0.1.0

Initial version:

- Input from .bib file with `-b`
- Input from DOI with `-D`
- Write tree with metadata and verbatim bibtex
