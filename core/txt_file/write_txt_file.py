import os
import csv
from contextlib import contextmanager

from core.txt_file.constants import TXT_LIST_HEADERS
from core.txt_file.exceptions import EmptyFileError
from core.txt_file.logic import check_file_is_non_empty_txt_file


def get_txt_last_index(filepath):
    check_file_is_non_empty_txt_file(filepath)

    with open(filepath, "rb") as fi:
        try:
            fi.seek(-300, os.SEEK_END)
            data = fi.read()
        except OSError:
            data = fi.read()
            if len(data.splitlines()) < 2:
                data = b"-1\tnull\tnull\t0\tnull"

    return int(data.decode().splitlines()[-1].split("\t")[0])


@contextmanager
def txt_list_writer(filepath):
    mode = "w"

    if not filepath.endswith(".txt"):
        filepath = f"{filepath}.txt"

    filepath = os.path.abspath(os.path.join(filepath))

    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if os.path.isfile(filepath):
        mode = "a"

    try:
        last_index = get_txt_last_index(filepath)
    except (FileNotFoundError, EmptyFileError):
        with open(filepath, mode=mode, encoding="utf-8") as fo:
            headers_joined = "\t".join(TXT_LIST_HEADERS)
            header_row = f"{headers_joined}\n"
            fo.write(header_row)
        last_index = -1
        mode = "a"

    with open(filepath, mode=mode, encoding="utf-8", newline="") as fo:
        tsv_writer = csv.writer(fo, delimiter="\t")
        try:
            yield tsv_writer, last_index
        except Exception as e:
            raise Exception(f"CSV writing failed: {filepath}") from e
