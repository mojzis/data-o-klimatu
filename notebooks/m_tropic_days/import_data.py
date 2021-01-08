import pandas as pd


def parse_sheet(city, sheet_name):
    """Imports data from the excel spreadsheet,
    melts them into "long" format (days as rows) """
    data = pd.read_excel(
        city['file_name'],
        sheet_name=sheet_name,
        header=3
    )
    data = data.rename(columns={'rok': 'year', 'měsíc': 'month'})
    long_data = pd.melt(data, id_vars=['year', 'month'], var_name='day')
    long_data.dropna(inplace=True)
    long_data['day'] = pd.to_numeric(long_data.day, downcast='integer')
    long_data.sort_values(by=['year', 'month', 'day'], inplace=True)
    long_data['city'] = city['key']
    return long_data
