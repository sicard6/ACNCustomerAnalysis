# %% [markdown]
# ### UVR
# [Link](https://totoro.banrep.gov.co/analytics/saw.dll?Go&Action=prompt&Path=%2Fshared%2FSeries%20Estad%C3%ADsticas_T%2F1.%20UPAC%20-%20UVR%2F1.1%20UVR%2F1.1.2.UVR_Serie%20historica%20diaria&Options=rdf&lang=es&NQUser=publico&NQPassword=publico123)

# %%
import os
import sys
import glob
import time
import pandas as pd
import selenium as sel
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base as bs


# %%
path = 'C:/Users/'+os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Indicadores_Macro'

# start_date = sys.argv[1]
# end_date = sys.argv[2]
# %%


def extraer(start_date: str, end_date: str):
    """Función que ingresa a la página del banco de la república y descarga los datos de UVR. 
    Almacena el arcivo en la carpeta de data cruda.

    Args:
        driver (sel.webdriver.Edge): driver de selenium
        conservar (bool, optional): True para dejar el rango por defecto, False para establecerlo. Predeterminado a True.
        fecha_inicio (str, optional): Fecha desde la que se quieren extraer los datos. Predeterminado a '01/01/2000'.
        fecha_final (str, optional): Fecha hasta la que se quieren extraer los datos. Predeterminado a datetime.today().strftime("%d/%m/%Y").
    """
    driver = bs.ejecutar_driver(
        'https://totoro.banrep.gov.co/analytics/saw.dll?Go&Action=prompt&Path=%2Fshared%2FSeries%20Estad%C3%ADsticas_T%2F1.%20UPAC%20-%20UVR%2F1.1%20UVR%2F1.1.2.UVR_Serie%20historica%20diaria&Options=rdf&lang=es&NQUser=publico&NQPassword=publico123')
    inputs = driver.find_elements(By.XPATH, './/input')

    desde = inputs[0]
    hasta = inputs[1]
    aceptar = inputs[2]

    desde.clear()
    desde.send_keys(start_date.replace('-', '/'))

    hasta.clear()
    hasta.send_keys(end_date.replace('-', '/'))

    aceptar.click()

    time.sleep(20)

    driver.find_elements(
        By.XPATH, './/td[@class="ResultLinksCell"]')[2].click()
    aux = driver.find_elements(
        By.XPATH, './/td[@class="masterMenu shadowMenuCell"]')[2]
    aux.find_elements(By.XPATH, './/a')[4].click()
    driver.find_element(By.XPATH, './/a[@aria-label="CSV"]').click()

    time.sleep(10)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')

    df = pd.read_csv(fuente_archivo)
    df['date'] = df['Fecha (dd/mm/aaaa)'].str.split(
        '-').map(lambda x: '-'.join(x[::-1]))

    try:
        start = df[df['date'] == start_date].index[0]
    except IndexError:
        start = 0

    try:
        end = df[df['date'] == end_date].index[0]
    except IndexError:
        end = len(df) - 1

    df['Granularidad'] = 'Diario'
    df['Indicador'] = 'UVR'
    df['Unidad'] = 'UVR'
    df.rename(columns={'Pesos colombianos por UVR': 'Valor'}, inplace=True)

    df = df.loc[start:end, ['date', 'Granularidad', 'Indicador',
                            'Unidad', 'Valor']].reset_index().drop(['index'], axis=1)
    # bs.guardar_archivo(fuente_archivo, path+'/Data/Raw/UVR.xlsx')

    return df


# %%
# extraer_UVR(start_date, end_date)
