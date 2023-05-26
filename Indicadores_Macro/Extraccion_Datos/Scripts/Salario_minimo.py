# %% [markdown]
# ### Salario minimo
# [Link](https://totoro.banrep.gov.co/analytics/saw.dll?Portal&PortalPath=%2Fshared%2FDashboards_T%2FD_Estad%C3%ADsticas%2FEstad%C3%ADsticas&NQUser=publico&NQPassword=publico123&lang=es&page=Actividad%20econ%C3%B3mica,%20mercado%20laboral%20y%20cuentas%20financieras&pagina=Salarios)

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
    driver = bs.ejecutar_driver('https://totoro.banrep.gov.co/analytics/saw.dll?Portal&PortalPath=%2Fshared%2FDashboards_T%2FD_Estad%C3%ADsticas%2FEstad%C3%ADsticas&NQUser=publico&NQPassword=publico123&lang=es&page=Actividad%20econ%C3%B3mica,%20mercado%20laboral%20y%20cuentas%20financieras&pagina=Salarios')
    frame = driver.find_element(By.XPATH, './/iframe[@id="frame_dashboard"]')
    driver.switch_to.frame(frame)
    driver.find_element(By.XPATH, '//div[@title="Salarios"]').click()
    time.sleep(5)
    driver.find_elements(By.XPATH, '//span[@id="shielddx"]//a')[2].click()

    time.sleep(15)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')

    df = pd.read_excel(fuente_archivo, header=5)
    df.drop(df.tail(12).index, inplace=True)

    aux_1 = start_date.split('-')
    aux_2 = end_date.split('-')

    try:
        start = df[df['Año (aaaa)'] == int(aux_1[2])].index[0]
    except IndexError:
        start = 0

    try:
        end = df[df['Año (aaaa)'] == int(aux_2[2])].index[0]
    except IndexError:
        end = len(df) - 1

    df['date'] = '01-01-'+df['Año (aaaa)'].map(str)
    df['Granularidad'] = 'Anual'
    df['Indicador'] = 'Salario minimo'
    df['Unidad'] = 'COP'
    df.rename(columns={'Salario mínimo mensual (COP)': 'Valor'}, inplace=True)

    df = df.loc[start:end, ['date', 'Granularidad', 'Indicador',
                            'Unidad', 'Valor']].reset_index().drop(['index'], axis=1)
    # bs.guardar_archivo(fuente_archivo, path+'/Data/Raw/Salario_Minimo.xlsx')

    return df


# %%
# extraer_salario(start_date, end_date)
