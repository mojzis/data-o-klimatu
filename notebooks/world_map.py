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
# Inspirace: [Fakta o klimatu](https://faktaoklimatu.cz/infografiky/mapa-zmeny-teploty).  
# Barvy se na několika místech neshodují kvůli zaokrouhlení.  
# Data: [NASA](https://data.giss.nasa.gov/gistemp/maps/index_v4.html), [Fakta o klimatu](https://docs.google.com/spreadsheets/d/16bTWzt0y8Omne9xxjd3o1rpszF764ATaC5UpFO5Zd7I/edit?usp=sharing)

# %%
# %reload_ext autoreload
# %autoreload 2

import pandas as pd

from m_world_map.process_data import *
from m_world_map.charting import *


# %%
# %config Completer.use_jedi = False

# %%
def round_better(x, d=2):
    return round(x * 10 / d) * d / 10

# file from the google spreadsheet by FOK.cz
zones = pd.read_csv("m_world_map/data/fok_temp_changes.csv")
# for some places there are no data, leave them out
zones = zones[zones.temp.notnull()]
# rounding the temperature by 0.2 C to get a reasonable amount of areas
zones["rt"] = zones.temp.apply(round_better)
rt_list = zones.groupby(by="rt", as_index=False).count()[["rt", "temp"]]
rt_list.rename(columns={"temp": "tcount"}, inplace=True)
temps_to_show = zones.rt.unique().tolist()


# %%
polies = {}

for rounded_temp in temps_to_show:
    shapes = generate_shapes(zones, rounded_temp)
    if len(shapes) > 0:
        polies[rounded_temp] = {'shapes': shapes}


# %%
fig = create_figure(sorted_temps, polies)

fig.show()
