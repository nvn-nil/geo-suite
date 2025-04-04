import math
from math import pi, sin

import numpy as np

WGS84_RADIUS = 6378137


def rad(value):
    return value * pi / 180


def ring__area(coordinates):
    """
    Calculate the approximate _area of the polygon were it projected onto
        the earth.  Note that this _area will be positive if ring is oriented
        clockwise, otherwise it will be negative.

    Reference:
        Robert. G. Chamberlain and William H. Duquette, "Some Algorithms for
        Polygons on a Sphere", JPL Publication 07-03, Jet Propulsion
        Laboratory, Pasadena, CA, June 2007 http://trs-new.jpl.nasa.gov/dspace/handle/2014/40409

    @Returns

    {float} The approximate signed geodesic _area of the polygon in square meters.
    """

    assert isinstance(coordinates, (list, tuple))

    _area = 0
    coordinates_length = len(coordinates)

    if coordinates_length > 2:
        for i in range(0, coordinates_length):
            if i == (coordinates_length - 2):
                lower_index = coordinates_length - 2
                middle_index = coordinates_length - 1
                upper_index = 0
            elif i == (coordinates_length - 1):
                lower_index = coordinates_length - 1
                middle_index = 0
                upper_index = 1
            else:
                lower_index = i
                middle_index = i + 1
                upper_index = i + 2

            p1 = coordinates[lower_index]
            p2 = coordinates[middle_index]
            p3 = coordinates[upper_index]

            _area += (rad(p3[0]) - rad(p1[0])) * sin(rad(p2[1]))

        _area = _area * WGS84_RADIUS * WGS84_RADIUS / 2

    return _area


def polygon__area(coordinates):

    assert isinstance(coordinates, (list, tuple))

    _area = 0
    if len(coordinates) > 0:
        _area += abs(ring__area(coordinates))

    return _area


def reduce_small_areas_to_points(coordinates, threshold_area_in_meter_square=150):
    area = polygon__area(coordinates)

    if area <= threshold_area_in_meter_square:
        simple_centroid = np.mean(coordinates, axis=0).tolist()
        return [simple_centroid]

    return coordinates


def reduce_points_in_a_line(
    coordinates,
    allowed_angle_deviation=1,
    use_weighted_tolerance=False,
    max_distance_for_weighting=0.05,
    max_angle_for_weighting=25,
    reduce_area_to_point=False,
    threshold_area_in_meter_square=100,
    **kwargs
):
    """Given a list of coordinates remove redundant points in a line

    Optionally, allow a tolerance so a slight deviation from straightness is allowed in this check

    :param coordinates: list of coordinates
    :type coordinates: list
    :param allowed_angle_deviation: allowed max deviation of a point from the line drawn by the 2
        previous points to still be considered straight
    :type allowed_angle_deviation: Optional[float]
    """
    if reduce_area_to_point and len(coordinates) >= 3:
        coordinates = reduce_small_areas_to_points(
            coordinates, threshold_area_in_meter_square=threshold_area_in_meter_square
        )

    if len(coordinates) >= 3:

        prev_coordinate = None
        current_coordinate = None
        next_coordinate = None
        thinning_approach = (
            constant_angle_deviation_check if not use_weighted_tolerance else length_weighted_angle_deviation_check
        )
        thinning_function_kwargs = (
            {}
            if not use_weighted_tolerance
            else {"max_distance_for_weighting": max_distance_for_weighting, "max_angle": max_angle_for_weighting}
        )

        reduced_coordinates = []

        for i in range(len(coordinates)):
            current_coordinate = coordinates[i]

            if i == 0 or i == len(coordinates) - 1:
                reduced_coordinates.append(current_coordinate)
                continue

            if i > 0 and prev_coordinate is None:
                prev_coordinate = coordinates[i - 1]

            if i < len(coordinates) - 1:
                next_coordinate = coordinates[i + 1]

            if thinning_approach(
                prev_coordinate,
                current_coordinate,
                next_coordinate,
                allowed_angle_deviation=allowed_angle_deviation,
                **thinning_function_kwargs,
            ):
                reduced_coordinates.append(current_coordinate)
                prev_coordinate = None

        return reduced_coordinates

    return coordinates


def constant_angle_deviation_check(
    prev_coordinate, current_coordinate, next_coordinate, allowed_angle_deviation=1, **kwargs
):
    angle_prev_current_next = angle_between_3_points(prev_coordinate, current_coordinate, next_coordinate)
    angle_between_lines = 180 - angle_prev_current_next

    if angle_between_lines > allowed_angle_deviation:
        return True

    return False


def length_weighted_angle_deviation_check(
    prev_coordinate,
    current_coordinate,
    next_coordinate,
    allowed_angle_deviation=1,
    max_distance_for_weighting=0.05,
    max_angle=25,
):
    # https://sciencing.com/convert-latitude-longtitude-feet-2724.html
    # 1 degree is about 111,139 meters - we'll approximate this to assume 100000m
    # d > 0.0001        -   tolerance = allowed_angle_deviation
    # 0 <= d <= 0.0001  -   tolerance = linear_conversion from [0, 0.0001] to [allowed_angle_deviation, 15]
    distance_prev_next = distance_between_coordinates(prev_coordinate, next_coordinate)

    angle_prev_current_next = angle_between_3_points(prev_coordinate, current_coordinate, next_coordinate)
    angle_between_lines = 180 - angle_prev_current_next

    weighted_allowed_angle_deviation = allowed_angle_deviation
    if distance_prev_next <= max_distance_for_weighting:
        # linear_conversion of distance from [0, max_distance_for_weighting] to ~[allowed_angle_deviation, 15]
        weighted_allowed_angle_deviation = linear_conversion(
            distance_prev_next, 0, max_distance_for_weighting, max_angle, allowed_angle_deviation
        )

    if angle_between_lines > weighted_allowed_angle_deviation:
        return True

    return False


def linear_conversion(value, old_min, old_max, new_min, new_max):
    if (old_max - old_min) == 0:
        return new_min

    return (((value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min


def distance_between_coordinates(coordinate_a, coordinate_b):
    if coordinate_a is None or coordinate_b is None:
        return None

    dx_sq = math.pow(coordinate_b[0] - coordinate_a[0], 2)
    dy_sq = math.pow(coordinate_b[1] - coordinate_a[1], 2)
    dz_sq = math.pow(coordinate_b[2] - coordinate_a[2], 2)
    return math.sqrt(dx_sq + dy_sq + dz_sq)


def angle_between_3_points(point_a, point_b, point_c, round_to=5):
    distance_a_b = distance_between_coordinates(point_a, point_b)
    distance_b_c = distance_between_coordinates(point_b, point_c)
    distance_a_c = distance_between_coordinates(point_a, point_c)

    # Using law of cosines for a triangle
    sum_of_squares = pow(distance_a_b, 2) + pow(distance_b_c, 2) - pow(distance_a_c, 2)
    denominator = 2 * distance_a_b * distance_b_c

    if denominator == 0:
        # Happens when there are duplicate points, we'll consider the
        # angle between them is 180 i.e. on the straight line
        # So they get removed in the thinning process
        return 180

    cos_angle = round(sum_of_squares / denominator, 6)
    cos_inverse = math.acos(cos_angle)
    return round(math.degrees(cos_inverse), round_to)
