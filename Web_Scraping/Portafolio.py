# %%
from selenium.webdriver.common.by import By
from datetime import datetime
import selenium as sel
from tqdm import tqdm
import pandas as pd
import base as bs
import os as os
import sys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# %%
# Empresa con la cual vamos a extraer los articulos
empresa = str.lower(sys.argv[1])
if " " in empresa:
    empresa_ = empresa.replace(" ", "%20")
else:
    empresa_ = empresa
num_paginas = 5

# %%
# crear driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = sel.webdriver.Edge()
driver.get(f'https://www.portafolio.co/buscar?q={empresa_}')
driver.maximize_window()
WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH,
                                      './/button[@class="align-right secondary slidedown-button"]')))\
    .click()

# %%
# Articulos a extraer
url_princ = f'https://www.portafolio.co/buscar?q={empresa_}&page='
titulares = []
for i in tqdm(range(1, num_paginas+1)):
    if i != 1:
        aux = str(i)
        url_a_buscar = url_princ+aux
        driver.get(url_a_buscar)
    articulos = [driver.find_element(By.XPATH, './/div[contains(@class, "listing-item first ")]')] + \
        driver.find_elements(
            By.XPATH, './/div[contains(@class, "listing-item  ")]')

    for art in tqdm(articulos):
        url = art.find_element(
            By.XPATH, './/h3[@class="listing-title"]//a').get_attribute('href')
        if not (bs.existedb(url, "database")):
            titulo = articulos[0].find_element(
                By.XPATH, './/h3[@class="listing-title"]//a').text
            fechaP = bs.obtener_fecha_port(art)
            tema = art.find_element(
                By.XPATH, './/div[@class="listing-category"]').text
            resumen = art.find_element(
                By.XPATH, './/div[@class="listing-epigraph"]').text
            imagen = bs.obtener_imagen_port(art)
            titulares.append({'Fecha Extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              'Titulo': titulo,
                              'Fecha Publicacion': fechaP,
                              'URL': url,
                              'Tema': tema,
                              'Resumen': resumen,
                              'Imagen': imagen,
                              'Empresa': empresa,
                              'Fuente': 'Portafolio'
                              })

# %%
for tit in tqdm(titulares):
    driver.get(tit["URL"])
    driver.implicitly_wait(10)
    tit['Autor'], tit['Contenido'], tit['RelNewsUrls'] = bs.obtener_autor_contenido_relsnews(
        driver)

# %%
df = pd.DataFrame(titulares)
bs.writeData("database", df)

# %%
driver.close()
