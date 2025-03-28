import os
import unittest

from core.osm.loader import osm_loader

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")


class TestOsmLoader(unittest.TestCase):
    def test_osm_loader(self):
        file = os.path.join(DATA_FOLDER, "medium-small.osm")

        with osm_loader(file, None, "sample.sqlite") as con:
            print(con)
