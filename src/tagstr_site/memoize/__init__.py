from typing import Sequence, Callable

from tagstr_site.typing import Decoded, Interpolation

TagStringArgs = Sequence[Decoded | Interpolation]
TagStringCallable = Callable[[TagStringArgs], str]