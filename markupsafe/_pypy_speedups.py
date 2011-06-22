import array
from __pypy__.builders import UnicodeBuilder

from markupsafe import Markup


ESCAPED_CHARS_TABLE_SIZE = 63
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
    while i < len(s):
        c = ord(s[i])
        if c < len(ESCAPED_CHARS_DELTA_LEN) and ESCAPED_CHARS_DELTA_LEN[c]:
            delta += ESCAPED_CHARS_DELTA_LEN[c]
            repls += 1
        i += 1
        del c
    if not repls:
        return s

    res = UnicodeBuilder(len(s) + delta)
    in_idx = 0
    while repls > 0:
        repls -= 1
        next_escp = in_idx
        while next_escp < len(s):
            if (ord(s[next_escp]) < len(ESCAPED_CHARS_DELTA_LEN) and
                ESCAPED_CHARS_DELTA_LEN[ord(s[next_escp])]):
                break
            next_escp += 1
        if next_escp > in_idx:
            res.append_slice(s, in_idx, next_escp)
        res.append(ESCAPED_CHARS_REPL[ord(s[next_escp])])
        in_idx = next_escp + 1
        del next_escp
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
