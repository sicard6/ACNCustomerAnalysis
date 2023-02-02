# %%
from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
import time
import datetime
import base as bs
import sys

import os as os
import csv
import json

# %%
# Empresa con la cual vamos a extraer los articulos
empresa = str.lower(sys.argv[1])  # input("Digite la empresa a extraer: ")

# %%
# cerar driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = sel.webdriver.Edge()
driver.get(f'https://www.larepublica.co/{empresa}')
time.sleep(2)

# %%
# sacar primer titular CON BASE DE DATOS INICIAL
titulares = []
princip = driver.find_element(
    By.XPATH, './/div[contains(@class,"first-news")]')
urlPrinc = princip.find_elements(By.XPATH, './/a')[1].get_attribute('href')
if not (bs.existedb(urlPrinc, "larepublica")):  # Si no existe (elimine el .csv)
    temaPrinc = princip.find_elements(By.XPATH, './/a')[1].text
    fechaPrinc = princip.find_element(By.XPATH, './/span').text
    tituloPrinc = princip.find_elements(By.XPATH, './/a')[2].text
    imagenPrinc = princip.find_element(By.XPATH, './/img').get_attribute('src')
    titulares.append({'Fecha Extraccion': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      'Titulo': tituloPrinc,
                      'Fecha Publicacion': fechaPrinc,
                      'Tema': temaPrinc,
                      'URL': urlPrinc,
                      'Imagen': imagenPrinc,
                      'Empresa': empresa})

# el resto, autor, resumen, contenido y relacionados se sacan entrando a la url
# despues de guardar articulos normales. Mismo para las otras dos noticias principales

# %%
# Extrae la lista de todos los articulos de la pagina
# Todas las noticias relacionadas
articulos = driver.find_elements(
    By.XPATH, './/div[contains(@class,"row news")]')

# %%
# Itera por cada articulo y extrae la informacion (CASO DE QUE YA EXISTA ARCHIVO DONDE SE ALMACENA)
for art in articulos:
    url = art.find_elements(By.XPATH, './/a')[1].get_attribute('href')
    if not (bs.existedb(url, "larepublica")):  # Agregar la fuente para que corra la función .existedb
        fechaP = art.find_element(
            By.XPATH, './/span[@class = "date-news"]').text
        tema = art.find_elements(By.XPATH, './/a')[1].text
        resumen = art.find_element(By.XPATH, './/p').text
        titulo = art.find_element(By.XPATH, './/h2').text
        imagen = art.find_elements(By.XPATH, './/img')[0].get_attribute('src')
        titulares.append({'Fecha Extraccion': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          'Titulo': titulo,
                          'Fecha Publicacion': fechaP,
                          'Tema': tema,
                          'Resumen': resumen,
                          'URL': url,
                          'Imagen': imagen,
                          'Empresa': empresa})


# %%
# se carga la info del primer titular
driver.get(titulares[0]['URL'])

# agregar resumen al dict de titularesPrinc
titulares[0]['Resumen'] = bs.obtener_resumen(driver)


# %%
# busca los autores de cada articulo y las almacena en la lista de titulares
for tit in titulares:

    driver.get(tit['URL'])

    # agregar autor al dict de titulares
    tit['Autor'] = bs.obtener_autor(driver)

    # agregar contenido al dict de titulares
    tit['Contenido'] = bs.obtener_contenido_republica(driver)

    # agregar lista de URLs de noticias relacionadas
    tit['RelNewsUrls'] = bs.obtener_articulos_relacionados(driver)

    # se podria agregar un if resumen vacio, llamar a resumen. (para las 3 noticias principales)

# %%
driver.close()

# %%
df = pd.DataFrame(titulares)
bs.writeData("database", df)
