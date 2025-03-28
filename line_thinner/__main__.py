import argparse
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from core.txt_file.logic import get_node_name
from core.txt_file.read_txt_file import read_txt_file
from core.txt_file.write_txt_file import txt_list_writer
from core.utilities import file_handler
from line_thinner.line_thinner import reduce_points_in_a_line

DEFAULT_ALLOWED_ANGLE_DEVIATION = 1
DEFAULT_USE_WEIGHTED_TOLERANCE = False
DEFAULT_MAX_DISTANCE_FOR_WEIGHTING = 0.01
DEFAULT_ANGLE_FOR_WEIGHTING = 15
DEFAULT_REDUCE_AREA_TO_POINT = False
DEFAULT_AREA_TO_POINT_THRESHOLD = 100

config_file = "config.json"
if os.path.isfile(config_file):
    with open("config.json", "r") as fi:
        config_data = json.load(fi)
else:
    config_data = {}


def worker(option):
    with file_handler(option["output_file"], replace=option["replace"]) as filepath:
        counter = 0
        for this_feature_nodes in read_txt_file(option["input_file"]):
            feature_node_named_groups = defaultdict(list)

            for node in this_feature_nodes:
                name = get_node_name(node)
                feature_node_named_groups[name].append(node)

            for nodes in feature_node_named_groups.values():
                group_name = nodes[0]["name"] + ("-" + nodes[0]["sub_name"] if nodes[0]["sub_name"] else "")

                lon_lat_alt_coordinates = list(map(lambda x: [x["longitude"], x["latitude"], x["altitude"]], nodes))
                reduced_coordinates = reduce_points_in_a_line(lon_lat_alt_coordinates, **option["thinning_options"])

                with txt_list_writer(filepath) as (tsv_writer, last_index):
                    current_write_counter = 0
                    for coordinate in reduced_coordinates:
                        row = []
                        row.append(last_index + current_write_counter + 1)
                        row.append(coordinate[0])
                        row.append(coordinate[1])
                        row.append(coordinate[2])
                        row.append(group_name)
                        tsv_writer.writerow(row)

                        counter += 1
                        current_write_counter += 1

    return counter


def get_file_options(input_item, args):
    filepath = os.path.join(input_item)

    if args.output_folder and not os.path.isdir(args.output_folder):
        os.makedirs(args.output_folder, exist_ok=True)

    output_folder = (
        args.output_folder if args.output_folder and os.path.isdir(args.output_folder) else os.path.dirname(filepath)
    )
    basename = (
        os.path.basename(filepath)
        if args.replace
        else os.path.basename(filepath).replace(".txt", "") + args.output_suffix + ".txt"
    )

    return {
        "replace": args.replace,
        "input_file": filepath,
        "output_file": filepath if args.replace else os.path.join(output_folder, basename),
        "thinning_options": {
            "allowed_angle_deviation": args.allowed_angle_deviation
            if args.allowed_angle_deviation
            else config_data.get("allowed_angle_deviation", DEFAULT_ALLOWED_ANGLE_DEVIATION),
            "use_weighted_tolerance": args.use_weighted_tolerance
            if args.use_weighted_tolerance
            else config_data.get("use_weighted_tolerance", DEFAULT_USE_WEIGHTED_TOLERANCE),
            "max_distance_for_weighting": args.max_distance_for_weighting
            if args.max_distance_for_weighting
            else config_data.get("max_distance_for_weighting", DEFAULT_MAX_DISTANCE_FOR_WEIGHTING),
            "max_angle_for_weighting": args.max_angle_for_weighting
            if args.max_angle_for_weighting
            else config_data.get("max_angle_for_weighting", DEFAULT_ANGLE_FOR_WEIGHTING),
            "reduce_area_to_point": args.reduce_area_to_point
            if args.reduce_area_to_point
            else config_data.get("reduce_area_to_point", DEFAULT_REDUCE_AREA_TO_POINT),
            "threshold_area_in_meter_square": args.area_to_point_threshold
            if args.area_to_point_threshold
            else config_data.get("area_to_point_threshold", DEFAULT_AREA_TO_POINT_THRESHOLD),
        },
    }


def main():
    parser = argparse.ArgumentParser("Multipolygon fixer")
    parser.add_argument(
        "-i",
        "--inputs",
        nargs="+",
        help="<Required> TXT filepaths or folders containing files to be merged separated by space",
        required=True,
    )
    parser.add_argument(
        "-r",
        "--replace",
        dest="replace",
        help="<Optional> Replace the input file with the output, if not append a suffix",
        action="store_true",
    )
    parser.add_argument(
        "--use-distance-weighted",
        dest="use_weighted_tolerance",
        help="<Optional> Smaller distance between the points allow for higher angle deviation",
        action="store_true",
    )
    parser.add_argument(
        "--allowed-angle-deviation", help="<Optional> Angular deviation allowed from straight line", type=float
    )
    parser.add_argument(
        "--max-distance-for-weighting",
        help=(
            "<Optional> Distance under which lines get weighted, if using distance weighted.\n"
            "Distances above this will use 'allowed-angle-deviation' angle"
        ),
        type=float,
    )
    parser.add_argument(
        "--max-angle-for-weighting",
        help="<Optional> When using distance weighted, this will be the maximum angle for distance close to zero",
        type=float,
    )
    parser.add_argument(
        "-s",
        "--output-suffix",
        help="<Optional> Suffix to add to the output file name based on the input file name, if replace is False",
        default="_points_reduced",
        required=False,
    )
    parser.add_argument(
        "-o", "--output-folder", help="<Optional> Folder to put the output files in if replace is False", required=False
    )
    parser.add_argument("--reduce-area-to-point", action="store_true")
    parser.add_argument("--area-to-point-threshold", type=int, default=100)
    args = parser.parse_args()

    options = []

    for input_item in args.inputs:
        if os.path.isfile(input_item) and input_item.endswith(".txt"):
            options.append(get_file_options(input_item, args))
        elif os.path.isdir(input_item):
            folder_items = os.listdir(input_item)
            for item in folder_items:
                filepath = os.path.join(input_item, item)
                if os.path.isfile(filepath) and filepath.endswith(".txt"):
                    options.append(get_file_options(filepath, args))

    # Set up multithreading
    number_of_threads = 10
    with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
        results = executor.map(worker, options)

    for result in results:
        print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
