from typing import Sequence, Callable

from tagstr_site import Thunk

TagStringArgs = Sequence[str | Thunk]
TagStringCallable = Callable[[TagStringArgs], str]