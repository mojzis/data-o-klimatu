import plotly.express as px


def chart_per_type(df, var_type, known_cities, cities):
    translation = {'ice': 'Ledové dny', 'tropical': 'Tropické dny'}
    df.sort_values(by=['city','var_name','year'], inplace=True)
    trofig = px.line(df[
                         (df.var_type == var_type) &
                         (df.calc_type.isin(['m5', 'line']))
                         ],
                     x='year',
                     y='val',
                     color='legend',
                     template='plotly_white',
                     )
    trofig.update_traces(patch={'line': {'width': 1}})
    trofig.update_traces(patch={'line': {'width': 4}, 'opacity': 0.5},
                         selector=lambda x: '_line' in x['name'])
    trofig.update_traces(patch={'line': {'width': 5, 'dash': 'dot'}, 'opacity': 0.5},
                         selector=lambda x: '_lch' in x['name'])
    trofig.update_traces(patch={'hovertemplate': 'Rok: %{x}<br>Počet dní: %{y:.2f}'})

    for ck in known_cities:
        trofig.update_traces(patch={'legendgroup': ck, 'line':{'color': cities[ck]['color']}},
                             selector=lambda x: f'{ck}_' in x['name'])
        trofig.update_traces(patch={'name': cities[ck]['name']},
                             selector=lambda x: (f'{ck}_' in x['name']) & ('_line' in x['name']))
        trofig.update_traces(patch={'name': cities[ck]['name'] + ' - klouz','showlegend': False},
                             selector=lambda x: (f'{ck}_' in x['name']) & ('_m5' in x['name']))

    trofig.update_layout(
#         title=f'{translation[var_type]}',
        legend_title_text='',
        legend_orientation='h',
        legend_y=1.1,
        hovermode='closest')
    return trofig


# trying to acheive a neatly organized chart as on the fok web
# sorting data to ensure fat lines are below other stuff ... lame but quick
# ALL[ALL.city == 'prg']
def nice_chart_city(df, city):
    fig = px.line(df.sort_values(by=['year', 'var_name']),
                  x='year',
                  y='val',
                  template='plotly_white',
                  color='var_name',
                  )
    fig.update_traces(patch={'line': {'width': 7}, 'opacity': 0.3},
                      selector=lambda x: '_line' in x['name'])
    fig.update_traces(patch={
        'line': {'width': 1},
        'mode': 'lines+markers',
        'marker': {'size': 3}},
        selector=lambda x: '_src' in x['name'])
    fig.update_traces(patch={'line': {'color': 'navy'}, 'legendgroup': 'ice'},
                      selector=lambda x: 'ice_' in x['name'])
    fig.update_traces(patch={'line': {'color': 'crimson'}, 'legendgroup': 'tropical'},
                      selector=lambda x: 'tropical_' in x['name'])
    fig.update_traces(patch={'hovertemplate': 'Rok: %{x}<br>Počet dní: %{y:.2f}<br>'})
    fig.update_layout(
        title=f'Dny - {city["name"]}',
        legend_title_text='Proměnné',
        hovermode='closest')
    fig.update_xaxes(patch={'title': {'text': 'Rok'}})
    fig.update_yaxes(patch={'title': {'text': 'Počet dní'}})
    return fig

def nice_chart_cities(df, known_cities, cities):
    fig = px.line(df.sort_values(by=['year', 'var_name']),
              x='year',
              y='val',
              template='plotly_white',
              color='legend',
              )
    fig.update_traces(patch={'line': {'width': 7}, 'opacity': 0.3},
                      selector=lambda x: '_line' in x['name'])
    # thin line for source data
    fig.update_traces(patch={
        'line': {'width': 1},
        'mode': 'lines+markers',
        'marker': {'size': 3}},
        selector=lambda x: '_src' in x['name'])
    # set colors - blue for ice, red for tropical    
    fig.update_traces(patch={'line': {'color': 'navy'}},
                      selector=lambda x: 'ice_' in x['name'])    
    fig.update_traces(patch={'line': {'color': 'crimson'}},
                      selector=lambda x: 'tropical_' in x['name'])
    # hide all but one    
    fig.update_traces(patch={'visible': 'legendonly'},
                      selector=lambda x: 'brn_' not in x['name'])
    fig.update_traces(patch={'showlegend': False})
    fig.update_traces(patch={'showlegend': True},
                     selector=lambda x: ('src' in x['name']) & ('ice_' in x['name']))
    fig.update_xaxes(patch={'title': {'text': 'Rok'}})
    fig.update_yaxes(patch={'title': {'text': 'Počet dní'}})
    fig.update_traces(patch={'hovertemplate': 'Rok: %{x}<br>Počet dní: %{y:.2f}<br>'})
    fig.update_layout(
#         title=f'Tropické a ledové dny',
        legend_title_text='',
        legend_orientation='h',
        legend_y=1.1,
        hovermode='closest')

    for ck in known_cities:
        fig.update_traces(patch={'legendgroup': ck},
                         selector=lambda x: f'{ck}_' in x['name'])
        fig.update_traces(patch={'name': cities[ck]['name']},
                             selector=lambda x: (f'{ck}_' in x['name']) & ('_src' in x['name']) & ('ice_' in x['name'])) 
    
    return fig