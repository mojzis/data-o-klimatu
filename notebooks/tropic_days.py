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
# # Tropické a ledové dny
#
# Inspirace: [Fakta o klimatu](https://faktaoklimatu.cz/infografiky/tropicke-dny-brno).  
# Data: [ČHMU](http://portal.chmi.cz/historicka-data/pocasi/denni-data/data-ze-stanic-site-RBCN)

# %% cell_id="00000-ede5d12f-9c26-4202-8a81-c73345b04e05" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=895 execution_start=1609771864303 source_hash="dc007c46"
# %load_ext autoreload
# %autoreload 2
# %config Completer.use_jedi = False

import pandas as pd
import plotly.express as px

from m_tropic_days.charting import *
from m_tropic_days.import_data import parse_sheet
from m_tropic_days.process_data import get_yearly_count, add_moving, add_line, add_line_check


# %% cell_id="00002-e9b6be71-0182-4253-a727-bdb07c84062c" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=1 execution_start=1609772200554 source_hash="cbdfb499"
# TODO fetch files automatically from CHMU
# https://www.chmi.cz/files/portal/docs/meteo/ok/denni_data/files/O1MOSN01.xls
colors = ["#56ebd3", "#851e39", "#65d04b", "#9b3ec8", "#a9c358", "#1c4c5e", "#99ceeb", "#1f3ca6", "#f67fec", "#458612"]

cities_old = {
    'prg' : {'name': 'Praha', 'file_name': 'P1PRUZ01.xls'},
    'brn' : {'name': 'Brno', 'file_name': 'B2BTUR01.xls'},
    'prb' : {'name': 'Přibyslav', 'file_name': 'P3PRIB01.xls'},
    'pri' : {'name': 'Přimda', 'file_name': 'L2PRIM01.xls'},
    'koc' : {'name': 'Kocelovice', 'file_name': 'C1KOCE01.xls'},
    'mos' : {'name': 'Mošnov', 'file_name': 'O1MOSN01.xls'},
    'lib' : {'name': 'Liberec', 'file_name': 'U2LIBC01.xls'},
    'mil' : {'name': 'Milešovka', 'file_name': 'U1MILE01.xls'},
    'lys' : {'name': 'Lysá hora', 'file_name': 'O1LYSA01.xls'},
    'kra' : {'name': 'Kramolín', 'file_name': 'P3KOSE01.xls'},
}

city_keys = sorted(cities_old.keys())

cities = {}

for city in city_keys:
    cities[city] = cities_old[city]
    cities[city]['color'] = colors.pop()


    
sheet_name = 'teplota maximální'


# %% cell_id="00004-6f3eca9f-7cbd-4c4f-96cc-a6f76830c231" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=4738 execution_start=1609772203124 source_hash="b36a88ed"
all_days = pd.DataFrame()
for city_key, city in cities.items():
    city['key'] = city_key
    all_days = all_days.append(parse_sheet(city, sheet_name))

# add columns for ice_day and tropical day according to the definition on Fakta o Klimatu
all_days['ice_day'] = all_days.value < 0
all_days['ice_day'] = all_days['ice_day'].astype(int)
all_days['tropical_day'] = all_days.value > 30
all_days['tropical_day'] = all_days['tropical_day'].astype(int)

# %% cell_id="00006-e2feda6f-ad96-4c26-a2cb-0602f4bd9c39" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=13 execution_start=1609772228662 source_hash="110e03fb"
ALL = pd.DataFrame()
var_names = ['ice_day', 'tropical_day']

for var_name in var_names:
    ALL = ALL.append(get_yearly_count(all_days, var_name))

ALL['legend'] = ALL.city + '_' + ALL.var_name


# %% cell_id="00007-8e94a35b-33b0-45e6-b9ba-712e911e39e4" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=1 execution_start=1609772236447 source_hash="d2da4a64"
# todo - this needs to be better :)
def content_stats():
    """helper function to be able to check quickly all necessary data is available """
    ALL['var_type'] = ALL.var_name.str.split('_', expand=True)[0]
    ALL['calc_type'] = ALL.var_name.str.split('_', expand=True)[2]
    return ALL[['city','var_type','calc_type','val']].groupby(by=['city','var_type','calc_type']).count()


# %% source_hash cell_id="00010-163c5f1e-2b68-4077-b268-bcf4a7db5c93" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=93 execution_start=1609772361958 output_cleared=true
for city in cities:
    ALL = ALL.append(add_moving(ALL, var_names, city))
    
ALL['legend'] = ALL.city + '_' + ALL.var_name

# %% source_hash cell_id="00012-d271d85f-ecc6-41f6-bce5-936000d397f2" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=213 execution_start=1609772385002 output_cleared=true

known_cities = ALL.city.unique().tolist()
known_var_names = ALL.var_name.unique().tolist()
hold_out_validation = pd.DataFrame()


for var_name in known_var_names:
    if '_src' in var_name:
        # drop existing line data in case its there
        ALL = ALL[(ALL.var_name != var_name.replace('_src','_line'))]        
        for city in known_cities:
            lines, validation = add_line(ALL, city, var_name)
            ALL = ALL.append(lines)
            hold_out_validation = hold_out_validation.append(validation, ignore_index=True)


# %% cell_id="00014-cc184098-da5f-47c8-aa02-25d7ea7bdc5e" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=163 execution_start=1609772430001 source_hash="9fbaae6b"
for var_name in known_var_names:
    # try breaking the line to see how the fitting copes
    if '_src' in var_name:
        # drop existing line data in case its there
        ALL = ALL[(ALL.var_name != var_name.replace('_src','_lch'))]        
        for city in known_cities:
            lines = add_line_check(ALL, city, var_name, 1997)
            ALL = ALL.append(lines)

# %% cell_id="00015-c818e6b0-3e4e-4604-8045-69ec7b7e1ecd" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=0 execution_start=1609772438550 source_hash="31d37885"
hold_out_validation['abs_mbe'] = hold_out_validation.mbe.abs()

# %% cell_id="00017-13f2f29e-ee34-4ce8-bf6f-6d3c3981d2ce" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=2 execution_start=1609772442737 source_hash="d2fb6f8e"
ALL['var_type'] = ALL.var_name.str.split('_', expand=True)[0]

# %% cell_id="00018-da0d2345-86e8-4ac4-914d-3942d3bc8e7e" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=7 execution_start=1609772444581 source_hash="eb6190fd"
ALL['calc_type'] = ALL.var_name.str.split('_', expand=True)[2]

# %% [markdown]
# ## Tropické a ledové dny

# %%
nice_chart_cities(ALL[ALL.calc_type != 'lch'], known_cities, cities)

# %% [markdown]
# ## Tropické dny

# %% cell_id="00020-7e013aad-2e2a-4c6b-8638-1ac78b3f877b" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=211 execution_start=1609772450547 pycharm={"is_executing": false} source_hash="5512e190"
chart_per_type(ALL, 'tropical', known_cities, cities)

# %% [markdown]
# ## Ledové dny

# %% cell_id="00021-1f929ebb-613f-499e-83b2-a4d2a63aff93" deepnote_cell_type="code" deepnote_to_be_reexecuted=false execution_millis=198 execution_start=1609772457009 source_hash="67fa7605"
chart_per_type(ALL, 'ice', known_cities, cities)
