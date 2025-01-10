from astropy.coordinates import SkyCoord
from dateutil import parser
from atom.core.io import json_utils


class EinsteinJsonNotice:
    """
    A container for Einstein Probe JSON notice data.

    Attributes
    ----------
    observatory : str
        The name of the observatory.

    type : str
        The type of transient event.

    record : object
        The deserialized Kafka message.

    id : int
        The notice/trigger ID.

    image_snr : float
        The SNR of the image.

    event_time : datetime.datetime
        The time of the event.

    instrument : str
        The name of the instrument.

    coords : astropy.coordinates.SkyCoord
        The SkyCoord object containing the events sky location.

    coords_error_deg : float
        The error in coordinates measured in degrees.

    See Also
    --------
    Einstein Probe notice schema:
        https://gcn.nasa.gov/docs/schema/v4.2.0/gcn/notices/einstein_probe
    """
    observatory = 'Einstein Probe'
    type = 'fast x-ray'

    def __init__(self, record, parse: bool = True):
        self.record = json_utils.read(record)

        self.id = None
        self.image_snr = None
        self.event_time = None
        self.instrument = None

        self.coords = None
        self.coords_error_deg = None
        self.notice_time = None
        self.astrophysical = True

        if parse:
            self.parse()

    def __repr__(self):
        """ Returns `EinsteinJsonNotice(id=123, ra=60 deg, dec=45 deg)`. """
        class_name = self.__class__.__name__
        ra, dec = round(self.coords.ra.deg, 2), round(self.coords.dec.deg, 2)
        return f"{class_name}(id={self.id}, ra={ra} deg, dec={dec} deg)"

    def parse(self) -> None:
        """ Parses the deserialized Einstein Probe notice. """
        self.id = self.parse_id()
        self.instrument = self.parse_instrument()
        self.event_time = self.parse_event_time()
        self.image_snr = self.parse_image_snr()

        self.coords = self.parse_coordinates()
        self.coords_error_deg = self.parse_coordinates_error()

    def parse_id(self) -> int:
        """
        Parses the Einstein Probe notice ID.

        Returns
        -------
        int
            The notice/trigger ID number.
        """
        trigger_id = json_utils.get_value(self.record, 'id')

        if isinstance(trigger_id, list):
            # EP notices stores the ID as a list for some reason.
            return int(trigger_id[0])

        # noinspection PyTypeChecker
        return int(trigger_id)

    def parse_instrument(self) -> str:
        """
        Parses the Einstein Probe instrument name.

        Returns
        -------
        str
            The name of the instrument.
        """
        # noinspection PyTypeChecker
        return json_utils.get_value(self.record, 'instrument')

    def parse_event_time(self):
        """
        Parses the Einstein Probe event time.

        Returns
        -------
        datetime.datetime
            The datetime of the event time.
        """
        # noinspection PyTypeChecker
        return parser.isoparse(
            json_utils.get_value(self.record, 'trigger_time')
        )

    def parse_image_snr(self) -> float:
        """
        Parses the Einstein Probe image snr.

        Returns
        -------
        float
            The snr of the image.
        """
        # noinspection PyTypeChecker
        return json_utils.get_value(self.record, 'image_snr', required=False)

    def parse_coordinates(self) -> SkyCoord:
        """
        Parses Einstein Probe notice coordinates.

        Returns
        -------
        astropy.coordinates.SkyCoord
            The coordinates of the event.
        """
        return SkyCoord(
            ra=self.record.get('ra'),
            dec=self.record.get('dec'),
            unit='deg',
        )

    def parse_coordinates_error(self) -> float:
        """
        Parses Einstein Probe notice coordinates error.

        Returns
        -------
        float
            The error (measured in degrees) of the coordinates.
        """
        return self.record.get('ra_dec_error')
