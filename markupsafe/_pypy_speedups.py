import array
from __pypy__.builders import UnicodeBuilder

from markupsafe import Markup


ESCAPED_CHARS_TABLE_SIZE = 256
ESCAPED_CHARS_DELTA_LEN = array.array("l", [0]) * ESCAPED_CHARS_TABLE_SIZE
ESCAPED_CHARS_REPL = [""] * ESCAPED_CHARS_TABLE_SIZE
for c, repl in [
    ('"', u"&#34;"),
    ("'", u"&#39;"),
    ("&", u"&amp;"),
    ("<", u"&lt;"),
    (">", u"&gt;"),
]:
    ESCAPED_CHARS_DELTA_LEN[ord(c)] = len(repl)
    ESCAPED_CHARS_REPL[ord(c)] = repl

def escape(s):
    if hasattr(s, '__html__'):
        return s.__html__()
    s = unicode(s)

    i = 0
    delta = 0
    repls = 0
    # Find the total number of replacements, and their total distance.
    while i < len(s):
        c = ord(s[i])
        try:
            d = ESCAPED_CHARS_DELTA_LEN[c]
        except IndexError:
            pass
        else:
            delta += d
            # Obscene performance hack, d >> 2 returns 0 for 0 or 1 for 4 and 5
            # which are the only values that can be here.
            repls += d >> 2
        i += 1
        # Performance hack, can go away when PyPy's bridges are better
        # optimized
        del c
        del d
    # If there are no replacements just return the original string.
    if not repls:
        return s

    res = UnicodeBuilder(len(s) + delta)
    in_idx = 0
    # While there are still replcaements in the string.
    while repls > 0:
        repls -= 1
        next_escp = in_idx
        # Find the next escape
        while next_escp < len(s):
            if (ord(s[next_escp]) < len(ESCAPED_CHARS_DELTA_LEN) and
                ESCAPED_CHARS_DELTA_LEN[ord(s[next_escp])]):
                break
            next_escp += 1
        # If we moved anywhere between escapes, copy that data.
        if next_escp > in_idx:
            res.append_slice(s, in_idx, next_escp)
        res.append(ESCAPED_CHARS_REPL[ord(s[next_escp])])
        in_idx = next_escp + 1
        # Another performance hack
        del next_escp
    # If there's anything left of the string, copy it over.
    if in_idx < len(s):
        res.append_slice(s, in_idx, len(s))
    return Markup(res.build())


def escape_silent(s):
    """Like :func:`escape` but converts `None` into an empty
    markup string.
    """
    if s is None:
        return Markup()
    return escape(s)


def soft_unicode(s):
    """Make a string unicode if it isn't already.  That way a markup
    string is not converted back to unicode.
    """
    if not isinstance(s, unicode):
        s = unicode(s)
    return s
