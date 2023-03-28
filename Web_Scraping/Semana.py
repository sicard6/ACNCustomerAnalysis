# %%
from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
import time
from datetime import datetime
import sys

import base as bs

import os as os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# %%
meses = {"ene": "1", "feb": "2", "mar": "3", "abr": "4", "may": "5", "jun": "6", "jul": "7",
         "ago": "8", "sep": "9", "oct": "10", "nov": "11", "dic": "12"}


def convert_fecha(fecha: str):
    aux_1 = fecha.split(",")[1].split()
    aux_1[1] = meses[aux_1[1]]
    return datetime.strptime(aux_1[0]+"/"+aux_1[1]+"/"+aux_1[2], "%d/%m/%Y")


# %%
# Empresa con la cual vamos a extraer los articulos
empresa = str.lower(sys.argv[1])  # input("Digite la empresa a extraer: ")
if "_" in empresa:
    empresa = empresa.strip().replace("_", "%20")
# %%
# cerar driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = sel.webdriver.Edge()
driver.get(f'https://www.semana.com/buscador/?query={empresa}')
driver.implicitly_wait(10)  # Nueva metodología de wait

driver.delete_all_cookies()

# %%
# Extrae la lista de todos los articulos de la pagina
articulos = driver.find_elements(
    By.XPATH, './/div[contains(@class,"queryly_item_row")]')

# %%
# Itera por cada articulo y extrae la informacion (EN CASO DE QUE NO EXISTA ARCHIVO DE ALMACENAMIENTO ANTERIOR)
titulares = []
for art in articulos:
    url = art.find_element(By.XPATH, './/a').get_attribute('href')
    if not (bs.existedb(url, "database")):
        fechaP = convert_fecha(art.find_element(
            By.XPATH, './/div[contains(@style,"margin-bottom:0px;color:#555;font-size:12px;")]').text)
        resumen = art.find_element(
            By.XPATH, './/div[contains(@class,"queryly_item_description")]').text
        titulo = art.find_element(
            By.XPATH, './/div[contains(@class,"queryly_item_title")]').text
        txtImage = art.find_element(
            By.XPATH, './/div[contains(@class,"queryly_advanced_item_imagecontainer")]').get_attribute('style')
        imagen = 'https://www.semana.com'
        imagen = imagen + txtImage.split("\"")[1]
        titulares.append({'Fecha Extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          'Titulo': titulo,
                          'Fecha Publicacion': fechaP,
                          'Resumen': resumen,
                          'URL': url,
                          'Imagen': imagen,
                          'Empresa': empresa})


# %%
# Itera por cada articulo y extrae la informacion (CASO DE QUE YA EXISTA ARCHIVO DONDE SE ALMACENA)
titulares = []
for art in articulos:
    url = art.find_element(By.XPATH, './/a').get_attribute('href')
    if not (bs.existedb(url, "database")):
        fecha = convert_fecha(
            art.find_element(
                By.XPATH, './/div[contains(@style,"margin-bottom:0px;color:#555;font-size:12px;")]').text
        )
        resumen = art.find_element(
            By.XPATH, './/div[contains(@class,"queryly_item_description")]').text
        titulo = art.find_element(
            By.XPATH, './/div[contains(@class,"queryly_item_title")]').text
        txtImage = art.find_element(
            By.XPATH, './/div[contains(@class,"queryly_advanced_item_imagecontainer")]').get_attribute('style')
        imagen = 'https://www.semana.com'
        imagen = imagen + txtImage.split("\"")[1]
        titulares.append({'Fecha Extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          'Titulo': titulo,
                          'Fecha Publicacion': fechaP,
                          'Resumen': resumen,
                          'URL': url,
                          'Imagen': imagen,
                          'Empresa': empresa,
                          'Fuente': 'Semana'})

# %%
# busca los autores de cada articulo y las almacena en la lista de titulares
for tit in titulares:

    driver.get(tit['URL'])
    driver.implicitly_wait(10)  # Nueva metodología de wait

    # agregar contenido al dict de titulares
    tit['Contenido'] = bs.obtener_contenido(driver)

    # agregar tags al dict de titulares
    tit['Tags'] = bs.obtener_tags(driver)

    # agregar contenido al dict de titulares
    tit['Tema'] = bs.obtener_tema(driver)

    driver.delete_all_cookies()

# %%
df = pd.DataFrame(titulares)
df['Empresa'] = df['Empresa'].str.replace('%20',' ')
bs.writeData("database", df)

# %%
driver.close()
