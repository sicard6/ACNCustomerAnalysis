# %%
from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
from datetime import datetime
import base as bs

import os as os
import sys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# %%
meses = {"Enero": "1", "Febrero": "2", "Marzo": "3", "Abril": "4", "Mayo": "5", "Junio": "6", "Julio": "7",
         "Agosto": "8", "Septiembre": "9", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"}

# %%


def get_url(driver: sel.webdriver.Edge):
    """Función para obtener las url de los artículos relacionados
    a la búqueda

    Args:
        driver (sel.webdriver.Edge): pagina en la que se bsucara 
        el elemento

    Returns:
        str: string que contiene la url del artículo
    """
    try:
        url = driver.find_element(By.XPATH, './/h2//a').get_attribute('href')
    except:
        try:
            url = driver.find_element(
                By.XPATH, './/h3//a').get_attribute('href')
        except:
            url = None
    return url


# %%
def get_titulo(driver: sel.webdriver.Edge):
    """Función para obtener el título de un artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        str: string con el titulo del arículo
    """
    try:
        titulo = driver.find_element(
            By.XPATH, './/div[contains(@class, "row")]//a').text
    except:
        titulo = None
    else:
        return titulo

# %%


def get_autor(driver: sel.webdriver.Edge):
    """Función para obtener el autor del artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        str: string con el autor del arículo
    """
    try:
        autor = driver.find_element(
            By.XPATH, './/div[@class="mainInternalArticle__autor mb-10"]//a').text
    except:
        autor = None
    else:
        return autor

# %%


def get_fecha(driver: sel.webdriver.Edge):
    """Función para obtener la fecha de publicación del artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        datetime (datetime): fecha en la que sepublicó el artículo
    """
    try:
        fecha = driver.find_element(
            By.XPATH, './/div[contains(@class, "col-12")]//time').text
        lst_fecha = fecha.split()
        dia = lst_fecha[1][:-1]
        mes = meses[lst_fecha[0]]
        ano = lst_fecha[2]

        fecha_pub = datetime.strptime(dia+"/"+mes+"/"+ano, "%d/%m/%Y")
    except:
        fecha_pub = None
    return fecha_pub

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
        imagen = driver.find_element(
            By.XPATH, './/div[contains(@class, "mainHistoria-imagen")]//img').get_attribute('src')
    except:
        imagen = None
    return imagen

# %%


def get_contenido(driver):
    """Función para obtener todos los párrafos que conforman
    el arículo

    Args:
        driver (_type_): página en la que se hará la búsqueda

    Returns:
        str: string con todos los párrafos del artículo
    """
    try:
        contenido = driver.find_element(
            By.XPATH, './/div[contains(@class, "p normal body-text-large mb-30 all")]').text
        if len(contenido) <= 300:
            parrafos = driver.find_elements(
                By.XPATH, './/div[contains(@class, "row")]//p')
            contenido = ' '.join(list(map(lambda x: x.text, parrafos)))
    except:
        try:
            parrafos = driver.find_elements(By.XPATH, './/p')
            contenido = ' '.join(list(map(lambda x: x.text, parrafos)))
        except:
            contenido = None
    return contenido


# %%
# Empresa con la cual vamos a extraer los articulos
# input("Digite la empresa a extraer: ").lower()
empresa = str.lower(sys.argv[1])
revista = "laSillaVacia"

# %%
# crear driver... MODIFICAR DEPENDIENDO DEL NAVEGADOR
driver = sel.webdriver.Edge()
driver.get(f'https://www.lasillavacia.com/buscar?q={empresa}&cat=all')

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
    url = get_url(art)
    if url == None:
        continue
    if not (bs.existedb(url, "database")):
        titulo = get_titulo(art)
        titulares.append({'Fecha Extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          'Titulo': titulo,
                          'URL': url,
                          'Empresa': empresa
                          })

# %%
for tit in titulares:
    driver.get(tit["URL"])
    driver.implicitly_wait(10)
    tit["Autor"] = get_autor(driver)
    tit["Fecha Publicacion"] = get_fecha(driver)
    tit["Imagen"] = get_imag(driver)
    # tit["Resumen"] = get_resumen(driver)
    tit["Fuente"] = "La Silla Vacía"
    tit["Contenido"] = get_contenido(driver)

# %%
df = pd.DataFrame(titulares)
bs.writeData("database", df)

# %%
driver.close()
print(sys.argv)
