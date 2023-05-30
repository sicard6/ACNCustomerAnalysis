# %%
import base as bs
from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
import time
import sys
import os

# %%


def extraer(start_date: str, end_date: str):
    """Función que ingresa a la página de la OECD y descarga las
    los datos de paridad adquisitiva. 
    Extrae la información de interes y la almacena en el Data Frame.

    Args:
        start_date (str): Fecha desde la que se obtendrán los datos.
        end_date (str): Fecha hasta la que se obtendrán los datos.

    Returns:
        pd.DataFrame: Data Frame con 5 columnas:
        date | Granularidad | Indicador | Unidad | Valor
    """
    driver = bs.ejecutar_driver(
        'https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm')
    driver.find_element(
        By.XPATH, './/span[@class="download-btn-label"]').click()
    driver.find_element(
        By.XPATH, './/a[@class="download-indicator-button"]').click()

    time.sleep(10)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')

    df = pd.read_csv(fuente_archivo)
    df = df[df['LOCATION'] == 'COL'].loc[:, ['TIME', 'Value']].reset_index().drop([
        'index'], axis=1)

    aux_1 = start_date.split('-')
    aux_2 = end_date.split('-')

    try:
        start = df[df['TIME'] == int(aux_1[2])].index[0]
    except IndexError:
        start = 0

    try:
        end = df[df['TIME'] == int(aux_2[2])].index[0]
    except IndexError:
        end = len(df) - 1

    df['date'] = '01-01-'+df['TIME'].map(str)
    df['Granularidad'] = 'Anual'
    df['Indicador'] = 'Paridad de poder adquisitivo'
    df['Unidad'] = 'PPA'
    df.rename(columns={'Value': 'Valor'}, inplace=True)

    df = df.loc[start:end, ['date', 'Granularidad', 'Indicador',
                            'Unidad', 'Valor']].reset_index().drop(['index'], axis=1)

    os.remove(fuente_archivo)

    return df
