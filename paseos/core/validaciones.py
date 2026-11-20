from typing import Annotated

from pydantic import StringConstraints

_LETRA = r"[^\W\d_]"
_SEPARADOR = r"[ '\u2019-]"

PATRON_NOMBRE = rf"^{_LETRA}+(?:{_SEPARADOR}{_LETRA}+)*$"

Nombre = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=PATRON_NOMBRE),
]