import os
import shutil
from uuid import uuid4
from contextlib import contextmanager
from tempfile import TemporaryDirectory


def replace_file_in_place(filepath, replace_with_filepath):
    basename = os.path.basename(filepath)
    root_name, extension = os.path.splitext(basename)
    backup_original = os.path.join(os.path.dirname(filepath), root_name + "_before" + extension)

    i = 1
    while os.path.isfile(backup_original):
        backup_original = os.path.join(os.path.dirname(filepath), root_name + "_before_" + str(i) + extension)
        i += 1

    shutil.copy(filepath, backup_original)
    shutil.move(replace_with_filepath, filepath)

    return backup_original


@contextmanager
def file_handler(filepath, replace=False):
        if not replace:
            yield filepath
        else:
            with TemporaryDirectory(suffix="_nvn_tool") as tempdir:
                try:
                    extension = os.path.splitext(filepath)[-1]
                    temp_filepath = os.path.join(tempdir, str(uuid4()) + extension)
                    yield temp_filepath
                except:
                    pass
                finally:
                    backup_file = replace_file_in_place(filepath, temp_filepath)
                    print(f"file {filepath} replaced with file {temp_filepath}, backed up original file to {backup_file}")
