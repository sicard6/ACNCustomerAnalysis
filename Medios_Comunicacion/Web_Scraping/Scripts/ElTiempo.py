# %% [markdown]
# #

# %%
import selenium as sel
from selenium.webdriver.common.by import By
import pandas as pd
import base as bs
import sys

import os as os

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# %% [markdown]
# Web Scraping El tiempo

# %%
# Empresa con la cual vamos a extraer los articulos. Comentar y descomentar con respecto a la utilidad que va a tener
# empresa = input("Digite la empresa a extraer: ") # Utilizar este método si no se usará un archivo json, y se ingresa manualmente la empresa

empresa = sys.argv[1]
empresa_ = empresa.lower().replace("_", "%20")

paginas = 5  # Se recolecta los artículos de 5 páginas del Tiempo

# %%
# cerar driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = bs.ejecutar_driver('https://www.eltiempo.com')

# %%
titulares = []

# hacer el WS del primer url
bs.obtener_articulos_eltiempo(
    driver=driver, url=f'https://www.eltiempo.com/buscar?q={empresa}', titulares=titulares, empresa=empresa)

for i in range(2, int(paginas) + 1):
    bs.obtener_articulos_eltiempo(
        driver=driver, url=f'https://www.eltiempo.com/buscar/{i}?q={empresa}', titulares=titulares, empresa=empresa)


# %% [markdown]
# ### Extrae info de cada URL

# %%
# Inicializa los cookies del navegador
driver.delete_all_cookies()

# Busca cada articulo y las almacena en la lista de titulares
for tit in titulares:
    driver.get(tit['URL'])
    driver.implicitly_wait(10)  # Nueva metodología de wait

    ignored_exceptions = (NoSuchElementException,
                          StaleElementReferenceException)
    contenido = ''
    try:
        html = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((By.XPATH, './/div[contains(@class,"modulos public-side")]')))
        parrafos = html.find_elements(By.XPATH, './/p')

    except:
        try:
            html = driver.find_element(
                By.XPATH, './/div[contains(@class,"modulos public-side")]')
            parrafos = html.find_elements(By.XPATH, './/p')
        except:
            contenido = 'SIN PARRAFOS'
        else:
            for i in parrafos:
                contenido += i.text

    else:
        try:
            for i in parrafos:
                contenido += i.text
        except:
            print(
                'Error en el último for == el más dentro de "for tit in titulares:" externo')

    # agregar contenido al dict de titulares
    tit['Contenido'] = contenido

    # Para agregar el Autor del artículo
    autor_eltiempo = ''
    try:
        autor_eltiempo = driver.find_element(
            By.XPATH, "//div[(@class='author_data')]/div/a[@class='who']/span[@class='who']").text
    except:
        autor_eltiempo = 'SIN AUTOR'

    if (autor_eltiempo == ''):
        try:
            autor_eltiempo = driver.find_element(
                By.XPATH, "//div[(@class='author_data')]/div/a[@class='who']/span[@class='who-modulo who']").text
        except:
            autor_eltiempo = 'SIN AUTOR'

    tit['Autor'] = autor_eltiempo

    # Sacar la imagen del artículo
    imagen = ''

    try:
        imagen_temp = driver.find_element(
            By.XPATH, "//div[@class='recurso_apertura']")
    except:
        imagen = 'SIN IMAGEN'
    else:
        imagen = imagen_temp.find_element(
            By.XPATH, './/img').get_attribute('src')

    tit['Imagen'] = imagen

    driver.delete_all_cookies()  # clear all cookies in scope of session

    # agregar lista de URLs de noticias relacionadas
    # tit['RelNewsUrls'] = bs.obtener_articulos_relacionados_eltiempo(driver)


# %% [markdown]
# ### Para agregar la info en un archivo CSV

# %%
# Cerrar navegador
driver.quit()

# %%
df = pd.DataFrame(titulares)
bs.writeData("database", df)
