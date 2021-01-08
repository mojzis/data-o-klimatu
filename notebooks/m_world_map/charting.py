import plotly.graph_objects as go


def colors_for_chart():
    """ helper to provide colors, now manually entered to remain consistent with FOK.cz """
    return {
        -1.4: "#2596be",
        -1.2: "#2596be",
        -1.0: "#79dbee",
        -0.8: "#79dbee",
        -0.6: "#79dbee",
        -0.4: "#b9f5b7",
        -0.2: "#fefefe",
        0.0: "#fefefe",
        0.2: "#fefefe",
        0.4: "#fff766",
        0.6: "#ffc330",
        0.8: "#ffc330",
        1.0: "#ffc330",
        1.2: "#ff8f32",
        1.4: "#ff8f32",
        1.6: "#ff8f32",
        1.8: "#ff8f32",
        2.0: "#fe1e1d",
        2.2: "#fe1e1d",
        2.4: "#fe1e1d",
        2.6: "#fe1e1d",
        2.8: "#fe1e1d",
        3.0: "#fe1e1d",
        3.2: "#fe1e1d",
        3.4: "#fe1e1d",
        3.6: "#fe1e1d",
        3.8: "#fe1e1d",
        4.0: "#aa0f0c",
        4.2: "#aa0f0c",
        4.4: "#aa0f0c",
        4.6: "#aa0f0c",
        4.8: "#aa0f0c",
        5.0: "#aa0f0c",
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
        height=400,
        margin={"r": 10, "t": 20, "l": 10, "b": 10},
        font={"family": "Ubuntu"},
        legend_traceorder="reversed",
        legend_tracegroupgap=0,
    )
    return fig
