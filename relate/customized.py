
# {{{ formatted full_name

# http://stackoverflow.com/a/30070664/3437454

CJK_RANGES = [
  {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},         # compatibility ideographs
  {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},         # compatibility ideographs
  {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},         # compatibility ideographs
  #{"from": ord(u"\U0002f800"), "to": ord(u"\U0002fa1f")}, # compatibility ideographs
  {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")},         # Japanese Kana
  {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},         # cjk radicals supplement
  {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
  {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
  #{"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
  #{"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
  #{"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
  #{"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
]

def verbose_blank(s):
    from django.utils.translation import ugettext_lazy as _
    if not s:
        return _("(blank)")
    else:
        return s

def is_cjk(char):
  return any([range["from"] <= ord(char) <= range["to"] for range in CJK_RANGES])

def format_full_name(first_name, last_name):
    joined = first_name + last_name
    if joined:
        if is_cjk(joined[0]):
            return "%s%s" % (verbose_blank(last_name), verbose_blank(first_name))

    return '%s %s' % (verbose_blank(first_name), verbose_blank(last_name))

#}}}
