# %% [markdown]
# ### UVR
# [Link](https://totoro.banrep.gov.co/analytics/saw.dll?Go&Action=prompt&Path=%2Fshared%2FSeries%20Estad%C3%ADsticas_T%2F1.%20UPAC%20-%20UVR%2F1.1%20UVR%2F1.1.2.UVR_Serie%20historica%20diaria&Options=rdf&lang=es&NQUser=publico&NQPassword=publico123)

# %%
import base as bs
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime
import selenium as sel
import time
import glob
import sys
import os

cwd = os.getcwd()
cwd = cwd.replace("Notebooks", "Scripts")
sys.path.insert(0, cwd.replace("\\\\", "\\"))

# %%
path = 'C:/Users/'+os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Indicadores_Macro'

# %%
driver = bs.ejecutar_driver(
    'https://totoro.banrep.gov.co/analytics/saw.dll?Go&Action=prompt&Path=%2Fshared%2FSeries%20Estad%C3%ADsticas_T%2F1.%20UPAC%20-%20UVR%2F1.1%20UVR%2F1.1.2.UVR_Serie%20historica%20diaria&Options=rdf&lang=es&NQUser=publico&NQPassword=publico123')

# %%


def extraer_UVR(driver: sel.webdriver.Edge, conservar: bool = True, fecha_inicio: str = '01/01/2000', fecha_final: str = datetime.today().strftime("%d/%m/%Y")):
    """Función que ingresa a la página del banco de la república y descarga los datos de UVR. 
    Almacena el arcivo en la carpeta de data cruda.

    Args:
        driver (sel.webdriver.Edge): driver de selenium
        conservar (bool, optional): True para dejar el rango por defecto, False para establecerlo. Predeterminado a True.
        fecha_inicio (str, optional): Fecha desde la que se quieren extraer los datos. Predeterminado a '01/01/2000'.
        fecha_final (str, optional): Fecha hasta la que se quieren extraer los datos. Predeterminado a datetime.today().strftime("%d/%m/%Y").
    """
    inputs = driver.find_elements(By.XPATH, './/input')

    desde = inputs[0]
    hasta = inputs[1]
    aceptar = inputs[2]
    if not conservar:
        desde.clear()
        desde.send_keys(fecha_inicio)

        hasta.clear()
        hasta.send_keys(fecha_final)

    aceptar.click()

    time.sleep(15)

    driver.find_elements(
        By.XPATH, './/td[@class="ResultLinksCell"]')[2].click()
    aux = driver.find_elements(
        By.XPATH, './/td[@class="masterMenu shadowMenuCell"]')[2]
    aux.find_elements(By.XPATH, './/a')[4].click()
    driver.find_element(By.XPATH, './/a[@aria-label="CSV"]').click()

    time.sleep(5)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')
    bs.guardar_archivo(fuente_archivo, path+'/Data/Raw/UVR.xlsx')


# %%
extraer_UVR(driver)
