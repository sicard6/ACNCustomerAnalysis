# %% [markdown]
# ### Extracción de Estadísticas de Recaudo Mensual por Tipo de Impuesto
# [Link](https://www.dian.gov.co/dian/cifras/Paginas/EstadisticasRecaudo.aspx)

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
path = 'C:/Users/'+os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Indicadores_Macro'

# start_date = sys.argv[1]
# end_date = sys.argv[2]
# %%


def extraer(start_date: str, end_date: str):
    """Función que ingresa a la página de la DIAN y descarga las
    Estadísticas de Recaudo Mensual por Tipo de Impuesto. 
    Extrae el archico del zip y lo almacena en en la data cruda.

    Args:
        driver (sel.webdriver.Edge): driver de selenium
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

    time.sleep(10)
    driver.quit()

    # try:
    #     os.remove(path+'/Data/Raw/IVA.xlsx')
    # except:
    #     pass

    path_to_zip_file = '/Users/'+os.getlogin()+'/Downloads/' + \
        nombre_archivo.capitalize()+'.zip'
    # directory_to_extract_to = path+'/Data/Raw'

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall('/Users/'+os.getlogin()+'/Downloads/')

    os.remove(path_to_zip_file)

    lista_de_archivos = glob.glob('/Users/'+os.getlogin()+'/Downloads/*')
    fuente = max(lista_de_archivos, key=os.path.getctime).replace('\\', '/')

    df = pd.read_excel(fuente, header=7)
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
    # os.rename(fuente, '/'.join(fuente.split('/')[:-1])+'/IVA.xlsx')
    os.remove(fuente)
    return df


# %%
# print(extraer('01-01-1990', '01-01-2040'))
