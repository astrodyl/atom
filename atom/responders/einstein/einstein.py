import astropy.units as u

from atom.core.skynet.observation import Observation
from atom.database.db import Notice, Transient, Response
from atom.responders.einstein import EinsteinJsonNotice

from atom.responders.responder import Responder


class EinsteinResponder(Responder):
    """
    Responder for Einstein Probe notices.

    Responds in the following ways:
        - creates early and late time observations for new events.
        - updates existing events from updated notices.
        - notifies of new and updated events.
        - stores records in the database.
    """
    def __init__(self, notice):
        super().__init__(EinsteinJsonNotice(notice))

    def respond(self):
        """ Responds to the Einstein notice. """
        if self.is_new_notice():
            return self.respond_to_new_notice()

        return self.respond_to_update_notice()

    def respond_to_new_notice(self) -> None:
        """
        Responds to an Einstein notice for a new transient event.

        If the event is astrophysical in origin and is considered to be
        of interest, we schedule two observations. One that observed the
        early, rapid temporal evolution, and one that observes the late
        time, slower evolution.

        Notifications are then sent out with the event's information.

        In some cases, we may receive a notice from an observatory that they
        consider to be a new event, but that we already started observing via
        a notice from another, faster responding observatory. In this case, we
        do not respond to the new notice. In the future, we may want to update
        the coordinates if the new notice has a better localization.
        """
        transient_id = None

        if self.notice.astrophysical and self.is_interesting():

            if (transient_id := self.known_transient()) is None:
                early_obs = self.schedule_early_follow_up()
                Response.add(early_obs.id, transient_id)

                self.notify_new_event(early_obs.id)

        if transient_id is None:
            transient_id = Transient.add(self.notice)

        Notice.add(self.notice, transient_id)

    def is_interesting(self) -> bool:
        """
        Determines if the event is interesting (worth observing).

        The Einstein Probe observatory often triggers on uninteresting events
        near the galactic plane. We do not respond to events occurring within
        four degrees of the plane.

        Returns
        -------
        bool
            ``True`` if the event is interesting.
        """
        return abs(self.notice.coords.galactic.b) > 4.0 * u.deg

    def schedule_early_follow_up(self):
        """
        Schedules the early follow-up observation.

        The early observation uses the Campaign Manager to capture any
        potential temporal evolution in the early moments.

        Returns
        -------

        """
        return Observation.add(
            self.settings.get('observation').get('early'),
            self.notice
        )

    def schedule_late_follow_up(self):
        """
        Schedules the late-time follow-up observation.

        Returns
        -------

        """
        pass

    def respond_to_update_notice(self) -> None:
        """
        Updates active observations according to the updated notice.

        If previous notices considered the transient to be astrophysical, but
        the updated notice does not, flags the `transient` entry to no longer
        be astrophysical which will prevent further updates to this transient.
        """
        transient = self.get_transient()
        responses = self.get_responses()

        # Transient is no longer considered to be astrophysical in origin
        if transient.astrophysical and not self.notice.astrophysical:
            Transient.set_false_alarm(transient.id)

        # Transient is astrophysical, interesting, and still being observed
        elif self.is_interesting() and responses:
            for resp in responses:
                Observation.update(resp.obs_id, self.notice)
                Transient.update(resp.transient_id, self.notice)

            self.notify_update_event(responses)

        Notice.add(self.notice, transient.id)

    def notify_new_event(self, obs_id: int) -> None:
        """
        Sends out a notification via every notifier in ``notifiers``.

        Parameters
        ----------
        obs_id : int
            TODO: will change to tuple of obs ids (size == 2)
        """
        msg = self.new_event_message()

        msg += (
            f"Observations\n"
            f"------------\n"
            f"Early Time Obs: https://skynet.unc.edu/obs/view?id={obs_id}\n"
            # f"Late Time Obs: https://skynet.unc.edu/obs/view?id={obs_ids[1]}\n"
            f"\n\n"
        )

        for n in self.notifiers:
            n.send(msg)

    def notify_update_event(self, responses) -> None:
        """
        Sends out a notification via every notifier in ``notifiers``.

        Parameters
        ----------
        responses : list of namedtuple
            The list of responses that have been updated.
        """
        msg = (
                self.updated_event_message() +
                f"The following observations were updated: " +
                ', '.join([r.obs_id for r in responses])
        )

        for n in self.notifiers:
            n.send(msg)
