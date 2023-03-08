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
# Empresa con la cual vamos a extraer los articulos
# str.lower(sys.argv[1])  # input("Digite la empresa a extraer: ")
empresa = str.lower(sys.argv[2])
paginas = 5  # input("la cantidad de paginas ")

# %%
# cerar driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = sel.webdriver.Edge()

# %%
titulares = []
get_url = driver.current_url

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
