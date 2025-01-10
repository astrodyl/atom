import astropy.units as u
from datetime import timedelta

from atom.core import factories
from atom.core.io import path_utils, toml_utils
from atom.core.skynet.observation import Observation
from atom.database.db import Notice, Transient, Response


class Responder:
    """
    Responds to streamed GCN notices.

    Attributes
    ----------
    settings : dict
        The responder's settings.

    notifiers : list of `atom.notifiers.Notifier`
        Will be used to send notifications.

    notice : `atom.responders.*.notices.*`
        The deserialized notice.
    """
    def __init__(self, notice) -> None:
        self.settings = None
        self.notifiers = []
        self.notice = notice

        self.read()

    def read(self) -> None:
        """ Reads in the settings file. """
        self.read_settings()
        self.read_notification_settings()

    def read_settings(self) -> None:
        """ Reads in the settings file. """
        self.settings = toml_utils.read(path_utils.einstein_settings_path())

    def read_notification_settings(self) -> None:
        """ Reads in the notification section of the settings file. """
        notification = self.settings.get('notification')

        for section in notification:
            self.notifiers.append(
                factories.notifier(notification[section], section)
            )

    def get_transient(self):
        """
        Returns the `transient` entry for the notice, if it exists.

        Returns
        -------
        namedtuple or None
            The transient entry for the notice.
        """
        notice = Notice.get(
            col='trigger_id',
            val=self.notice.id,
            one_or_none=True
        )

        return Transient.get(
            col='id',
            val=notice.transient_id,
            one_or_none=True
        )

    def get_responses(self, active: bool = True):
        """
        Returns all the `response` entries for the transient.

        Parameters
        ----------
        active : bool, optional, default=True
            If `active` is `True`, only returns the response entries for which
            there is an active observation.

        Returns
        -------
        list of namedtuple
            The `response` entries for the transient.
        """
        responses = Response.get(
            col='transient_id',
            val=self.get_transient().id
        )

        if not active:
            return responses

        active_responses = []
        for resp in responses:
            obs =  Observation.get(resp.obs_id)

            if obs.state == 'active':
                active_responses.append(resp)

        return active_responses

    def is_new_notice(self) -> bool:
        """ Returns ``True`` if there is a notice with same trigger ID. """
        return Notice.get('trigger_id', self.notice.id) == []

    def known_transient(self) -> int | None:
        """
        Checks if the transient has been triggered by another observatory.

        Since observatories do not include information pertaining to other
        observatories triggers, we must search out database of transients
        for events that occurred at similar time and location. This is by
        no means a full-proof way, but unless observatories start including
        additional information, this is the best we can do.

        Returns
        -------
        int or None
            If previously triggered, returns transient ID.
        """
        match = Transient.search(
            ra_deg=self.notice.coords.ra.deg,
            dec_deg=self.notice.coords.dec.deg,
            range_deg=0.5,
            start_time=self.notice.event_time - timedelta(minutes=30),
            end_time=self.notice.event_time + timedelta(minutes=30),
            one_or_none=True
        )
        return match.id if match else None

    def new_event_message(self) -> str:
        """
        A boilerplate message for new events.

        Returns
        -------
        str
            The message for new events.
        """
        msg = (
            f"[ {self.notice.observatory} {self.notice.instrument} {self.notice.id} ]"
            f"\n\n"

            f"This is a new alert for a likely {self.notice.type} detection that "
            f"occurred at {self.notice.event_time} UT in the following location: "
            f"\n\n"
        )
        return msg + self.coordinates_message()

    def updated_event_message(self) -> str:
        """
        A boilerplate message for updated events.

        Returns
        -------
        str
            The message for updated events.
        """
        msg =(
            f"[ {self.notice.observatory} {self.notice.instrument} {self.notice.id} ]"
            f"\n\n"

            f"This an updated alert for the {self.notice.observatory} trigger "
            f"{self.notice.id}. The {self.notice.instrument} instrument updated "
            f"the coordinates to:\n\n"
        )
        return msg + self.coordinates_message()

    def coordinates_message(self) -> str:
        """
        A boilerplate message for the coordinates.

        Returns
        -------
        str
            The message for transient coordinates.
        """
        return (
            f"Right Ascension (J2000):\n"
            f"{round(self.notice.coords.ra, 3)} = "
            f"\t{self.notice.coords.ra.to_string(unit=u.hourangle, sep=':')} "
            f"(hh:mm:ss) +/- {round(self.notice.coords_error_deg * 60, 3)} arc min"
            f"\n\n"

            f"Declination (J2000):\n"
            f"{round(self.notice.coords.dec, 3)} = "
            f"{self.notice.coords.dec.to_string(unit=u.deg, sep=':')}"
            f"(dd:mm:ss) +/- {round(self.notice.coords_error_deg * 60, 3)} arc min"
            f"\n\n"

            f"Galactic longitude:\n"
            f"\t{round(self.notice.coords.galactic.l, 3)}"
            f"\n\n"

            f"Galactic latitude:\n"
            f"\t{round(self.notice.coords.galactic.b, 3)}"
            f"\n\n"
        )
