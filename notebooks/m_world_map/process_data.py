import geopandas as gp
import pandas as pd


def generate_shapes(zones, rounded_temp):
    """ for a given rounded temperature finds all points,
    creates squares around them and unifies those into polygons,
    extracts the points of the polygons and provides lists of those so
    that we can build the individual pieces in plotly
    returns list of dataframes of points, representing individual polygons"""
    df = zones[zones.rt == rounded_temp]
    # TODO: since we are building the squares from the centre, we might do +1 here,
    # would have to figure out what that means (ie will lat 181 work ?)
    gz_rows = gp.points_from_xy(x=df.lon, y=df.lat)
    gz = gp.GeoSeries(gz_rows)
    # apparently the gp way to create squares is to do envelopes for circles :)
    circles = gz.buffer(1)
    squares = circles.envelope
    unified = squares.unary_union
    # it looks like the simplification doesnt really improve it, so we dont do it now
    # simplified = unified.simplify(1,preserve_topology=True)
    points = []
    # review "exterior.coords", may leave out parts, see discussion here
    # https://stackoverflow.com/questions/58844463/how-to-get-a-list-of-every-point-inside-a-multipolygon-using-shapely
    try:
        for polygon in unified:
            points.append(polygon.exterior.coords)
    # in some cases, its only 1 polygon, not a list
    except Exception as e:
        points.append(unified.exterior.coords)
    shapes = []
    for pol in points:
        plpo = []
        #         TODO: improve !
        for p in pol:
            plpo.append({
                'lon': p[0],
                'lat': p[1]
            })
        points_on_map = pd.DataFrame(plpo)
        shapes.append(points_on_map)

    return shapes
