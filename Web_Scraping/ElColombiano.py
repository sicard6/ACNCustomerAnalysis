# %%
from tqdm import tqdm
from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
from datetime import datetime
import base as bs
import sys

import os as os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


# %%
def get_imag(driver: sel.webdriver.Edge):
    """Función para obtener el la url que contiene la imágen principal
    del artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        str: string con la url de la imágen
    """
    try:
        imagen = driver.find_element(By.XPATH, './/img').get_attribute('src')
    except:
        imagen = None
    return imagen

# %%


def get_contenido(driver: sel.webdriver.Edge):
    """Función para obtener todos los párrafos que conforman
    el arículo

    Args:
        driver (sel.webdriver.Edge): página en la que se hará la búsqueda

    Returns:
        str: string con todos los párrafos del artículo
    """
    try:
        contenido = driver.find_elements(
            By.XPATH, './/div[@class="block-text"]//p')
    except:
        contenido = []

    return " ".join([parrafo.text for parrafo in contenido])

# %%


def get_resumen(driver: sel.webdriver.Edge):
    """Función para obtener el resumen del artículo

    Args:
        driver (sel.webdriver.Edge): página en la que se hará la búsqueda

    Returns:
        str: cadena con el resumen del artículo 
    """
    try:
        resumen = driver.find_element(
            By.XPATH, './/div[@class="block-headline"]//h2').text
    except:
        resumen = None

    return resumen


# %%
# Empresa con la cual vamos a extraer los articulos
empresa = str.lower(sys.argv[1])
if " " in empresa:
    empresa_ = empresa.replace(" ", "%20")
else:
    empresa_ = empresa

# %%
# crear driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = sel.webdriver.Edge()
driver.get(
    f'https://www.elcolombiano.com/busqueda/-/search/{empresa_}/false/false/19810311/20230311/date/true/true/0/0/meta/0/0/0/1')
# driver.implicitly_wait(10)

# input_element = driver.find_element(By.XPATH, ".//input[@class='iter-field-input iter-field-input-text']")
# time.sleep(2)
# input_element.send_keys(empresa)
# input_element.send_keys(Keys.ENTER)

# %%

# %%
# Articulos a extraer
num_paginas = 5
url_princ = driver.current_url[:-1]
titulares = []
for i in tqdm(range(1, int(num_paginas) + 1)):
    aux = str(i)
    url_a_buscar = url_princ+aux
    driver.get(url_a_buscar)
    articulos = driver.find_elements(
        By.XPATH, './/li[@class="element   full-access norestricted"]')

    for art in tqdm(articulos):
        url = art.find_element(
            By.XPATH, './/div[contains(@class, "right")]//a').get_attribute('href')
        if not (bs.existedb(url, "elColombiano")):
            titulo = art.find_element(
                By.XPATH, './/h3[contains(@class, "titulo-noticia")]//span').text
            fechaP = art.find_element(
                By.XPATH, './/div[contains(@class, "fecha")]//span').text
            fechaP = datetime.strptime(fechaP, '%d / %m / %Y')
            tema = art.find_element(
                By.XPATH, './/div[contains(@class, "information")]//a').text
            autor = art.find_element(
                By.XPATH, './/span[contains(@class, "autor")]').text
            lista_tags = art.find_element(
                By.XPATH, './/div[contains(@class, "tags-noticia")]//ul')
            tags = list(
                map(lambda x: x.text, lista_tags.find_elements(By.XPATH, './/li')))
            imagen = get_imag(art)
            titulares.append({'Fecha Extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              'Titulo': titulo,
                              'Fecha Publicacion': fechaP,
                              'URL': url,
                              'Tema': tema,
                              'Autor': autor,
                              'Tags': tags,
                              'Imagen': imagen,
                              'Empresa': empresa,
                              'Fuente': 'El Colombiano'
                              })

# %%
for tit in titulares:
    driver.get(tit["URL"])
    driver.implicitly_wait(10)
    tit["Contenido"] = get_contenido(driver)
    tit["Resumen"] = get_resumen(driver)

# %%
df = pd.DataFrame(titulares)
bs.writeData("database", df)

# %%
driver.close()
