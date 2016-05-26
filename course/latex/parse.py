import re
from .utils import strip_comments
from django.utils.translation import ugettext as _
from django.utils.functional import cached_property

class TexDocParseError(Exception):
    pass

class TexDocMissingElementError(TexDocParseError):
    pass

class TexDocWrongElementOrderError(TexDocParseError):
    pass

class TexDoc():
    """Defines a LaTeX document
    """
    preamble = ""
    document = ""
    has_preamble = False
    has_begindoc = False
    has_enddoc = False

    def is_empty_pagestyle_already(self):
        match = re.search(r"\\pagestyle{\s?empty\s?}", self.preamble)
        if match:
            return True
        return False

    def parse(self, latex, test=False):
        """
        parse the doc into preamble and document
        """
        ele_re_tuple = (
            (r"\documentclass",
             r"\\documentclass(\[[\w,= ]*\])?{\w*}"),
            (r"\begin{document}", r"\\begin\{document\}"),
            (r"\end{document}", r"\\end\{document\}")
        )
        ele_position_list = []
        required_ele_list = []
        # stripped_latex = self.comments_striped_source()
        has_ele = []

        for ele, pattern in ele_re_tuple:
            required_ele_list.append(ele)
            iter = re.finditer(pattern, latex)

            matched_indice = [m.start(0) for m in iter]
            matched_len = len(matched_indice)
            if matched_len == 0:
                if not test:
                    raise TexDocMissingElementError(
                        _("No %s found in latex source") % ele)
                else:
                    has_ele.append(False)
            elif matched_len > 1:
                raise TexDocParseError(
                    _("More than one %s found in latex source") % ele)
            else:
                if test:
                    has_ele.append(True)
                ele_position_list.append(matched_indice[0])

        if test:
            [self.has_preamble, self.has_begindoc, self.has_enddoc] = has_ele

        if not ele_position_list == sorted(ele_position_list):
            raise TexDocWrongElementOrderError(
                _("The occurance of %s are not in proper order")
                % ",".join(required_ele_list))

        [self.preamble, self.document] = latex.split((r"\begin{document}"))
        self.preamble = self.preamble.strip()
        self.document = self.document.split((r"\end{document}"))[0].strip()

        print self.preamble

        print self.document

        if not test:
            assert self.preamble is not None
            assert self.document is not None

    def as_latex(self):
        """Print LaTeX Document
        """
        latex = ""
        if self.empty_pagestyle:
            if not self.is_empty_pagestyle_already():
                self.preamble += "\n\\pagestyle{empty}\n"

        latex += self.preamble
        latex += "\\begin{document}\n"
        latex += self.document
        latex += "\\end{document}\n"

        return latex

    def __str__(self):
        return self.document()

    def __unicode__(self):
        return self.document()

    def __init__(self, text=None, preamble="", preamble_extra="", empty_pagestyle=False):
        """Try to parse latex document
        """
        if text:
            text = strip_comments(text)
            try:
                self.parse(text)
            except TexDocMissingElementError:
                self.parse(text, test=True)
                if self.has_preamble:
                    raise
                elif not preamble and not preamble_extra:
                    raise
                else:
                    if not self.has_begindoc:
                        text = "%s\n%s" % ("\\begin{document}", text)
                    if not self.has_enddoc:
                        text = "%s\n%s" % (text, "\\end{document}")

                    text = "%s\n%s\n%s" % (
                        strip_comments(preamble),
                        strip_comments(preamble_extra),
                        text)
                    self.parse(text)

            except:
                raise
        else:
            raise ValueError(_("No latex source code is provided."))

        self.empty_pagestyle = empty_pagestyle