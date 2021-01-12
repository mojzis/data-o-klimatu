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
# # Z čeho se vyrábí elektřina
# Srovnání států EU.
#
# Inspirace: [Fakta o klimatu](https://faktaoklimatu.cz/infografiky/elektrina-na-osobu-eu).  
# Data: [Fakta o klimatu](https://docs.google.com/spreadsheets/d/1SQSnRSfTQ5HVxVJvwj4igfl22hyblYVjDo_INceKy4I)

# %%
import pandas as pd
import plotly.express as px
import plotly.io as pio
from IPython.display import JSON


# %%
# %config Completer.use_jedi = False


# %%
source = pd.read_csv('energy_production_per_capita/data/countries_eu_per_capita.csv')
source

source.rename(columns={'Země':'country','Kategorie':'cat', 'Jednotka':'unit'}, inplace=True)
nrg = pd.melt(source, id_vars=['country', 'cat', 'unit'], var_name='year')

cats_to_ignore = [
    'Gas',
    'Other fossil',
    'Wind',
    'Solar',
    'Biomass and waste',
    'Hydro',
    'Population',
    'Production'
]
nrg = nrg[~nrg.cat.isin(cats_to_ignore)]

# %%
nrg.cat = nrg.cat.replace('[Gas + Other fossil]','Other fossil', regex=False)
nrg.cat = nrg.cat.replace('[Renewables]','Renewables', regex=False)

nrg.country = nrg.country.replace('Czechia', 'Czech Republic', regex=False)


nrg.value = nrg.value.str.replace(' ','', regex=False)

nrg.value = nrg.value.astype('float')

# %%
#### & (nrg.cat == 'Production')
# nrg_to_show = nrg[nrg.country.isin(['Bulgaria','Croatia','Sweden'])]
nrg_to_show = nrg
countries = sorted(nrg_to_show.country.unique().tolist())
number_of_columns = 6
number_of_rows = len(countries) // number_of_columns + 1
fig = px.area(
    nrg_to_show[nrg.cat != 'Demand'],
    x='year', 
    y='value',
    color='cat',
    facet_col='country',
    facet_col_wrap=number_of_columns,
    template='plotly_white',
    category_orders={'country': countries}
)


years = nrg_to_show.year.unique().tolist()
nrg_dem = nrg_to_show[nrg.cat == 'Demand']
fig.update_xaxes({'visible':False})
fig.update_yaxes({
    'title':{'text':''},
    'range':[0,18000],
    'tickvals': [0,5000,10000,15000]
})
fig.update_layout(
    height=750,
    legend_orientation='h',
    legend_y=1.1,
    legend_title_text='',
)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig.update_traces({'hovertemplate':'<b>%{y:.0f}</b><br>year:%{x}'})

# for i in range(len(countries)):
#     itext = i+1
#     show_legend= False
#     if i == 0:
#         itext = ''
#         show_legend= True
#     fig.add_scatter(
#         x=years,
#         y=nrg_dem[nrg_dem.country == countries[i]].value,
#         name='Demand',
#         line={'color':'black','width':1 },
#         xaxis=f'x{itext}',
#         yaxis=f'y{itext}',
#         showlegend=show_legend,
#         legendgroup='demand',
#     )

for row_idx, row_figs in enumerate(fig._grid_ref):
    for col_idx, col_fig in enumerate(row_figs):
        # the subplots as generated in a funny way, subplot 0 is in left bottom corner, hence this "magic"        
        i = abs(row_idx+1 - number_of_rows)*number_of_columns + col_idx 
        show_legend= False
        if i == 1:
            show_legend = True
        if i <= len(countries)-1:
            fig.add_scatter(
                x=years,
                y=nrg_dem[nrg_dem.country == countries[i]].value,
                name='Demand',
                line={'color':'red','width':1 },
#                 xaxis=f'x{itext}',
#                 yaxis=f'y{itext}',
                showlegend=show_legend,
                legendgroup='demand',
                row=row_idx+1,
                col=col_idx+1,
                hovertemplate='<b>%{y:.0f}</b><br>year:%{x}'
            )
    
fig

# %%
with open('energy_production_per_capita/ogimg.png','bw') as ogim:
    ogim.write(pio.to_image(
        fig,
        format='png',
        width=1400, 
        height=700,
        engine='kaleido'))



# %%
