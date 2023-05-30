# %%
import pandas as pd
import requests

# %%


def extraer(start_date: str, end_date: str):
    """Función que extrae le precio del Brent en USD por medio de una API.
    Extrae la información de interes y la almacena en el Data Frame.

    Args:
        start_date (str): Fecha desde la que se obtendrán los datos.
        end_date (str): Fecha hasta la que se obtendrán los datos.

    Returns:
        pd.DataFrame: Data Frame con 5 columnas:
        date | Granularidad | Indicador | Unidad | Valor
    """
    url = 'https://www.alphavantage.co/query?function=BRENT&interval=monthly&apikey=1W4H8KKSYD89ZCZ4'
    r = requests.get(url, verify=False)
    data = r.json()

    df = pd.DataFrame(pd.json_normalize(data['data']))
    df['date'] = df['date'].map(lambda x: '-'.join(x.split('-')[::-1]))

    try:
        start = df[df['date'] == start_date].index[0]
    except IndexError:
        start = 0

    try:
        end = df[df['date'] == end_date].index[0]
    except IndexError:
        end = len(df) - 1

    df = df.loc[start:end, :].reset_index().drop(['index'], axis=1)

    df['Granularidad'] = 'Diario'
    df['Indicador'] = 'Brent'
    df['Unidad'] = 'USD'
    df['Valor'] = df['value']
    df.drop('value', axis=1, inplace=True)

    return df
