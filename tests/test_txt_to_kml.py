import os
import unittest

from core.kml_file.write_kml_file import kml_writer
from core.txt_file.read_txt_file import read_txt_file

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")


class TestTxtToKml(unittest.TestCase):
    def test_txt_to_kml_conversion(self):
        test_file = os.path.join(DATA_FOLDER, "Battery Abandoned_RenewMap_point.txt")
        test_out_file = os.path.join(DATA_FOLDER, "Battery Abandoned_RenewMap_point.kml")

        with kml_writer(test_out_file) as write_node_group:
            for this_feature_nodes in read_txt_file(test_file):
                basename = os.path.basename(test_file)
                basename_noext = os.path.splitext(basename)[0]
                is_area = basename_noext.lower().endswith("area")
                write_node_group(this_feature_nodes, is_area=is_area)

    def test_txt_to_kml_conversion_2(self):
        test_file = os.path.join(DATA_FOLDER, "TouristAreas.txt")
        test_out_file = os.path.join("TouristAreas.kml")

        with kml_writer(test_out_file) as write_node_group:
            for this_feature_nodes in read_txt_file(test_file):
                basename = os.path.basename(test_file)
                basename_noext = os.path.splitext(basename)[0]
                is_area = basename_noext.lower().endswith("area")
                write_node_group(this_feature_nodes, is_area=is_area)


if __name__ == "__main__":
    unittest.main()
