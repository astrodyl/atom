import requests

from atom.core import utils
from atom.core.io import toml_utils, path_utils


class GroupMeNotifier:
    """

    Attributes
    ----------
    token : str

    url : str

    """
    def __init__(self, token: str, url: str):
        self.token = token
        self.url = url

    @classmethod
    def from_dict(cls, d: dict):
        """
        Instantiates a GroupMeNotifier object from a TOML file.

        Parameters
        ----------
        d : dict
            The dictionary containing the token and url.

        Returns
        -------
        GroupMeNotifier
            The instantiated GroupMeNotifier object.
        """
        config = toml_utils.read(path_utils.token_path()).get('groupme')

        # noinspection PyTypeChecker
        return cls(
            utils.get_dict_value(config, 'token'),
            utils.get_dict_value(d, 'url'),
        )

    def send(self, msg: str | dict) -> requests.models.Response:
        """
        Sends a message to the specified GroupMe group.

        Parameters
        ----------
        msg : str or dict
            The text content of the message to be sent.

        Returns
        -------
            The requests response object
        """
        if isinstance(msg, dict):
            msg = utils.stringify(msg)

        return requests.post(self.url, json={"bot_id": self.token, "text": msg})
