# %%

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pandas as pd
import base as bs
import time
import os
# %%


def extraer(start_date: str, end_date: str):
    driver = bs.ejecutar_driver('https://totoro.banrep.gov.co/analytics/saw.dll?Portal&PortalPath=%2Fshared%2FDashboards_T%2FD_Estad%C3%ADsticas%2FEstad%C3%ADsticas&NQUser=publico&NQPassword=publico123&lang=es&page=Actividad%20econ%C3%B3mica,%20mercado%20laboral%20y%20cuentas%20financieras&pagina=Ocupaci%C3%B3n%20y%20desempleo')
    frame = driver.find_element(By.XPATH, './/iframe[@id="frame_dashboard"]')
    driver.switch_to.frame(frame)
    driver.find_element(
        By.XPATH, '//div[@title="Ocupación y desempleo"]').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'shielddy')))
    driver.find_elements(By.XPATH, '//span[@id="shielddy"]//a')[2].click()

    time.sleep(10)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')

    df = pd.read_excel(fuente_archivo, header=5)
    df.drop(df.tail(15).index, inplace=True)
    df['date'] = df['Año-Mes (AAAA-MM)'].map(lambda x: '01'+x[4:]+'-'+x[:4])

    aux_1 = start_date.replace(start_date[:2], '01')
    aux_2 = end_date.replace(end_date[:2], '01')

    try:
        start = df[df['date'] == aux_1].index[0]
    except IndexError:
        start = 0

    try:
        end = df[df['date'] == aux_2].index[0]
    except IndexError:
        end = len(df) - 1

    df['Granularidad'] = 'Mensual'
    df['Indicador'] = 'Tasa de Desempleo'
    df['Unidad'] = '%'
    df.rename(columns={'Tasa de desempleo (%)': 'Valor'}, inplace=True)

    df = df.loc[start:end, ['date', 'Granularidad', 'Indicador',
                            'Unidad', 'Valor']].reset_index().drop(['index'], axis=1)

    os.remove(fuente_archivo)

    return df
