#!/usr/bin/env bash

poetry build

VERSION=$(poetry version -s)

poetry run shiv -c bib2forester -o zips/bib2forester-$VERSION.pyz dist/bib2forester-$VERSION-py3-none-any.whl
