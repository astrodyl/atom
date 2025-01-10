from pathlib import Path


def project_root() -> Path:
    """
    Returns the project root directory.

    Returns
    -------
    Path
        The project root directory.
    """
    return Path(__file__).parent.parent.parent


# <editor-fold desc="Responder paths">
def responders_path() -> Path:
    """"""
    return project_root() / 'responders'


def einstein_path() -> Path:
    """"""
    return responders_path() / 'einstein'


def einstein_settings_path() -> Path:
    """"""
    return einstein_path() / 'settings' / 'settings.toml'


def swift_path() -> Path:
    """"""
    return responders_path() / 'swift'


def igwn_path() -> Path:
    """"""
    return responders_path() / 'igwn'
# </editor-fold>


def token_path() -> Path:
    """ Returns the path to the tokens TOML file. """
    return project_root() / '..' / 'tokens.toml'


def kafka_topics_path() -> Path:
    """"""
    return project_root() / 'kafka' / 'topics.toml'


def database_path() -> Path:
    """ Returns the path to the database file. """
    return project_root() / 'database' / 'atom.db'
