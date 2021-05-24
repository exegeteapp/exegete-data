import os
from .bible import OT, NT
from itertools import count
import requests
from lxml import etree
from io import BytesIO


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
        outf = "{}/{:>03}.xml".format(indir, chapter)
        if os.access(outf, os.R_OK):
            return True
        resp = self.session.get(
            "https://labs.bible.org/api/",
            params={
                "passage": "{} {}".format(book, chapter),
                "type": "xml",
                "formatting": "full",
            },
        )
        assert resp.status_code == 200
        # check that the chapter in the response matches what we asked for: bible.org API will
        # return chapter 1 if we overrun
        et = etree.parse(BytesIO(resp.content))
        if str(chapter) != et.xpath("/bible/item/chapter/text()")[0]:
            return False
        tmpf = outf + ".tmp"
        with open(tmpf, "w") as fd:
            fd.write(resp.text)
        os.rename(tmpf, outf)
        return True

    def dumpbook(self, basedir, book_idx, book):
        indir = mkdir_p(basedir, "{:>02} {}".format(book_idx, book))
        for chapter in count(1):
            print(book, chapter)
            if not self.dumpbookchapter(indir, book, chapter):
                break

    def dumptestament(self, testament, books):
        indir = mkdir_p("xml/", "{}".format(testament))
        for book_idx, book in enumerate(books, 1):
            self.dumpbook(indir, book_idx, book)

    def dumpbible(self):
        self.dumptestament("ot", OT)
        self.dumptestament("nt", NT)


def cli():
    dump = Dumper()
    dump.dumpbible()
    pass
