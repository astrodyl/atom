import json
from datetime import timedelta, timezone, datetime

from skynetapi import ObservationRequest
from atom.core.io import path_utils, toml_utils


# TODO: This should be moved to the skynetapi library

class Observation:
    def __init__(self):
        pass

    @staticmethod
    def add(data: dict, notice):
        """
        Schedules the Skynet observation.

        Uses the `observation` section in the Einstein settings file
        located in `path_utils.get_einstein_settings_path()`. Parameters
        that could not be known a priori are taken from the notice and
        set here as well.

        Returns
        -------

        """
        # Format the times to comply with the Skynet API
        event_time = notice.event_time.isoformat().split('+')[0]

        cancel_after_utc = (
                datetime.now(timezone.utc) + timedelta(data.pop('cancelAfterDays'))
        ).isoformat().split('+')[0]

        # Update the Observation Parameters
        data.update({'name': f"{notice.observatory}-{notice.id}"})
        data.update({'raHours': notice.coords.ra.deg / 15})
        data.update({'decDegs': notice.coords.dec.deg})
        data.update({'cancelAfterUtc': cancel_after_utc})

        # Update the Campaign Trigger Parameters
        data.get('trigger').update({'eventTime': event_time})
        data.update({'trigger': json.dumps(data.get('trigger'))})

        config = toml_utils.read(path_utils.token_path()).get('skynet')
        return ObservationRequest(config.get('token')).add(**data)

    @staticmethod
    def get(obs_id: str | int):
        """

        Returns
        -------

        """
        config = toml_utils.read(path_utils.token_path()).get('skynet')
        return ObservationRequest(config.get('token')).get(obs_id)

    @staticmethod
    def update(obs_id: str | int, notice):
        """"""
        data = {
            'raHours': notice.coords.ra.deg / 15,
            'decDegs': notice.coords.dec.deg
        }
        config = toml_utils.read(path_utils.token_path()).get('skynet')
        return ObservationRequest(config.get('token')).update(obs_id, **data)
