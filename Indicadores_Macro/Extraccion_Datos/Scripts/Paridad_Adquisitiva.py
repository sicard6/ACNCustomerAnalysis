# %% [markdown]
# ### Paridad adquisitiva (varios países)
# [Link](https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm)

# %%
import base as bs
from selenium.webdriver.common.by import By
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
    'https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm')

# %%


def extraer_PA(driver: sel.webdriver.Edge):
    """Función que ingresa a la página de la OECD y descarga las
    los datos de paridad adquisitiva. 
    Almacena el arcivo en la carpeta de data cruda.

    Args:
        driver (sel.webdriver.Edge): driver de selenium
    """
    driver.find_element(
        By.XPATH, './/span[@class="download-btn-label"]').click()
    driver.find_element(
        By.XPATH, './/a[@class="download-indicator-button"]').click()

    time.sleep(5)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')
    bs.guardar_archivo(fuente_archivo, path +
                       '/Data/Raw/Paridad_Adquisitiva.csv')


# %%
extraer_PA(driver)
