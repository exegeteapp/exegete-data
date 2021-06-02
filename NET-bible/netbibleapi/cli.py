import json
import os
from io import BytesIO
from itertools import count

import requests

from .bible import NT, OT


def mkdir_p(indir, d):
    indir = "{}/{}/".format(indir, d)
    try:
        os.mkdir(indir)
    except FileExistsError:
        pass
    return indir


class Dumper:
    def __init__(self):
        self.session = requests.session()

    def dumpbookchapter(self, indir, book, chapter):
        outf = "{}/{:>03}.json".format(indir, chapter)
        if os.access(outf, os.R_OK):
            return True
        resp = self.session.get(
            "https://labs.bible.org/api/",
            params={
                "passage": "{} {}".format(book, chapter),
                "type": "json",
                "formatting": "full",
            },
        )
        assert resp.status_code == 200
        text = resp.json()
        # check that the chapter in the response matches what we asked for: bible.org API will
        # return chapter 1 if we overrun
        if str(chapter) != text[0]["chapter"]:
            return False
        tmpf = outf + ".tmp"
        with open(tmpf, "w") as fd:
            json.dump(text, fd, indent=2, sort_keys=True)
        os.rename(tmpf, outf)
        return True

    def dumpbook(self, basedir, book_idx, book):
        indir = mkdir_p(basedir, "{:>02} {}".format(book_idx, book))
        for chapter in count(1):
            print(book, chapter)
            if not self.dumpbookchapter(indir, book, chapter):
                break

    def dumptestament(self, testament, books):
        indir = mkdir_p("json/", "{}".format(testament))
        for book_idx, book in enumerate(books, 1):
            self.dumpbook(indir, book_idx, book)

    def dumpbible(self):
        self.dumptestament("ot", OT)
        self.dumptestament("nt", NT)


def cli():
    dump = Dumper()
    dump.dumpbible()
    pass
