# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Změny teploty na Zemi
#
# Na různých místech Země se teplota zvyšuje různě rychle, podívejte se kde a jak.  
# Mapa ukazuje změny teploty mezi roky 1961 a 2019.  
# Inspirace: [Fakta o klimatu](https://faktaoklimatu.cz/infografiky/mapa-zmeny-teploty).  
# Barvy se na několika místech neshodují kvůli zaokrouhlení.  
# Data: [NASA](https://data.giss.nasa.gov/gistemp/maps/index_v4.html), [Fakta o klimatu](https://docs.google.com/spreadsheets/d/16bTWzt0y8Omne9xxjd3o1rpszF764ATaC5UpFO5Zd7I/edit?usp=sharing)

# %%
import pandas as pd
import geopandas as gp
import plotly.graph_objects as go
from shapely.geometry import box, Point, Polygon, LineString, LinearRing
import shapely.ops as sho
import plotly.graph_objects as go
import plotly.io as pio


# %%
# %config Completer.use_jedi = False

# %%
borders = [-2,-1,-0.5,-0.2,0.2,0.5,1,2.0,4,4.9]
bin_labels = borders[1:]

# %%
# file from the google spreadsheet by FOK.cz
zones = pd.read_csv("m_world_map/data/fok_temp_changes.csv")
# for some places there are no data, leave them out
zones = zones[zones.temp.notnull()]
zones['tg'] = pd.cut(zones.temp, borders, right=False, labels=bin_labels)


# %%
def split_to_avoid_holes(poly, rec_level = 0):
#     print(rec_level)
    hole = Polygon(poly.interiors[0].coords)
    exterior = LinearRing(poly.exterior.coords)
    line = sho.nearest_points(hole.centroid, exterior)
    line = LineString(line)
    
    minx, miny, maxx, maxy = poly.bounds
    bounding_box = box(minx, miny, maxx, maxy)
    a, b = line.boundary
    if a.x == b.x:  # vertical line
        extended_line = LineString([(a.x, miny), (a.x, maxy)])
    elif a.y == b.y:  # horizonthal line
        extended_line = LineString([(minx, a.y), (maxx, a.y)])
    else:
        # linear equation: y = k*x + m
        k = (b.y - a.y) / (b.x - a.x)
        m = a.y - k * a.x
        y0 = k * minx + m
        y1 = k * maxx + m
        x0 = (miny - m) / k
        x1 = (maxy - m) / k
        points_on_boundary_lines = [Point(minx, y0), Point(maxx, y1), 
                                    Point(x0, miny), Point(x1, maxy)]
        points_sorted_by_distance = sorted(points_on_boundary_lines, key=bounding_box.distance)
        extended_line = LineString(points_sorted_by_distance[:2])
    eidams = list(sho.split(poly, extended_line))
    for p in eidams[:]:
        if (len(p.interiors) > 0) & (rec_level < 8):
            eidams.remove(p)
            eidams.extend(split_to_avoid_holes(p, rec_level +1))
    return eidams


def nicer_poly(poly):
    distortion = 3
    if len(poly.exterior.coords) > 10:
        poly = poly.buffer(distortion, join_style=1).buffer(distortion * -1, join_style=1)

    return poly


def generate_shapes(zones, temp_group):
    df = zones[zones.tg == temp_group]

    gz_rows = gp.points_from_xy(x=df.lon, y=df.lat)
    gz = gp.GeoSeries(gz_rows)

    circles = gz.buffer(1)
    squares = circles.envelope
    unified = squares.unary_union
    polygons = []
    # sometimes a collection, sometimes a single poly    
    if type(unified) == Polygon:
        unified = [unified]
    unified = list(unified)
    polygons.extend(unified)

    for pol in polygons[:]:
        if len(pol.interiors) > 0:
            polygons.remove(pol)
            eidams = split_to_avoid_holes(pol)
            polygons.extend(eidams)

    nice_polygons = []
    for pol in polygons:
        nice_polygons.append(nicer_poly(pol))

    for pol in nice_polygons[:]:
        if len(pol.interiors) > 0:
            nice_polygons.remove(pol)
            eidams = split_to_avoid_holes(pol)
            nice_polygons.extend(eidams)
    
    shapes = []
    for pol in nice_polygons:
        if len(pol.interiors) > 0:
            display(pol)
        pol_points = pol.exterior.coords
        plpo = []
        #         TODO: improve !
        for p in pol_points:
            plpo.append({
                'lon': p[0],
                'lat': p[1]
            })
        points_on_map = pd.DataFrame(plpo)
        shapes.append(points_on_map)

    return shapes

polies = {}

for temp_group in bin_labels:
    shapes = generate_shapes(zones, temp_group)
    if len(shapes) > 0:
        polies[temp_group] = {'shapes': shapes}


# %%
def colors_for_chart():
    """ helper to provide colors, now manually entered to remain consistent with FOK.cz """
    return {
        -1: "#2596be",
        -0.5: "#79dbee",
        -0.2: "#b9f5b7",
        0.2: "#fefefe",
        0.5: "#fff766",
        1.0: "#ffc330",
        2.0: "#ff8f32",
        4.0: "#fe1e1d",
        4.9: "#aa0f0c",
    }


def create_scatter(df, name, fillcolor, show_legend=True):
    """ helper function to provide all necessary settings of the plot """
    return {
        "lon": df.lon,
        "lat": df.lat,
        "fill": "toself",
        "fillcolor": fillcolor,
        "mode": "none",
        "name": name,
        "legendgroup": name,
        "showlegend": show_legend,
        "opacity": 0.7,
    }


def create_figure(sorted_temps, polies):
    """Creates a scatter_geo chart comprising of a plot for each polygon.

    Had to do it this way, since I cant figure out how to plot polygons from geojson:
    https://community.plotly.com/t/geojson-data-in-scatter-geo-only-draws-points-not-areas/48804
    """
    colors = colors_for_chart()
    fig = go.Figure()
    for key in sorted_temps:
        first = True
        for poly in polies[key]["shapes"]:
            fig.add_scattergeo(
                **create_scatter(poly, key, colors[key], first)
            )
            first = False

    fig.update_geos(
        resolution=110,
        projection_type="orthographic",
        showrivers=True,
        riverwidth=2,
        showlakes=True,
        lakecolor="rgb(211, 242, 245)",
        oceancolor="rgb(211, 242, 245)",
        showocean=True,
    )
    fig.update_layout(
        height=500,
        margin={"r": 10, "t": 20, "l": 10, "b": 10},
        font={"family": "Ubuntu"},
        legend_traceorder="reversed",
        legend_tracegroupgap=0,
    )
    return fig


# %%
fig = create_figure(bin_labels, polies)

fig.show()

# %%
with open('m_world_map/ogimg.png','bw') as ogim:
    ogim.write(pio.to_image(
        fig,
        format='png',
        width=1400, 
        height=700,
        engine='kaleido'))

