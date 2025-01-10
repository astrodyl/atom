import os
import unittest

from atom.database.db import Notice, Transient
from atom.responders.einstein import EinsteinJsonNotice
from atom.responders.einstein.einstein import EinsteinResponder


class MyTestCase(unittest.TestCase):
    """ Tests the `atom.db.notice.Notice` methods. """
    @classmethod
    def setUpClass(cls):
        cwd = os.path.dirname(__file__)

        with open(os.path.join(cwd, '..', 'resources', 'einstein.json'), 'r') as f:
            cls.file   = f.read()
            cls.notice = EinsteinJsonNotice(cls.file)

    def test_add(self) -> None:
        """"""
        Notice.add(self.notice, 2)

    def test_get(self) -> None:
        """ """
        self.assertEqual(1, Notice.get('id', 1, one_or_none=True).id)

    def test_search(self):
        """"""
        rows = Transient.search(
            59, 44, 2,
            '2025-01-08 12:34:55.000', '2025-01-08 12:34:57.000'
        )

    def test_responder(self):
        """"""
        responder = EinsteinResponder(self.file)
        responder.respond()

if __name__ == '__main__':
    unittest.main()
