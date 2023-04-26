# %%
from selenium.webdriver.common.by import By
from datetime import datetime
import selenium as sel
from tqdm import tqdm
import pandas as pd
import base as bs
import os as os
import sys
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
driver.get(
    f'https://www.elcolombiano.com/busqueda/-/search/{empresa_}/false/false/19810311/20230311/date/true/true/0/0/meta/0/0/0/1')
driver.implicitly_wait(10)

driver.delete_all_cookies()

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
    driver.implicitly_wait(10)
    articulos = driver.find_elements(
        By.XPATH, './/li[@class="element   full-access norestricted"]')

    for art in tqdm(articulos):
        url = art.find_element(
            By.XPATH, './/div[contains(@class, "right")]//a').get_attribute('href')
        if not (bs.existedb(url, "database")):
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
            imagen = bs.obtener_imagen_col(art)
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
    tit["Contenido"] = bs.obtener_contenido_col(driver)
    tit["Resumen"] = bs.obtener_resumen_col(driver)

    driver.delete_all_cookies()

# %%
df = pd.DataFrame(titulares)
df['Empresa'] = df['Empresa'].str.replace('_', ' ')
bs.writeData("database", df)

# %%
driver.close()
