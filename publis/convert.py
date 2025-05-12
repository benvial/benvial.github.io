# Authors: Benjamin Vial
# This file is part of pytmod
# License: GPLv3
# See the documentation at bvial.info/pytmod


import os
import sys

from pybtex.style.formatting import BaseStyle
from pybtex.database import parse_file
from pybtex.textutils import abbreviate
from pybtex.backends.html import Backend
from pybtex.richtext import Tag, Text, Symbol, HRef
from pybtex.database import BibliographyData

sourcefile = "./publis.bib"
# betterbibfile = "./better/pubbetter.bib"
betterbibfile = sourcefile
# os.system("betterbib {} {}".format(sourcefile, betterbibfile))

try:
    BUILD_STATS = bool(int(sys.argv[1]))
except:
    BUILD_STATS = False
    

class HtmlTag(Tag):
    def __init__(self, name, opt, *args):
        super(HtmlTag, self).__init__(name, *args)
        self.options = opt

    def render(self, backend):
        text = super(Tag, self).render(backend)
        try:
            return backend.format_tag(self.name, text, self.options)
        except TypeError:
            return backend.format_tag(self.name, text)


def make_author(ret, context):
    authors = context.persons["author"]
    af = Text()
    for i, a in enumerate(authors):
        # fn = a.get_part("first")[0].abbreviate()
        # ln = a.get_part("last")[0]
        fn = a.rich_first_names[0].abbreviate()
        ln = a.rich_last_names[0]
        sep = Text(", ")
        if i == len(authors) - 1 and i != 0:
            fn = Text("and ") + fn
        af += fn + Text(" ") + ln + sep
    ret += af
    return ret


def make_editor(ret, context):
    authors = context.persons["editor"]
    af = Text("edited by ")
    for i, a in enumerate(authors):
        # fn = a.get_part("first")[0].abbreviate()
        # ln = a.get_part("last")[0]
        fn = a.rich_first_names[0].abbreviate()
        ln = a.rich_last_names[0]
        sep = Text(", ")
        if i == len(authors) - 1 and i != 0:
            fn = Text("and ") + fn
        af += fn + Text(" ") + ln + sep
    ret += af
    return ret


def make_title(ret, context):
    title = context.fields["title"]
    title = title.replace("{", "").replace("}", "")
    t = enrich(title)
    ret += Tag("em", t) + ". "
    return ret


def enrich(t):
    return Text.from_latex(t)


def make_links(ret, context):
    links = Text(" ")
    sep = Text(" ")
    if "doi" in context.fields:
        icon = HtmlTag("i", 'class="fa fa-link"', " ") + " DOI"
        links += HtmlTag(
            "a", 'href="https://doi.org/{}" target="_blank"'.format(context.fields["doi"]), icon
        )
        sep = Text(" | ")
    if "url" in context.fields:
        icon = HtmlTag("i", 'class="fa fa-download"', " ") + " URL"
        links += sep + HtmlTag("a", 'href="{}" target="_blank"'.format(context.fields["url"]), icon)

    if BUILD_STATS:

        if "doi" in context.fields:
            doi = context.fields['doi']
            if doi != "":
                links += HtmlTag("span", f'class="__dimensions_badge_embed__" data-doi="{doi}" data-hide-zero-citations="false" data-style="large_rectangle"', " ")

    ret += HtmlTag("span", 'class="biblinks"', links)
    return ret


def make_year(ret, context):
    if "year" in context.fields:
        ret += ", (" + context.fields["year"] + ")"
    return ret


class MyStyle(BaseStyle):
    def format_article(self, entry):
        context = entry["entry"]
        ret = Text("")
        ret = make_author(ret, context)
        ret = make_title(ret, context)
        ret += context.fields["journal"]
        if "volume" in context.fields:
            ret += Symbol("nbsp") + context.fields["volume"]
        if "number" in context.fields:
            ret += Symbol("nbsp") + "(" + context.fields["number"] + ")"
        if "pages" in context.fields:
            ret = ret + ":" + context.fields["pages"]

        ret = make_year(ret, context)
        ret = make_links(ret, context)
        return Tag("li", ret)

    def format_book(self, entry):
        context = entry["entry"]
        ret = Text("")
        ret = make_author(ret, context)
        ret = make_title(ret, context)
        ret = make_editor(ret, context)
        if "isbn" in context.fields:
            ret = ret + "ISBN: " + context.fields["pages"]
        ret = make_year(ret, context)
        ret = make_links(ret, context)
        return Tag("li", ret)

    def format_phdthesis(self, entry):
        context = entry["entry"]
        ret = Text("")
        ret = make_author(ret, context)
        ret = make_title(ret, context)
        if "school" in context.fields:
            ret = ret + enrich(context.fields["school"])
        ret = make_year(ret, context)
        ret = make_links(ret, context)
        return Tag("li", ret)

    def format_misc(self, entry):
        context = entry["entry"]
        ret = Text("")
        ret = make_author(ret, context)
        ret = make_title(ret, context)
        ret += context.fields["journal"]
        ret = make_year(ret, context)
        ret = make_links(ret, context)
        return Tag("li", ret)

    def format_inproceedings(self, entry):
        context = entry["entry"]
        ret = Text("")
        ret = make_author(ret, context)
        ret = make_title(ret, context)
        ret += Text("In ") + enrich(context.fields["booktitle"])
        if "volume" in context.fields:
            ret += Symbol("nbsp") + context.fields["volume"]
        if "number" in context.fields:
            ret += Symbol("nbsp") + "(" + context.fields["number"] + ")"
        if "pages" in context.fields:
            ret = ret + ":" + context.fields["pages"]
        if "address" in context.fields:
            ret = ret + Text(", ") + enrich(context.fields["address"])
        if "note" in context.fields:
            ret = ret + Text(", ") + context.fields["note"]
        ret = make_year(ret, context)
        ret = make_links(ret, context)
        return Tag("li", ret)


class HtmlBackend(Backend):
    symbols = {"ndash": u"&ndash;", "newblock": u"<br/>\n", "nbsp": u"&nbsp;"}
    format_tag = (
        lambda self, tag, text, options=None: u"<{0} {2} >{1}</{0}>".format(
            tag, text, options if options else ""
        )
        if text
        else u""
    )
    label = None

    def write_entry(self, key, label, text):
        if label != self.label:
            # self.output(u'<h3 class="{0} year">{0}</h3>\n'.format(label))
            self.label = label
        self.output(u"%s\n" % text)

    write_epilogue = lambda self: self.output(u"</ul>\n\n<hr />")
    prologue = u"""<ul class="biblio">
		"""

    def prepout(self, head, body):
        self.prologue = self.prologue

    def write_prologue(self):
        try:
            self.prepout("", "")
        except ValueError:
            pass
        self.output(self.prologue)


style = MyStyle()
back = HtmlBackend()
bib_data = parse_file(betterbibfile)
entries = bib_data.entries
keys = entries.keys()

cite_type = ["article", "book"]


#### presort
contents = []
for c in cite_type:
    bib = BibliographyData()
    for k in keys:
        etype = entries[k].original_type
        if etype == c:
            bib.add_entry(entry=entries[k], key=k)
    formatbib = style.format_bibliography(bib)
    outfile = "out.html"
    back.write_to_file(formatbib, outfile)
    with open(outfile, "r") as f:
        contents.append(f.read())


bib = BibliographyData()
for k in keys:
    etype = entries[k].original_type
    if etype == "inproceedings":
        bib.add_entry(entry=entries[k], key=k)
entries = bib.entries
keys = entries.keys()

for t in ["lecture comittee", "conference", "france"]:
    bib = BibliographyData()
    for k in keys:
        kw = entries[k].fields["type"]
        if kw == t:
            bib.add_entry(entry=entries[k], key=k)
    formatbib = style.format_bibliography(bib)
    outfile = "out.html"
    back.write_to_file(formatbib, outfile)
    with open(outfile, "r") as f:
        contents.append(f.read())


entries = bib_data.entries
keys = entries.keys()

for c in ["phdthesis"]:
    bib = BibliographyData()
    for k in keys:
        etype = entries[k].original_type
        if etype == c:
            bib.add_entry(entry=entries[k], key=k)
    formatbib = style.format_bibliography(bib)
    outfile = "out.html"
    back.write_to_file(formatbib, outfile)
    with open(outfile, "r") as f:
        contents.append(f.read())


for k in keys:
    etype = entries[k].original_type
    if etype == "misc":
        bib.add_entry(entry=entries[k], key=k)
entries = bib.entries
keys = entries.keys()

for t in ["code","prep"]:
    bib = BibliographyData()
    for k in keys:
        kw = entries[k].fields["type"]
        if kw == t:
            bib.add_entry(entry=entries[k], key=k)
    formatbib = style.format_bibliography(bib)
    outfile = "out.html"
    back.write_to_file(formatbib, outfile)
    with open(outfile, "r") as f:
        contents.append(f.read())


mdhead = """---
layout: page
title: "Publications"
description: ""
header-img: ""
weight: 3
---
"""

titles = [
    "### Articles in international peer-rewied journals",
    "### Contribution to a book chapter",
    "### Proceedings of international peer-reviewed conferences",
    "### International peer-reviewed conferences",
    "### National conferences and seminars",
    "### PhD thesis",
    "### Software and codes",
    "### In preparation",
]


mdfile = "../publications.md"
try:
    os.system("rm {}".format(mdfile))
except OSError:
    pass
with open(mdfile, "w") as outfile:
    outfile.write(mdhead)
    for t, c in zip(titles, contents):
        outfile.write(t)
        outfile.write("\n")
        outfile.write("\n")
        outfile.write(c)
        outfile.write("\n")
        outfile.write("\n")


os.system(f"rm out.html")
