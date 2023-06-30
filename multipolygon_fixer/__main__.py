import os
import argparse

from concurrent.futures import ThreadPoolExecutor

from core.txt_file.write_txt_file import txt_list_writer
from multipolygon_fixer.merge_rings import process_feature_nodes
from core.txt_file.read_txt_file import read_txt_file
from core.utilities import file_handler


def worker(option):
    with file_handler(option["output_file"], replace=option["replace"]) as filepath:
        counter = 0
        for this_feature_nodes in read_txt_file(option["input_file"]):
            completed_rings, incomplete_groups = process_feature_nodes(this_feature_nodes)
            with txt_list_writer(filepath) as (tsv_writer, last_index):
                current_write_counter = 0
                for nodes in completed_rings:
                    name = nodes[0]['sub_name']
                    for node in nodes:
                        row = []
                        row.append(last_index + current_write_counter + 1)
                        row.append(node['longitude'])
                        row.append(node['latitude'])
                        row.append(node['altitude'])
                        row.append(name)
                        tsv_writer.writerow(row)
                        
                        counter += 1
                        current_write_counter += 1
                
                for nodes in incomplete_groups:
                    name = nodes[0]['name'] + "-" + nodes[0]['sub_name']
                    for node in nodes:
                        row = []
                        row.append(last_index + current_write_counter + 1)
                        row.append(node['longitude'])
                        row.append(node['latitude'])
                        row.append(node['altitude'])
                        row.append(name)
                        tsv_writer.writerow(row)
                        
                        counter += 1
                        current_write_counter += 1

    return counter


def get_file_options(input_item, args):
    filepath = os.path.join(input_item)

    if args.output_folder and not os.path.isdir(args.output_folder):
        os.makedirs(args.output_folder, exist_ok=True)

    output_folder = args.output_folder if args.output_folder and os.path.isdir(args.output_folder) else os.path.dirname(filepath)
    basename =  os.path.basename(filepath) if args.replace else os.path.basename(filepath).replace('.txt', '') + args.output_suffix + ".txt"

    return {
        "replace": args.replace,
        "input_file": filepath,
        "output_file": filepath if args.replace else os.path.join(output_folder, basename)
    }


def main():
    parser = argparse.ArgumentParser("Multipolygon fixer")
    parser.add_argument("-i", "--inputs", nargs='+', help='<Required> TXT filepaths or folders containing files to be merged separated by space', required=True)
    parser.add_argument("-r", "--replace", dest="replace", help='<Optional> Replace the input file with the output, if not append a suffix', action="store_true")
    parser.add_argument(
        "-s",
        "--output-suffix",
        help='<Optional> Suffix to add to the output file name based on the input file name, if replace is False',
        default="_mutlipolygon_fixed",
        required=False
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        help='<Optional> Folder to put the output files in if replace is False',
        required=False
    )
    args = parser.parse_args()

    options = []

    for input_item in args.inputs:
        if os.path.isfile(input_item) and input_item.endswith('.txt'):
            options.append(get_file_options(input_item, args))
        elif os.path.isdir(input_item):
            folder_items = os.listdir(input_item)
            for item in folder_items:
                filepath = os.path.join(input_item, item)
                if os.path.isfile(filepath) and filepath.endswith('.txt'):
                    options.append(filepath)

    # Set up multithreading
    number_of_threads = 10
    with ThreadPoolExecutor(max_workers = number_of_threads) as executor:
        results = executor.map(worker, options)

    for result in results:
        print(result)

if __name__ == "__main__":  # pragma: no cover
    main()
