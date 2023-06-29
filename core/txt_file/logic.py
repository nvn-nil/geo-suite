import os
import math

from core.txt_file.constants import TXT_LIST_HEADERS
from core.txt_file.exceptions import FileNotTXTListError, EmptyFileError


def check_file_is_non_empty_txt_file(filepath):
    if not filepath.endswith(".txt"):
        raise FileNotTXTListError(f"File is not a txt file: {filepath}")

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    headers = None
    with open(filepath, "r") as fi:
        headers = fi.readline()

    if not headers:
        raise EmptyFileError(f"File is empty: {filepath}")

    headers = headers.strip().split("\t")

    if headers != TXT_LIST_HEADERS:
        raise FileNotTXTListError(
            f"File headers does not match the format: current = {headers}, expected = {TXT_LIST_HEADERS}"
        )


def is_ring_closed(ring):
    return ring[0]['id'] == ring[-1]['id']


def get_node(feature):
    feature_name, sub_name = get_feature_name(feature[-1].strip())
    prepared_node = { "longitude": float(feature[1]), "latitude": float(feature[2]), "altitude": float(feature[3]), "name": feature_name, "sub_name": sub_name }
    prepared_node["id"] = get_id(prepared_node)
    return prepared_node


def get_feature_name(name):
    name = name.strip()
    
    if "-" not in name:
        return name, None

    name_parts = name.split("-")

    try:
        int(name_parts[0])
        int(name_parts[1])
    except:
        return name, None
    
    return name_parts[0], name_parts[1]


def get_id(node, max_digits=8):
    return f"{round(node['longitude'], max_digits)},{round(node['latitude'], max_digits)}"


def nodes_equal(one, other, check_name=True):
    equal_latitude = math.isclose(one["latitude"], other["latitude"], rel_tol=1e-9)
    equal_longitude = math.isclose(one["longitude"], other["longitude"], rel_tol=1e-9)
    equal_altitude = math.isclose(one["altitude"], other["altitude"], rel_tol=1e-9)
    
    node_equal = equal_latitude and equal_longitude and equal_altitude

    if check_name:
        equal_name = one["name"] == other["name"]
        equal_sub_name = one["sub_name"] == other["sub_name"]
        node_equal = node_equal and equal_sub_name and equal_name
    
    return node_equal


def dedupe_nodes(nodes):
    if len(nodes) < 2:
        return nodes
    
    found_duplicates = False
    
    for i in range(1, len(nodes)):
        if nodes_equal(nodes[i - 1], nodes[i]):
            found_duplicates = True
            break
    
    if not found_duplicates:
        return nodes

    result = [nodes[0]]
    for i in range(1, len(nodes)):
        if nodes_equal(nodes[i - 1], nodes[i]):
            continue
        result.append(nodes[i])
    return result
