from selenium.webdriver.common.by import By
import selenium as sel
import pandas as pd
import time
import datetime
import re

import os as os
import csv

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------------------------------------------------
# ------------- GLOBAL ------------------------------------
# ---------------------------------------------------------


def existedb(url: str, fuente: str):
    """Funcion que verifica si una url existe en la base de datos
    Args:
        url (str): url del articulo a verificar

    Returns:
        Bool: False si la url no existe o no encuentra la base de datos, True si no existe
    """
    try:
        db = pd.read_csv(f"./data/raw/{fuente}.csv", encoding='latin-1')
    except FileNotFoundError:
        return False
    else:
        return True if (db["URL"].eq(url)).any() else False


def writeData(nombre_archivo: str, datos: pd.DataFrame):
    """Función que concatena dataFrames y los guarda como csv.
    En caso de que no exista el archivo al que se quiere concatenar
    se crea uno con el mismo nombre

    Args:
        nombre_archivo (str): nombre del archivo a concatenar los datos o
        nombre del archivo nuevo
        datos (pd.DataFrame): datos a ser concatenados o guardados como csv
    """
    try:
        df = pd.read_csv(f'./data/raw/{nombre_archivo}.csv', index_col=[0])
        df = pd.concat([df, datos], ignore_index=True)
        df.to_csv(f'./data/raw/{nombre_archivo}.csv')
    except FileNotFoundError:
        datos.to_csv(f'./data/raw/{nombre_archivo}.csv')

# ---------------------------------------------------------
# ------------- SEMANA ------------------------------------
# ---------------------------------------------------------


def obtener_tags(driver: sel.webdriver.Edge):
    """Funcion que obtiene los tags del articulo

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str[]: Lista de strings/tags
    """
    tags = []
    try:
        secTags = driver.find_element(
            By.XPATH, './/div[contains(@class,"tags-list")]')
    except:
        tags = 'SIN TAGS'
    else:
        units = secTags.find_elements(By.XPATH, './/span')
        for i in units:
            tags.append(i.text)

    return tags


def obtener_contenido(driver: sel.webdriver.Edge):
    """Funcion que itera sobre todos los parrafos del articulo y los extrae.

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: devuelve el contenido del articulo
    """
    ignored_exceptions = (NoSuchElementException,
                          StaleElementReferenceException)
    contenido = ''
    try:
        html = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((By.XPATH, './/article[contains(@class,"paywall")]')))
        parrafos = html.find_elements(By.XPATH, './/p')
    except:
        try:
            html = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
                EC.presence_of_element_located((By.XPATH, './/p[contains(@id,"textId")]')))
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
            print('error en el for de parrafos del else externo')

    return contenido


def obtener_tema(driver: sel.webdriver.Edge):
    """Funcion que itera sobre todos los parrafos del articulo y los extrae.

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: devuelve el contenido del articulo
    """
    tema = ''
    try:
        tema = driver.find_element(By.XPATH, './/h3').text
    except:
        try:
            secc = driver.find_element(
                By.XPATH, './/div[contains(@class,"styles__Header-sc-1w6splk-3 jtSkhd hidden-md hidden-sm")]')
            tema = secc.find_element(By.XPATH, './/h1').text
        except:
            tema = 'SIN TEMA'
    return tema


# ---------------------------------------------------------
# ------------- LA REPUBLICA ------------------------------
# ---------------------------------------------------------

def obtener_autor(driver: sel.webdriver.Edge):
    """Funcion que obtiene el autor del articulo

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: Nombre del autor del articulo
    """
    autor = ''
    try:
        secAutor = driver.find_element(
            By.XPATH, './/div[contains(@class,"author-article")]')
    except:
        autor = 'SIN AUTOR'
    else:
        try:
            autor = secAutor.find_element(By.XPATH, './/button').text
        except:
            autor = secAutor.find_element(By.XPATH, './/span').text

    return autor


def obtener_resumen(driver: sel.webdriver.Edge):
    """Funcion que obtiene el resumen del articulo

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: Nombre del resumen del articulo
    """
    resumen = ''
    try:
        secResumen = driver.find_element(
            By.XPATH, './/div[contains(@class,"lead")]')
    except:
        resumen = 'SIN RESUMEN'
    else:
        try:
            resumen = secResumen.find_element(By.XPATH, './/p').text
        except:
            resumen = 'ERROR SACANDO LA P'

    return resumen


def obtener_articulos_relacionados(driver: sel.webdriver.Edge):
    """Obtener los articulos relacionados a un articulo

    Args:
        driver (sel.webdriver.Edge): referencia al driver de selenium

    Returns:
        List: lista de articulos relacionados
    """
    relNewsUrls = []
    try:
        related = driver.find_elements(
            By.XPATH, './/div[contains(@class,"relatedNews")]')
        for i in related:
            relNewsUrls.append(i.find_element(
                By.XPATH, './/a').get_attribute('href'))
    except:
        relNewsUrls = []
    return relNewsUrls


def obtener_contenido_republica(driver: sel.webdriver.Edge):
    """Funcion que itera sobre todos los parrafos del articulo y los extrae.

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: devuelve el contenido del articulo
    """
    contenido = ''
    try:
        html = driver.find_element(
            By.XPATH, './/div[contains(@class,"html-content")]')
        parrafos = html.find_elements(By.XPATH, './/p')
    except:
        contenido = 'SIN PARRAFOS'
    else:
        for i in parrafos:
            contenido += i.text
    return contenido


# ---------------------------------------------------------
# ------------- EL TIEMPO ---------------------------------
# ---------------------------------------------------------

def obtener_articulos_eltiempo(driver: sel.webdriver.Edge, url: str, titulares, empresa):
    """obtiene los ariculos de una pagina del tiempo dada la url.
        'https://www.eltiempo.com/buscar?q={empresa}'
        'https://www.eltiempo.com/buscar/{i}?q={empresa}'

    Args:
        driver (sel.webdriver.Edge): driver de selenium
        url (str): _description_
        titulares (_type_): _description_
        empresa: es la empresa a la que se está buscando
    """
    driver.get(url)
    driver.implicitly_wait(10)
    buscar = driver.find_element(
        By.XPATH, '//*[@id="main-container"]/div[16]/div[2]/div[2]/div[2]/div')
    articulos = buscar.find_elements(By.CLASS_NAME, "listing")

    for articulos in articulos:
        aux = articulos.find_element(
            By.XPATH, './/h3[contains(@class, "title-container")]')
        url = aux.find_element(By.XPATH, './/a').get_attribute('href')
        # print(url)
        if not (existedb(url, "database")):
            titulo = articulos.find_element(
                By.CLASS_NAME, "title-container").text
            # print(titulo)
            resumen = articulos.find_element(
                By.CLASS_NAME, "epigraph-container").text
            # print(resumen)
            fechaPub = articulos.find_element(
                By.CLASS_NAME, "published-at").text
            # print(fechaPub)
            tema = articulos.find_element(By.CLASS_NAME, "category").text
            # print(tema)
            titulares.append({'Fecha Extraccion': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              'Titulo': titulo,
                              'Fecha Publicacion': fechaPub,
                              'Tema': tema,
                              'URL': url,
                              'Resumen': resumen,
                              'Empresa': empresa,
                              'Fuente': 'El Tiempo'})


def obtener_articulos_eltiempo_dataframe(driver: sel.webdriver.Edge, url: str, titulares, empresa):
    """obtiene los ariculos de una pagina del tiempo dada la url con titulares en tipo pd.dataframe
        'https://www.eltiempo.com/buscar?q={empresa}'
        'https://www.eltiempo.com/buscar/{i}?q={empresa}'

    Args:
        driver (sel.webdriver.Edge): _description_
        url (str): _description_
        titulares (_type_): _description_
        empresa (_type_): _description_
    """
    driver.get(url)
    driver.implicitly_wait(10)
    buscar = driver.find_element(
        By.XPATH, '//*[@id="main-container"]/div[16]/div[2]/div[2]/div[2]/div')
    articulos = buscar.find_elements(By.CLASS_NAME, "listing")

    titulares = titulares + "hola"

    empresa = empresa+"hellow"
