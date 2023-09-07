from core.txt_file.logic import is_ring_closed


def get_nodes_as_kml_coordinates(nodes):
    return list(map(get_node_as_kml_coordinates, nodes))


def get_node_as_kml_coordinates(node):
    return f"{node['longitude']},{node['latitude']},{node['altitude']}"


def write_node_group(nodes, fp, is_area=False):
    number_of_nodes = len(nodes)
    is_ring = is_ring_closed(nodes) and number_of_nodes > 3
    if is_ring and is_area:
        write_polygon(nodes, fp)
    elif is_ring:
        write_linear_ring(nodes, fp)
    elif number_of_nodes == 1:
        write_point(nodes[0], fp)
    else:
        write_linestring(nodes, fp)


def write_polygon(nodes, fp):
    coordinates = get_nodes_as_kml_coordinates(nodes)
    placemark = f"""\n
    <Placemark>
        <name>{nodes["name"] + ("-" + nodes["sub_name"] if nodes["sub_name"] else "")}</name>
        <Polygon>
            <altitudeMode>clampToGround</altitudeMode>
            <outerBoundaryIs>
                <LinearRing>
                    <altitudeMode>clampToGround</altitudeMode>
                    <coordinates>
                        {' '.join(coordinates)}
                    </coordinates>
                </LinearRing>
            </outerBoundaryIs>
        </Polygon>
    </Placemark>\n"""
    fp.write(placemark)


def write_linestring(nodes, fp):
    coordinates = get_nodes_as_kml_coordinates(nodes)
    name = nodes[0]["name"] + ("-" + nodes[0]["sub_name"] if nodes[0]["sub_name"] else "")
    placemark = f"""\n
    <Placemark>
        <name>{name}</name>
        <LineString>
            <extrude>1</extrude>
            <tessellate>1</tessellate>
            <coordinates>
                {' '.join(coordinates)}
            </coordinates>
        </LineString>
    </Placemark>\n"""
    fp.write(placemark)


def write_linear_ring(nodes, fp):
    coordinates = get_nodes_as_kml_coordinates(nodes)
    name = nodes[0]["name"] + ("-" + nodes[0]["sub_name"] if nodes[0]["sub_name"] else "")

    placemark = f"""\n
    <Placemark>
        <name>{name}</name>
        <LinearRing>
            <extrude>1</extrude>
            <tessellate>1</tessellate>
            <coordinates>
                {' '.join(coordinates)}
            </coordinates>
        </LinearRing>
    </Placemark>\n"""
    fp.write(placemark)


def write_point(node, fp):
    coordinate = get_node_as_kml_coordinates(node)
    name = node["name"] + ("-" + node["sub_name"] if node["sub_name"] else "")
    placemark = f"""\n
    <Placemark>
        <name>{name}</name>
        <LinearRing>
            <extrude>1</extrude>
            <tessellate>1</tessellate>
            <coordinates>{coordinate}</coordinates>
        </LinearRing>
    </Placemark>\n"""
    fp.write(placemark)
