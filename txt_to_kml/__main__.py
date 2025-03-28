import argparse
import os
from concurrent.futures import ThreadPoolExecutor

from core.kml_file.write_kml_file import kml_writer
from core.txt_file.read_txt_file import read_txt_file
from core.utilities import file_handler


def worker(option):
    with file_handler(option["output_file"], replace=option["replace"]) as filepath:
        with kml_writer(filepath) as write_node_group:
            for this_feature_nodes in read_txt_file(option["input_file"]):
                basename = os.path.basename(option["input_file"])
                basename_noext = os.path.splitext(basename)[0]
                is_area = basename_noext.lower().endswith("area")
                write_node_group(this_feature_nodes, is_area=is_area)

    return True


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
        else os.path.basename(filepath).replace(".txt", "") + args.output_suffix + ".kml"
    )

    return {
        "replace": args.replace,
        "input_file": filepath,
        "output_file": filepath if args.replace else os.path.join(output_folder, basename),
    }


def main():
    parser = argparse.ArgumentParser("TXT to KML")
    parser.add_argument(
        "-i",
        "--inputs",
        nargs="+",
        help="<Required> TXT filepaths or folders containing files to convert to kml",
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
        "-s",
        "--output-suffix",
        help="<Optional> Suffix to add to the output file name based on the input file name, if replace is False",
        default="",
        required=False,
    )
    parser.add_argument(
        "-o", "--output-folder", help="<Optional> Folder to put the output files in if replace is False", required=False
    )
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
