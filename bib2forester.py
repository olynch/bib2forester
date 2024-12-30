#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.bibtexparser

import bibtexparser
from bibtexparser.middlewares import MergeNameParts, MergeCoAuthors, SeparateCoAuthors, SplitNameParts
import argparse
import io
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser(
                        prog='bib2forester',
                        description='converts bib files to forester',
                        epilog='')

    parser.add_argument('bibfile')
    parser.add_argument('destdir')

    return parser.parse_args()

def author_tree(author):
    return "-".join([n.lower() for n in author.first + author.last])

BORING_WORDS = ['the', 'an', 'a', 'on']

def title_part(e):
    if 'title' in e.fields_dict:
        words = [w.lower() for w in e.fields_dict['title'].value.split(' ') if not w.lower() in BORING_WORDS]
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
            return "-".join(authors[0].last).lower()
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
    bibtex_database = bibtexparser.parse_file(
        args.bibfile,
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
