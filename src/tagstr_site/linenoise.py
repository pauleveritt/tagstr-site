# NOTE: got to support re as a prefix for this specific example (so `import re
# as re_module`)!
#
# But in practice the combination of interpolation support along with using
# functionality like re.VERBOSE might make this module actually useful with some
# more work.

import re as re_module
import string

from tagstr_site.tagtyping import Decoded, Interpolation
from tagstr_site.tstring import Template, t


def re(template: Template) -> re_module.Pattern:
    pattern = []
    for arg in template.args:
        match arg:
            case str():
                pattern.append(arg)
            case getvalue, _, _, formatspec:
                pattern.append(format(getvalue(), '' if formatspec is None else formatspec))

    return re_module.compile(''.join(pattern), re_module.VERBOSE)


def demo():
    line = string.printable

    print(re(t'a.*z').search(line))

    decoded = 'efg'
    print(re(t'a.*{decoded}').search(line))


if __name__ == '__main__':
    demo()
