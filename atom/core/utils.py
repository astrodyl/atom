

def stringify(d: dict) -> str:
    """
    Converts a dictionary to a string with each key-value pair on a new line.

    Parameters
    ----------
    d : dict
        The dictionary to be converted

    Returns
    -------
        The string containing the dictionary contents.
    """
    return '\n'.join(f'{k}: {v}' for k, v in d.items())


def get_dict_value(d: dict, key: str, quiet: bool = False, required: bool = True):
    """
    Returns the value of ``d`` at ``key``, providing convenience options.

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

    Raises
    ------
    KeyError
        If `key` is not present in `d`.

    ValueError
        If value in ``key`` is ``None`` and `required` is ``True``.
    """
    val = None

    try:
        val = d.get(key)
    except KeyError as e:
        if not quiet:
            raise e

    if val is None and required:
        raise ValueError(
            f"Value at {key} is missing. If this value is optional, "
            f"call this method using `required=True`."
        )

    return val
