import pandas as pd
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression
import numpy as np


def get_yearly_count(df, var_name):
    """ how many times a year was there a given type of day """
    rdf = df[['year', 'city', var_name]].groupby(by=['year', 'city'], as_index=False).sum()
    rdf['var_name'] = var_name + 's_src'
    rdf.rename(columns={var_name: 'val'}, inplace=True)
    return rdf


def add_moving(df, var_names, city):
    """ calculate moving average, add it as extra rows """
    rdf = pd.DataFrame()
    for var_name in var_names:
        cols = ['year', 'val']
        irdf = df[
            (df.city == city) &
            (df.var_name == var_name + 's_src')][cols].rolling(
            5, on='year').mean()
        irdf.insert(0, 'city', city)
        irdf.insert(0, 'var_name', var_name + 's_m5')
        rdf = rdf.append(irdf)
    # print(f'adding {len(rdf)} for {city}')
    return rdf


def add_line(df, city, var_name):
    """linear regression of a given variable and city name, adds 3 years forward"""
    new_var_name = var_name.replace('_src', '_line')
    lr = LinearRegression()
    rdf = pd.DataFrame()
    validation = {}
    filtered = df[(df.city == city) & (df.var_name == var_name)]
    years = filtered.year.to_numpy()
    max_year = filtered.year.max()
    more_years = np.append(years, [max_year + 1, max_year + 2, max_year + 3])
    X = years.reshape(-1, 1)
    X2 = more_years.reshape(-1, 1)
    Y = filtered.val.to_numpy()
    lr.fit(X, Y)
    line = lr.predict(X2)
    rdf['year'] = more_years
    rdf['var_name'] = new_var_name
    rdf['city'] = city
    rdf['val'] = line
    rdf['legend'] = city + '_' + new_var_name
    splits = KFold(n_splits=3, shuffle=True, random_state=42).split(X)
    residuals = []
    for train_ix, test_ix in splits:
        testfit = LinearRegression().fit(X[train_ix], Y[train_ix])
        y_pred = testfit.predict(X[test_ix])
        residuals.append(Y[test_ix] - y_pred)
    residuals = np.concatenate(residuals)
    validation['city'] = city
    validation['var_name'] = new_var_name
    validation['rmse'] = np.std(residuals)
    validation['mbe'] = np.mean(residuals)
    return rdf, validation


def prepare_reg(df):
    """helper for split regressions"""
    lr = LinearRegression()
    years = df.year.to_numpy()
    X = years.reshape(-1, 1)
    Y = df.val.to_numpy()
    lr.fit(X, Y)
    line = lr.predict(X)
    return line


def add_line_check(df, city, var_name, limit_year):
    """splits the regression on a given year to compare the slopes"""
    new_var_name = var_name.replace('_src', '_lch')
    rdf = pd.DataFrame()

    filtered = df[
        (df.city == city) &
        (df.var_name == var_name)
        ]
    filtered_before = filtered[filtered.year <= limit_year]
    filtered_after = filtered[filtered.year > limit_year]
    years = filtered.year.to_numpy()
    line_before = prepare_reg(filtered_before)
    line_after = prepare_reg(filtered_after)
    line = np.concatenate((line_before, line_after))
    rdf['year'] = years
    rdf['var_name'] = new_var_name
    rdf['city'] = city
    rdf['val'] = line
    rdf['legend'] = city + '_' + new_var_name
    return rdf
