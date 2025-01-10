import os
import unittest
from datetime import datetime

from astropy.coordinates import SkyCoord
from dateutil.tz import tzutc

from atom.responders.einstein import EinsteinJsonNotice


class MyTestCase(unittest.TestCase):
    """
    Tests the `EinsteinJsonNotice` class.

    Attributes
    ----------
    notice : EinsteinJsonNotice
        The EinsteinJsonNotice representation of the JSON file in
        `../resources/einstein.json`.
    """
    @classmethod
    def setUpClass(cls):
        cwd = os.path.dirname(__file__)

        with open(os.path.join(cwd, '..', 'resources', 'einstein.json'), 'r') as f:
            cls.notice = EinsteinJsonNotice(f.read())

    def test_parse_id(self) -> None:
        """ Tests the trigger/event ID parser. """
        self.assertEqual(int('01708973486'), self.notice.parse_id())

    def test_parse_instrument(self) -> None:
        """ Tests the instrument parser. """
        self.assertEqual('WXT', self.notice.parse_instrument())

    def test_parse_event_time(self) -> None:
        """ Tests event time parser. """
        event_time = datetime.strptime(
            "2024-03-01T21:46:05.13Z",
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        event_time = event_time.replace(tzinfo=tzutc())

        self.assertEqual(event_time, self.notice.event_time)

    def test_parse_coordinates(self) -> None:
        """ Tests the coordinates parser. """
        coords = self.notice.parse_coordinates()

        self.assertIsInstance(coords, SkyCoord)
        self.assertEqual(120, coords.ra.deg)
        self.assertEqual(40, coords.dec.deg)

    def test_parse_coordinates_error(self) -> None:
        """ Tests the coordinates error parser. """
        self.assertEqual(0.02, self.notice.parse_coordinates_error())

    def test_parse_image_snr(self) -> None:
        """ Tests the image snr parser. """
        self.assertEqual(1, self.notice.parse_image_snr())


if __name__ == '__main__':
    unittest.main()
