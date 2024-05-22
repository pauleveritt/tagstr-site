from typing import Sequence, Callable

from tagstr_site.tagtyping import Decoded, Interpolation

TagStringArgs = Sequence[Decoded | Interpolation]
TagStringCallable = Callable[[TagStringArgs], str]