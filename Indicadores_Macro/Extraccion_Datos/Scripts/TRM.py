# %%
from selenium.webdriver.common.by import By
import pandas as pd
import base as bs
import time
import os

# %%


def extraer(start_date: str, end_date: str):
    driver = bs.ejecutar_driver(
        'https://totoro.banrep.gov.co/analytics/saw.dll?Portal&PortalPath=%2Fshared%2FDashboards_T%2FD_Estad%C3%ADsticas%2FEstad%C3%ADsticas&page=Tasas%20de%20cambio%20y%20sector%20externo&NQUser=publico&NQPassword=publico123&lang=es')

    frame = driver.find_element(By.XPATH, './/iframe[@id="frame_dashboard"]')
    driver.switch_to.frame(frame)
    driver.find_elements(By.XPATH, '//span[@id="shielded"]//a')[2].click()

    time.sleep(40)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')

    df = pd.read_excel(fuente_archivo, header=7)
    df.drop(df.tail(4).index, inplace=True)
    df['date'] = df['Fecha (dd/mm/aaaa)'].map(lambda x: x.strftime("%d-%m-%Y"))

    try:
        start = df[df['date'] == start_date].index[0]
    except IndexError:
        start = 0

    try:
        end = df[df['date'] == end_date].index[0]
    except IndexError:
        end = len(df) - 1

    df['Granularidad'] = 'Diario'
    df['Indicador'] = 'TRM'
    df['Unidad'] = 'COP'
    df.rename(columns={
              'Tasa de cambio representativa del mercado (TRM)': 'Valor'}, inplace=True)

    df = df.loc[start:end, ['date', 'Granularidad', 'Indicador',
                            'Unidad', 'Valor']].reset_index().drop(['index'], axis=1)

    os.remove(fuente_archivo)

    return df
