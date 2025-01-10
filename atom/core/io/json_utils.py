import json
from pathlib import Path

from atom.core import utils


def read(s, **kw) -> dict:
    """
    Reads JSON data from a string or file-like object.

    This method wraps `json.load` and `json.loads` to handle both string
    and file-like inputs. It accepts all keyword arguments supported by
    these methods and passes them along.

    Parameters
    ----------
    s : str or file-like object
        A ``json.read()``-supporting file-like object, ``str``, ``bytes``,
        or ``bytearray`` instance containing a JSON document.

    **kw : dict
        Additional keyword args passed to `json.load` or `json.loads`.

    Returns
    -------
    dict
        The deserialized JSON data.

    See Also
    --------
    ``json.load`` : For details on file-like object parsing.

    ``json.loads`` : For details on string parsing.
    """
    if isinstance(s, Path):
        with open(s, 'r') as f:
            s = f.read()

    if isinstance(s, (str, bytes, bytearray)):
        return json.loads(s, **kw)

    return json.load(s, **kw)


def get_value(d: dict, key: str, quiet: bool = False, required: bool = True):
    """
    Returns the value of ``d`` at ``key``.

    Parameters
    ----------
    d : dict
        The dictionary to get value from.

    key : str
        The key name to get.

    quiet : bool, optional
        If ``True``, ignores the KeyError (if raised).

    required : bool, optional
        If ``True``, allows the value at ``key`` to be ``None``.

    Returns
    -------
    any
        The value of `d[key]`.
    """
    return utils.get_dict_value(d, key, quiet, required)
