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


#---------------------------------------------------------
#------------- GLOBAL ------------------------------------
#---------------------------------------------------------

def existedb(url: str, fuente: str):
    """Funcion que verifica si una url existe en la base de datos
    Args:
        url (str): url del articulo a verificar

    Returns:
        Bool: False si la url existe, True si no existe
    """
    
    db = pd.read_csv(f"../data/raw/{fuente}.csv",encoding='latin-1')
    return True if (db["URL"].eq(url)).any() else False

def guardar_articulo(articulo: pd.DataFrame):
    if not(existedb(articulo['URL'])):
        print('')



#---------------------------------------------------------
#------------- SEMANA ------------------------------------
#---------------------------------------------------------

def obtener_tags(driver: sel.webdriver.Edge):
    """Funcion que obtiene los tags del articulo

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str[]: Lista de strings/tags
    """
    tags = []
    try :
        secTags = driver.find_element(By.XPATH,'.//div[contains(@class,"tags-list")]')
    except:
        tags = 'SIN TAGS'
    else:
        units = secTags.find_elements(By.XPATH,'.//span')
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
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
    contenido = ''
    try :
        html = WebDriverWait(driver,10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,'.//article[contains(@class,"paywall")]')))
        parrafos = html.find_elements(By.XPATH,'.//p')
    except:
        try:
            html = WebDriverWait(driver,10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,'.//p[contains(@id,"textId")]')))
            parrafos = html.find_elements(By.XPATH,'.//p')
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
    try :
        tema = driver.find_element(By.XPATH,'.//h3').text
    except:
        try:
            secc = driver.find_element(By.XPATH,'.//div[contains(@class,"styles__Header-sc-1w6splk-3 jtSkhd hidden-md hidden-sm")]')
            tema = secc.find_element(By.XPATH,'.//h1').text
        except:
            tema = 'SIN TEMA' 
    return tema 


#---------------------------------------------------------
#------------- LA REPUBLICA ------------------------------
#---------------------------------------------------------

def obtener_autor(driver: sel.webdriver.Edge):
    """Funcion que obtiene el autor del articulo

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: Nombre del autor del articulo
    """
    autor = ''
    try :
        secAutor = driver.find_element(By.XPATH,'.//div[contains(@class,"author-article")]')
    except:
        autor = 'SIN AUTOR'
    else:
        try:
            autor = secAutor.find_element(By.XPATH,'.//button').text
        except:
            autor = secAutor.find_element(By.XPATH,'.//span').text
            
    return autor
    
def obtener_resumen(driver: sel.webdriver.Edge):
    """Funcion que obtiene el resumen del articulo

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: Nombre del resumen del articulo
    """
    resumen = ''
    try :
        secResumen = driver.find_element(By.XPATH,'.//div[contains(@class,"lead")]')
    except:
        resumen = 'SIN RESUMEN'
    else:
        try:
            resumen = secResumen.find_element(By.XPATH,'.//p').text
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
    try :
        related = driver.find_elements(By.XPATH,'.//div[contains(@class,"relatedNews")]')
        for i in related:
            relNewsUrls.append(i.find_element(By.XPATH,'.//a').get_attribute('href'))
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
    try :
        html = driver.find_element(By.XPATH,'.//div[contains(@class,"html-content")]')
        parrafos = html.find_elements(By.XPATH,'.//p')
    except:
        contenido = 'SIN PARRAFOS'
    else:
        for i in parrafos:
            contenido += i.text
       
    return contenido




#---------------------------------------------------------
#------------- EL TIEMPO ---------------------------------
#---------------------------------------------------------


def obtener_articulos_relacionados_eltiempo(driver: sel.webdriver.Edge):
    """Obtener los articulos relacionados a un articulo

    Args:
        driver (sel.webdriver.Edge): referencia al driver de selenium

    Returns:
        List: lista de articulos relacionados
    """
    relNewsUrls = []
    try :
        related = driver.find_elements(By.XPATH,'.//div[contains(@class,"relatedNews")]')
        for i in related:
            relNewsUrls.append(i.find_element(By.XPATH,'.//a').get_attribute('href'))
    except:
        relNewsUrls = []
    return relNewsUrls

