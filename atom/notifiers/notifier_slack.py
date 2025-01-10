import requests

from atom.core import utils
from atom.core.io import toml_utils, path_utils


class SlackNotifier:
    """

    Attributes
    ----------
    token : str

    channel : str

    url : str

    """
    def __init__(self, token: str, channel: str, url: str):
        self.token = token
        self.channel = channel
        self.url = url

    @classmethod
    def from_dict(cls, d: dict):
        """
        Instantiates a SlackNotifier object from a TOML file.

        Parameters
        ----------
        d : dict
            The path to the TOML file.

        Returns
        -------
        SlackNotifier
            The instantiated SlackNotifier object.
        """
        config = toml_utils.read(path_utils.token_path()).get('slack')

        # noinspection PyTypeChecker
        return cls(
            utils.get_dict_value(config, 'token'),
            utils.get_dict_value(d, 'channel'),
            utils.get_dict_value(d, 'url'),
        )

    def send(self, msg: str | dict) -> requests.models.Response:
        """
        Sends a message to the specified Slack channel.

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

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        return requests.post(self.url, headers=headers, json={
            "channel": self.channel,
            "text": msg
        })
