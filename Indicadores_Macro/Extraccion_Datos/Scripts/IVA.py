# %%
import base as bs
from selenium.webdriver.common.by import By
from datetime import datetime
import selenium as sel
import pandas as pd
import zipfile
import time
import glob
import sys
import os

# %%


def extraer(start_date: str, end_date: str):
    """Función que ingresa a la página de la DIAN y descarga las
    Estadísticas de Recaudo Mensual por Tipo de Impuesto. 
    Extrae la información de interes y la almacena en el Data Frame.

    Args:
        start_date (str): Fecha desde la que se obtendrán los datos.
        end_date (str): Fecha hasta la que se obtendrán los datos.

    Returns:
        pd.DataFrame: Data Frame con 5 columnas:
        date | Granularidad | Indicador | Unidad | Valor
    """
    driver = bs.ejecutar_driver(
        'https://www.dian.gov.co/dian/cifras/Paginas/EstadisticasRecaudo.aspx')
    iva = driver.find_elements(
        By.XPATH, './/div[@class="panel panel-default"]')[2]
    nombre_archivo = iva.find_element(
        By.XPATH, './/a').text.replace('í', 'i').replace(' ', '-').replace('---', '-')
    sec = iva.find_element(
        By.XPATH, './/div[@class="panel-collapse collapse"]')
    url_archivo = sec.find_element(By.XPATH, './/a').get_attribute('href')

    driver.get(url_archivo)

    time.sleep(20)
    driver.quit()

    path_to_zip_file = '/Users/'+os.getlogin()+'/Downloads/' + \
        nombre_archivo.capitalize()+'.zip'

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall('/Users/'+os.getlogin()+'/Downloads/')

    os.remove(path_to_zip_file)

    lista_de_archivos = glob.glob('/Users/'+os.getlogin()+'/Downloads/*')
    fuente_archivo = max(
        lista_de_archivos, key=os.path.getctime).replace('\\', '/')

    df = pd.read_excel(fuente_archivo, header=7)
    df.drop(df.tail(3).index, inplace=True)
    df.drop(0, inplace=True)
    df.rename(columns={'Unnamed: 0': 'Año'}, inplace=True)
    df['Año'] = df['Año'].map(lambda x: int(
        x.replace('(p)**', '').strip()) if isinstance(x, str) else x)

    aux_1 = start_date.split('-')
    aux_2 = end_date.split('-')

    try:
        start = df[(df['Año'] == int(aux_1[2]))].index[0]
    except IndexError:
        start = 0

    try:
        end = df[(df['Año'] == int(aux_2[2]))].index[0]
    except IndexError:
        end = len(df) - 1

    df['date'] = '01-01-'+df['Año'].map(str)
    df['Granularidad'] = 'Anual'
    df['Indicador'] = 'IVA'
    df['Unidad'] = 'COP'
    df.rename(columns={'IVA ': 'Valor'}, inplace=True)

    df = df.loc[start:end, ['date', 'Granularidad', 'Indicador',
                            'Unidad', 'Valor']].reset_index().drop(['index'], axis=1)

    os.remove(fuente_archivo)

    return df
