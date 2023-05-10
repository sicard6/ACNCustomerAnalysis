# %%
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
import base as bs
import sys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# %%
# Empresa con la cual vamos a extraer los articulos
empresa = sys.argv[1]
empresa_ = empresa.lower().replace("_", "%20")
num_paginas = 5

# %%
# crear driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = bs.ejecutar_driver(f'https://www.portafolio.co/buscar?q={empresa_}')
WebDriverWait(driver, 500)\
    .until(EC.element_to_be_clickable((By.XPATH,
                                      './/button[@class="align-right secondary slidedown-button"]')))\
    .click()

# %%
# Articulos a extraer
url_princ = f'https://www.portafolio.co/buscar?q={empresa_}&page='
titulares = []
for i in range(1, num_paginas+1):
    if i != 1:
        aux = str(i)
        url_a_buscar = url_princ+aux
        driver.get(url_a_buscar)
    articulos = [driver.find_element(By.XPATH, './/div[contains(@class, "listing-item first ")]')] + \
        driver.find_elements(
            By.XPATH, './/div[contains(@class, "listing-item  ")]')

    for art in articulos:
        url = art.find_element(
            By.XPATH, './/h3[@class="listing-title"]//a').get_attribute('href')
        if not (bs.existedb(url, "database", empresa)):
            titulo = art.find_element(
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
                              'Empresa': empresa.capitalize(),
                              'Fuente': 'Portafolio'
                              })

# %%
for tit in titulares:
    driver.get(tit["URL"])
    driver.implicitly_wait(10)
    tit['Autor'], tit['Contenido'], tit['RelNewsUrls'] = bs.obtener_autor_contenido_relsnews(
        driver)

# %%
df = pd.DataFrame(titulares)
bs.writeData("database", df)

# %%
driver.quit()
