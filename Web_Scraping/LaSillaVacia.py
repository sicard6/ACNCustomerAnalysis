# %%
from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
import time
from datetime import datetime
import base as bs
import sys

import os as os
import csv

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# %%
# Empresa con la cual vamos a extraer los articulos
empresa = sys.argv[1].replace("_", " ")
empresa_ = empresa.lower().replace(" ", "%20")

# %%
# crear driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
try:
    driver = sel.webdriver.Edge()
except:
    driver = sel.webdriver.Edge(
        executable_path='Web_Scraping\msedgedriver.exe')
driver.get(f'https://www.lasillavacia.com/buscar?q={empresa_}&cat=all')

i = 1
try:
    while i < 2:
        driver.implicitly_wait(10)
        button = driver.find_element(
            By.XPATH, './/a[contains(@class, "load-more-results d-block p xl black-3d bold uppercase text-center")]')
        button.click()
except:
    pass

# %%
# "c c-d _g _g-md c-m-l c--m-n" Contiene tema
articulos = driver.find_elements(By.XPATH, './/article')

# %%
titulares = []
for art in articulos:
    url = bs.get_url_sv(art)
    if url == None:
        continue
    if not (bs.existedb(url, "database")):
        titulo = bs.get_titulo_sv(art)
        titulares.append({'Fecha Extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          'Titulo': titulo,
                          'URL': url,
                          'Empresa': empresa
                          })

# %%
for tit in titulares[:10]:
    driver.get(tit["URL"])
    driver.implicitly_wait(10)
    tit["Autor"] = bs.get_autor_sv(driver)
    tit["Fecha Publicacion"] = bs.get_fecha_sv(driver)
    tit["Imagen"] = bs.get_imag_sv(driver)
    # tit["Resumen"] = get_resumen(driver)
    tit["Fuente"] = "La Silla Vacía"
    tit["Contenido"] = bs.get_contenido_sv(driver)

# %%
df = pd.DataFrame(titulares)
bs.writeData("database", df)

# %%
driver.quit()
