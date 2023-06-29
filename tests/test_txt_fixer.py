import unittest
import os
from tempfile import TemporaryDirectory

from txt_fixer.txt_fixer import fix_txt_file
from multipolygon_fixer.merge_rings import merge_rings, get_node

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

def get_nodes(features):
    return [get_node(feature) for feature in features]


class TestTxtFixer(unittest.TestCase):
    def test_txt_fixer_split_multipolygon(self):
        test_file = os.path.join(DATA_FOLDER, "TouristAreas.txt")

        with TemporaryDirectory() as tempdir:
            output_file = os.path.join(tempdir, "outfile.txt")
            res = fix_txt_file(test_file, output_file)
            self.assertTrue(res)

class TestMergeRings(unittest.TestCase):
    def test_merge_ring_simple(self):
        ring_1 = get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
        ])
        ring_2 = get_nodes([
            [1, 1, 8, 0, "1-2"],
            [1, 5, 8, 0, "1-2"],
            [1, 5, 1, 0, "1-2"],
            [1, 1, 1, 0, "1-2"],
        ])

        completed, incomplete = merge_rings([ring_1, ring_2])

        self.assertListEqual(completed, [get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
            [1, 5, 8, 0, "1-2"],
            [1, 5, 1, 0, "1-2"],
            [1, 1, 1, 0, "1-2"],
        ])])

    def test_merge_ring_more_extra_complete(self):
        ring_1 = get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
        ])
        ring_2 = get_nodes([
            [1, 10, 8, 0, "1-3"],
            [1, 5, 8, 0, "1-3"],
            [1, 5, 1, 0, "1-3"],
            [1, 10, 8, 0, "1-3"],
        ])
        ring_3 = get_nodes([
            [1, 1, 8, 0, "1-2"],
            [1, 5, 8, 0, "1-2"],
            [1, 5, 1, 0, "1-2"],
            [1, 1, 1, 0, "1-2"],
        ])

        completed, incomplete = merge_rings([ring_1, ring_2, ring_3])
        expected_complete = [
            get_nodes([
                [1, 10, 8, 0, "1-3"],
                [1, 5, 8, 0, "1-3"],
                [1, 5, 1, 0, "1-3"],
                [1, 10, 8, 0, "1-3"],
            ]),
            get_nodes([
                [1, 1, 1, 0, "1-1"],
                [1, 1, 4, 0, "1-1"],
                [1, 1, 8, 0, "1-1"],
                [1, 5, 8, 0, "1-2"],
                [1, 5, 1, 0, "1-2"],
                [1, 1, 1, 0, "1-2"],
            ])
        ]

        self.assertListEqual(completed, expected_complete)

    def test_merge_ring_more_extra_incomplete(self):
        ring_1 = get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
        ])
        ring_2 = get_nodes([
            [1, 10, 8, 0, "1-3"],
            [1, 5, 8, 0, "1-3"],
            [1, 5, 1, 0, "1-3"],
            [1, 10, 9, 0, "1-3"],
        ])
        ring_3 = get_nodes([
            [1, 1, 8, 0, "1-2"],
            [1, 5, 8, 0, "1-2"],
            [1, 5, 1, 0, "1-2"],
            [1, 1, 1, 0, "1-2"],
        ])

        completed, incomplete = merge_rings([ring_1, ring_2, ring_3])
        expected_complete = [
            get_nodes([
                [1, 1, 1, 0, "1-1"],
                [1, 1, 4, 0, "1-1"],
                [1, 1, 8, 0, "1-1"],
                [1, 5, 8, 0, "1-2"],
                [1, 5, 1, 0, "1-2"],
                [1, 1, 1, 0, "1-2"],
            ])
        ]
        expected_incomplete = [get_nodes([
            [1, 10, 8, 0, "1-3"],
            [1, 5, 8, 0, "1-3"],
            [1, 5, 1, 0, "1-3"],
            [1, 10, 9, 0, "1-3"],
        ])]

        self.assertListEqual(completed, expected_complete)
        self.assertListEqual(incomplete, expected_incomplete)

    def test_merge_multiple_rings(self):
        ring_1 = get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
        ])
        ring_2 = get_nodes([
            [1, 10, 8, 0, "1-3"],
            [1, 5, 8, 0, "1-3"],
            [1, 5, 1, 0, "1-3"],
            [1, 10, 9, 0, "1-3"],
        ])
        ring_3 = get_nodes([
            [1, 10, 9, 0, "1-4"],
            [1, 5, 8, 0, "1-4"],
            [1, 5, 1, 0, "1-4"],
            [1, 10, 8, 0, "1-4"],
        ])
        ring_4 = get_nodes([
            [1, 1, 8, 0, "1-2"],
            [1, 5, 8, 0, "1-2"],
            [1, 5, 1, 0, "1-2"],
            [1, 1, 1, 0, "1-2"],
        ])

        completed, incomplete = merge_rings([ring_1, ring_2, ring_3, ring_4])
        expected_complete = [
            get_nodes([
                [1, 10, 8, 0, "1-3"],
                [1, 5, 8, 0, "1-3"],
                [1, 5, 1, 0, "1-3"],
                [1, 10, 9, 0, "1-3"],
                [1, 5, 8, 0, "1-4"],
                [1, 5, 1, 0, "1-4"],
                [1, 10, 8, 0, "1-4"],
            ]),
            get_nodes([
                [1, 1, 1, 0, "1-1"],
                [1, 1, 4, 0, "1-1"],
                [1, 1, 8, 0, "1-1"],
                [1, 5, 8, 0, "1-2"],
                [1, 5, 1, 0, "1-2"],
                [1, 1, 1, 0, "1-2"],
            ])
        ]

        self.assertListEqual(completed, expected_complete)

    def test_merge_ring_one_reversed(self):
        ring_1 = get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
        ])
        ring_2 = get_nodes([
            [1, 1, 1, 0, "1-2"],
            [1, 5, 1, 0, "1-2"],
            [1, 5, 8, 0, "1-2"],
            [1, 1, 8, 0, "1-2"],
        ])

        completed, incomplete = merge_rings([ring_1, ring_2])

        self.assertListEqual(completed, [get_nodes([
            [1, 1, 8, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 1, 0, "1-1"],
            [1, 5, 1, 0, "1-2"],
            [1, 5, 8, 0, "1-2"],
            [1, 1, 8, 0, "1-2"],
        ])])

    def test_merge_ring_one_reversed_complex(self):
        ring_1 = get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
        ])
        ring_2 = get_nodes([
            [1, 5, 1, 0, "1-2"],
            [1, 5, 8, 0, "1-2"],
            [1, 1, 8, 0, "1-2"],
        ])
        ring_3 = get_nodes([
            [1, 5, 1, 0, "1-3"],
            [1, 5, 8, 0, "1-3"],
            [1, 1, 1, 0, "1-3"],
        ])

        completed, incomplete = merge_rings([ring_1, ring_2, ring_3])

        self.assertListEqual(completed, [get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 8, 0, "1-1"],
            [1, 5, 8, 0, "1-2"],
            [1, 5, 1, 0, "1-2"],
            [1, 5, 8, 0, "1-3"],
            [1, 1, 1, 0, "1-3"],
        ])])

    def test_merge_ring_interconnected_intermediate_endpoints(self):
        ring_1 = get_nodes([
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 2, 2, 0, "1-1"],
        ])
        ring_2 = get_nodes([
            [1, 3, 3, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 4, 4, 0, "1-1"],
        ])
        ring_3 = get_nodes([
            [1, 5, 5, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 1, 0, "1-1"],
        ])
        ring_4 = get_nodes([
            [1, 4, 4, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 6, 6, 0, "1-1"],
        ])
        ring_5 = get_nodes([
            [1, 3, 3, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 5, 5, 0, "1-1"],
        ])
        ring_6 = get_nodes([
            [1, 6, 6, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 2, 2, 0, "1-1"],
        ])

        completed, incomplete = merge_rings([ring_1, ring_2, ring_3, ring_4, ring_5, ring_6])

        self.assertListEqual(completed, [get_nodes([
            [1, 2, 2, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 1, 1, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 5, 5, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 3, 3, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 4, 4, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 6, 6, 0, "1-1"],
            [1, 1, 4, 0, "1-1"],
            [1, 2, 2, 0, "1-1"],
        ])])
