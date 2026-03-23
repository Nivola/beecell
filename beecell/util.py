# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte
from typing import Union

def b(s: str)->bytes:
    return s.encode("latin-1")

def u(s):
    return s


def ensure_binary(s:Union[str,bytes], encoding:str='utf-8', errors:str='strict')->bytes:
    """ensuer s is binary

    For Python 3:
      - `str` -> encoded to `bytes`
      - `bytes` -> `bytes`
    """
    if isinstance(s, bytes):
        return s
    if isinstance(s, str):
        return s.encode(encoding, errors)
    raise TypeError("not expecting type '%s'" % type(s))

def ensure_text(s:Union[str,bytes], encoding:str='utf-8', errors:str='strict')->str:
    """Coerce *s* to six.text_type.
    """
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    elif isinstance(s, str):
        return s
    else:
        raise TypeError("not expecting type '%s'" % type(s))



def ensure_str(s:Union[str,bytes], encoding='utf-8', errors='strict')->str:
    """Coerce *s* to `str`.
    """
    # Optimization: Fast return for the common case.
    if type(s) is str:
        return s
    elif  isinstance(s, bytes):
        return s.decode(encoding, errors)
    else :
        raise TypeError("not expecting type '%s'" % type(s))
    return s