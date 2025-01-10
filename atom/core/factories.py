from atom.notifiers.notifier_groupme import GroupMeNotifier
from atom.notifiers.notifier_slack import SlackNotifier
from atom.responders.einstein.einstein import EinsteinResponder


def responder(message):
    """
    Returns the `Responder` object for the given `message`.

    Parameters
    ----------
    message :
        The kafka message.

    Returns
    -------
    Responder
        The `responder` instance.
    """
    if message.topic() == 'gcn.notices.einstein_probe.wxt.alert':
        return EinsteinResponder(message.value())

    raise ValueError('Unexpected topic!')


def notifier(d: dict, name: str):
    """
    Instantiates the `Notifier` with `d` for a given `name`.

    Parameters
    ----------
    d : dict
        The notifier data.

    name : str
        The name of the notifier.

    Returns
    -------
    Notifier
        The `Notifier` instance.
    """
    match name:
        case 'groupme':
            return GroupMeNotifier.from_dict(d)

        case 'slack':
            return SlackNotifier.from_dict(d)

        case _:
            raise ValueError(
                "Unsupported notifier. Must be 'groupme' or 'slack'."
            )
