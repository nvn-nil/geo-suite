import os
from contextlib import contextmanager

from core.kml_file.logic import write_node_group


@contextmanager
def kml_writer(filepath):
    mode = "w"

    if not filepath.endswith(".kml"):
        filepath = f"{filepath}.kml"

    filepath = os.path.abspath(os.path.join(filepath))

    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, mode=mode, encoding="utf-8", newline="") as fo:

        def write_node_group_callback(nodes, **kwargs):
            write_node_group(nodes, fo, **kwargs)

        fo.write(
            """<?xml version="1.0" encoding="utf-8" ?>
                <kml xmlns="http://www.opengis.net/kml/2.2">
                    <Document id="root_doc">")
            """
        )
        try:
            yield write_node_group_callback
        except Exception as e:
            raise Exception(f"KML writing failed: {filepath}") from e
        finally:
            fo.write("\n</Document></kml>")
