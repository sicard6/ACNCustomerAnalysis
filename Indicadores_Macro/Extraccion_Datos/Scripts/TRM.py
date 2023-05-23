# %% [markdown]
# # TRM
# [Link](https://totoro.banrep.gov.co/analytics/saw.dll?Portal&PortalPath=%2Fshared%2FDashboards_T%2FD_Estad%C3%ADsticas%2FEstad%C3%ADsticas&page=Tasas%20de%20cambio%20y%20sector%20externo&NQUser=publico&NQPassword=publico123&lang=es)
#
# Necesita autenticación

# %% [markdown]
# ### Desde 27/11/1991

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
    'https://totoro.banrep.gov.co/analytics/saw.dll?Portal&PortalPath=%2Fshared%2FDashboards_T%2FD_Estad%C3%ADsticas%2FEstad%C3%ADsticas&page=Tasas%20de%20cambio%20y%20sector%20externo&NQUser=publico&NQPassword=publico123&lang=es')

# %%


def extraer_TRM(driver: sel.webdriver.Edge):
    frame = driver.find_element(By.XPATH, './/iframe[@id="frame_dashboard"]')
    driver.switch_to.frame(frame)
    driver.find_elements(By.XPATH, '//span[@id="shielded"]//a')[2].click()

    time.sleep(10)
    driver.quit()

    fuente_archivo = bs.obtener_nombre_descarga(
        '/Users/'+os.getlogin()+'/Downloads')
    bs.guardar_archivo(fuente_archivo, path+'/Data/Raw/TRM.xlsx')


# %%
extraer_TRM(driver)
