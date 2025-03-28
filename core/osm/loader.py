import os
import sqlite3
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from tempfile import TemporaryDirectory


def extract_node_data(elem):
    elem_ref = elem.attrib["ref"]
    latitude = float(elem.attrib["lat"])
    longitude = float(elem.attrib["lon"])

    return elem_ref, latitude, longitude


@contextmanager
def osm_loader(filepath, output_folder, db_file=None):
    with TemporaryDirectory() as temp_dir:
        db_path = db_file if db_file else os.path.join(temp_dir, "data.sqlite")
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        cur.execute(
            "CREATE TABLE nodes (ref INTEGER PRIMARY KEY, latitude REAL NOT NULL, longitude REAL NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"  # noqa
        )
        cur.execute("CREATE TABLE ways (ref INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        cur.execute("CREATE TABLE relations (ref INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        cur.execute("CREATE TABLE tags (key TEXT NOT NULL, value TEXT NOT NULL, feature_ref INTEGER NOT NULL)")
        cur.execute(
            "CREATE TABLE way_node (node_ref INTEGER NOT NULL, way_ref INTEGER NOT NULL, PRIMARY KEY (way_ref, node_ref), FOREIGN KEY (node_ref) REFERENCES nodes(ref), FOREIGN KEY (way_ref) REFERENCES ways(ref))"
        )
        cur.execute(
            "CREATE TABLE relation_way (way_ref INTEGER NOT NULL, relation_ref INTEGER NOT NULL, PRIMARY KEY (relation_ref, way_ref), FOREIGN KEY (way_ref) REFERENCES ways(ref), FOREIGN KEY (relation_ref) REFERENCES relations(ref))"
        )
        cur.execute(
            "CREATE TABLE relation_node (node_ref INTEGER NOT NULL, relation_ref INTEGER NOT NULL, PRIMARY KEY (relation_ref, node_ref), FOREIGN KEY (node_ref) REFERENCES nodes(ref), FOREIGN KEY (relation_ref) REFERENCES relations(ref))"
        )
        con.commit()

        try:
            path = []
            for event, elem in ET.iterparse(filepath, events=("start", "end")):
                if event == "start":
                    path.append(elem)

                    elem_id = elem.attrib.get("ref", elem.attrib.get("id", None))
                    if elem_id is not None:
                        elem_id = int(elem_id)

                    try:
                        if elem.tag == "nd":
                            _, lat, lon = extract_node_data(elem)
                            cur.execute(f"INSERT INTO nodes(ref, latitude, longitude) VALUES({elem_id}, {lat}, {lon})")
                        elif elem.tag == "way":
                            cur.execute(f"INSERT INTO ways(ref) VALUES({elem_id})")
                        elif elem.tag == "relation":
                            cur.execute(f"INSERT INTO relations(ref) VALUES({elem_id})")
                    except Exception:
                        print(elem, elem.attrib)
                        raise
                elif event == "end":
                    if len(path) > 2:
                        parent_elem = path[-2]

                        if elem.tag in ["tag", "nd", "member"]:
                            try:
                                parent_id = int(parent_elem.attrib.get("id", parent_elem.attrib.get("ref")))
                            except Exception:
                                print(
                                    parent_elem,
                                    parent_elem.attrib,
                                    parent_elem.attrib.get("id"),
                                    parent_elem.attrib.get("ref"),
                                )
                                raise

                            if elem.tag == "tag":
                                key = elem.attrib["k"]
                                value = elem.attrib["v"]
                                cur.execute(f'INSERT INTO tags VALUES("{key}", "{value}", {parent_id})')
                            elif elem.tag == "nd":
                                if parent_elem.tag == "way":
                                    node_ref, lat, lon = extract_node_data(elem)
                                    cur.execute(f"INSERT INTO way_node VALUES({node_ref}, {parent_id})")
                            elif elem.tag == "member":
                                if parent_elem.tag == "relation":
                                    elem_id = int(elem.attrib["ref"])
                                    if elem.attrib["type"] == "node":
                                        cur.execute(f"INSERT INTO relation_node VALUES({elem_id}, {parent_id})")
                                    elif elem.attrib["type"] == "way":
                                        cur.execute(f"INSERT INTO relation_way VALUES({elem_id}, {parent_id})")
                    con.commit()
                    path.pop()

            yield None
        except Exception as e:
            con.close()
            raise Exception() from e
        finally:
            con.close()
