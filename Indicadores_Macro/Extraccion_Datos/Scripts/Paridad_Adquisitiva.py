# %% [markdown]
# ### Paridad adquisitiva (varios países)
# [Link](https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm)

# %%
import base as bs
from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
import time
import sys
import os

# %%
path = 'C:/Users/'+os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Indicadores_Macro'

# start_date = sys.argv[1]
# end_date = sys.argv[2]

# %%


def extraer(start_date: str, end_date: str):
    """Función que ingresa a la página de la OECD y descarga las
    los datos de paridad adquisitiva. 
    Almacena el arcivo en la carpeta de data cruda.

    Args:
        driver (sel.webdriver.Edge): driver de selenium
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
    # bs.guardar_archivo(fuente_archivo, path+'/Data/Raw/Paridad_Adquisitiva.csv')
    return df


# %%
# extraer_PA(start_date, end_date)
