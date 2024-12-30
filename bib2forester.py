#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.bibtexparser

import bibtexparser
from bibtexparser.middlewares import MergeNameParts, MergeCoAuthors, SeparateCoAuthors, SplitNameParts
import argparse
import io
from pathlib import Path
from unicodedata import category
import requests

## This code is stolen from pubs

def _get_request(url, headers=None):
    """GET requests to a url. Return the `requests` object.

    :raise ConnectionError:  if anything goes bad (connection refused, timeout
                             http status error (401, 404, etc)).
    """
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        raise ReferenceNotFoundError(e.args)


    ## DOI support

def doi2bibtex(doi, **kwargs):
    """Return a bibtex string from a DOI"""

    url = 'https://dx.doi.org/{}'.format(doi)
    headers = {'accept': 'application/x-bibtex'}
    r = _get_request(url, headers=headers)
    if r.encoding is None:
        r.encoding = 'utf8'  # Do not rely on guessing from request

    return r.text

def get_args():
    parser = argparse.ArgumentParser(
                        prog='bib2forester',
                        description='converts bib files to forester',
                        epilog='')

    parser.add_argument('-b', '--bib')
    parser.add_argument('-D', '--doi')
    parser.add_argument('destdir')

    return parser.parse_args()

def nameify(s):
    return ''.join([c for c in s.lower() if category(c) in ['Ll', 'Lu']])

def author_tree(author):
    return "-".join([nameify(n) for n in [author.first[0], author.last[0]]])

BORING_WORDS = ['the', 'an', 'a', 'on']

def title_part(e):
    if 'title' in e.fields_dict:
        words = [nameify(w) for w in e.fields_dict['title'].value.split(' ') if not nameify(w) in BORING_WORDS]
        return words[0] if len(words) > 0 else "notitle"
    return "notitle"

def year_part(e):
    if 'year' in e.fields_dict:
        return e.fields_dict['year'].value
    return 'noyear'

def author_part(e):
    if 'author' in e.fields_dict:
        authors = e.fields_dict['author'].value
        if len(authors) > 0:
            return nameify(authors[0].last[0])
    return "noauthor"

def tree(e):
    buf = io.StringIO()
    if 'title' in e.fields_dict:
        buf.write("\\title{{{}}}\n".format(e.fields_dict['title'].value))
    if 'author' in e.fields_dict:
        for author in e.fields_dict['author'].value:
            buf.write("\\author{{{}}}\n".format(author_tree(author)))
    if 'year' in e.fields_dict:
        buf.write("\\date{{{}}}\n".format(e.fields_dict['year'].value))
    buf.write("\\taxon{reference}\n")
    if 'doi' in e.fields_dict:
        buf.write("\\meta{{doi}}{{{}}}\n".format(e.fields_dict['doi'].value))
    elif 'DOI' in e.fields_dict:
        buf.write("\\meta{{doi}}{{{}}}\n".format(e.fields_dict['DOI'].value))
    elif 'url' in e.fields_dict:
        buf.write("\\meta{{external}}{{{}}}\n".format(e.fields_dict['url'].value))
    name = "{}-{}-{}".format(author_part(e), year_part(e), title_part(e))
    bibtex = bibtexparser.write_string(
        bibtexparser.Library([e]),
        prepend_middleware=[MergeNameParts(), MergeCoAuthors()]
    )
    buf.write("\\meta{{bibtex}}{{\\verb>>|\n{}>>}}".format(bibtex))
    buf.seek(0)

    return (buf.read(), name)

def main():
    args = get_args()
    if args.doi:
        bibs = doi2bibtex(args.doi)
    elif args.bib:
        with open(args.bib, 'r') as f:
            bibs = f.read()
    bibtex_database = bibtexparser.parse_string(
        bibs,
        append_middleware=[SeparateCoAuthors(), SplitNameParts()]
    )
    for e in bibtex_database.entries:
        (content, name) = tree(e)
        fname = name + ".tree"
        dest = Path(args.destdir) / fname
        print("writing {}".format(str(dest)))
        with open(str(dest), 'w') as out:
            out.write(content)

if __name__ == "__main__":
    main()
