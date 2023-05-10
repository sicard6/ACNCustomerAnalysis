import selenium as sel
import pandas as pd
import os as os
import datetime
import time
import re

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# ---------------------------------------------------------
# ------------- GLOBAL ------------------------------------
# ---------------------------------------------------------


def existedb(url: str, fuente: str, empresa: str):
    """Funcion que verifica si una url existe en la base de datos
    Args:
        url (str): url del articulo a verificar
        fuente (str): archivo en el que se busca la URL
        empresa (str): empresa a la que hace referencia el artículo

    Returns:
        Bool: False si la url no existe o no encuentra la base de datos, True si no existe
    """
    try:
        db = pd.read_csv(f"./data/raw/{fuente}.csv", encoding='utf-8-sig')
    except FileNotFoundError:
        return False
    else:
        if (db["URL"].eq(url)).any():
            # Lista de empresas consideradas en la URL
            emp = db.loc[db['URL'] == url]['Empresa'].to_list()
            if empresa in emp:
                return True
            else:
                return False
        else:
            return False


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
 
def ejecutar_driver(url: str, notebook: bool = False):
    """Función para abrir el navegador

    Args:
        url (str): dirección url en la que se va a navegar.
        notebook (bool, optional): booleano que indica si es un notebook o un script. Defaults to False.

    Returns:
        _type_: retorna el navegador en el que se hará la búsqueda
    """
    try:
        driver = sel.webdriver.Edge()
    except:
        if notebook:
            cwd = os.getcwd()
            path = os.path.join(cwd, 'msedgedriver.exe')
            driver = sel.webdriver.Edge(executable_path=path.replace("\\\\", "\\"))
        else:
            driver = sel.webdriver.Edge(executable_path=r"Web_Scraping\Scripts\msedgedriver.exe")
        
    driver.get(url)
    time.sleep(2)
    
    return driver

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
    """obtiene los ariculos de una pagina de El Tiempo dada la url.
        'https://www.eltiempo.com/buscar?q={empresa}'
        'https://www.eltiempo.com/buscar/{i}?q={empresa}'

    Args:
        driver (sel.webdriver.Edge): driver de selenium
        url (str): _description_
        titulares (_type_): _description_
        empresa: es la empresa a la que se está buscando
    """
    
    # Diccionario para cambiar los meses a sus números correspondientes
    meses = {'ENERO': '1', 'FEBRERO': '2', 'MARZO': '3', 'ABRIL': '4', 'MAYO': '5', 'JUNIO': '6', 'JULIO': '7',
             'AGOSTO': '8', 'SEPTIEMBRE': '9', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'}
    driver.get(url)
    driver.implicitly_wait(10)
    # buscar = driver.find_element(
    #     By.XPATH, '//*[@id="main-container"]/div[16]/div[2]/div[2]/div[2]/div')
    articulos = driver.find_elements(By.CLASS_NAME, "listing")

    for articulos in articulos:
        aux = articulos.find_element(
            By.XPATH, './/h3[contains(@class, "title-container")]')
        url = aux.find_element(By.XPATH, './/a').get_attribute('href')
        # print(url)
        if not (existedb(url, "database", empresa)):
            titulo = articulos.find_element(
                By.CLASS_NAME, "title-container").text
            # print(titulo)
            resumen = articulos.find_element(
                By.CLASS_NAME, "epigraph-container").text
            # print(resumen)
            aux = articulos.find_element(
                By.CLASS_NAME, "published-at").text
            aux_1 = aux.split()
            aux_1.remove('DE')
            fechaPub = datetime.datetime.strptime(
                aux_1[1]+'/'+meses[aux_1[0]]+'/'+aux_1[2], "%d/%m/%Y"
            )
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


def obtener_autor_eltiempo(driver: sel.webdriver.Edge):
    """Funcion que obtiene el autor del articulo

    Args:
        driver (sel.webdriver.Edge): driver de selenium

    Returns:
        str: Nombre del autor del articulo
    """
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

    return autor_eltiempo


# ---------------------------------------------------------
# ------------------ EL COLOMBIANO ------------------------
# ---------------------------------------------------------


def obtener_imagen_col(driver: sel.webdriver.Edge):
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


def obtener_contenido_col(driver: sel.webdriver.Edge):
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

    if contenido == []:
        try:
            contenido = driver.find_elements(
                By.XPATH, './/div[@class="text"]//p')
        except:
            contenido = []

    return " ".join([parrafo.text for parrafo in contenido])


def obtener_resumen_col(driver: sel.webdriver.Edge):
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

# ---------------------------------------------------------
# ------------------- PORTAFOLIO --------------------------
# ---------------------------------------------------------


def obtener_fecha_port(driver: sel.webdriver.Edge):
    """Función para obtener la fecha de publicación del artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        date.date: fecha de publicación en formato dd/mm/YYYY
    """
    meses = {'Ene': '1', 'Feb': '2', 'Mar': '3', 'Abr': '4', 'May': '5', 'Jun': '6',
             'Jul': '7', 'Ago': '8', 'Sept': '9', 'Oct': '10', 'Nov': '11', 'Dic': '12'}
    fecha_texto = driver.find_element(By.XPATH, './/div[@class="time"]').text
    fecha_lista = fecha_texto.rsplit('- ')[1].split()[:4]
    del fecha_lista[2]
    fecha = datetime.datetime.strptime(
        fecha_lista[1]+'/'+meses[fecha_lista[0][:-1]]+'/'+fecha_lista[2], '%d/%m/%Y')

    return fecha


def obtener_imagen_port(driver: sel.webdriver.Edge):
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


def obtener_autor_contenido_relsnews(driver: sel.webdriver.Edge):
    """Función para obtener todos los párrafos que conforman
    el arículo

    Args:
        driver (sel.webdriver.Edge): página en la que se hará la búsqueda

    Returns:
        str: string con todos los párrafos del artículo
    """
    try:
        primer_parrafo = driver.find_element(
            By.XPATH, './/p[@class="parrafo first-parrafo"]')
        parrafos = driver.find_elements(By.XPATH, './/p[@class="parrafo"]')
        contenido = [primer_parrafo.text] + \
            [i for parrafo in parrafos for i in parrafo.text.split('\n\n')]
    except:
        contenido = []

    try:
        rel_news = driver.find_elements(
            By.XPATH, './/div[@class="article-content"]//p//a')
        for noticia in rel_news:
            if noticia.text in contenido:
                contenido.remove(noticia.text)

        rel_news_url = ", ".join([news.get_attribute('href')
                                 for news in rel_news])
    except:
        rel_news_url = None

    if len(contenido) > 0:
        autor = contenido[-1]
    else:
        autor = None

    if len(contenido) > 0:
        contenido = ' '.join(contenido[:-1])

    return autor, contenido, rel_news_url


# ---------------------------------------------------------
# ----------------- LA SILLA VACÍA ------------------------
# ---------------------------------------------------------

def get_url_sv(driver: sel.webdriver.Edge):
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
            url = driver.find_element(By.XPATH, './/h3//a').get_attribute('href')
        except:
            url = None
    return url

def get_titulo_sv(driver: sel.webdriver.Edge):
    """Función para obtener el título de un artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        str: string con el titulo del arículo
    """
    try:
        titulo = driver.find_element(By.XPATH, './/div[contains(@class, "row")]//a').text
    except:
        titulo = None
    else:
        return titulo
    
def get_autor_sv(driver: sel.webdriver.Edge):
    """Función para obtener el autor del artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        str: string con el autor del arículo
    """
    try:
        autor = driver.find_element(By.XPATH, './/div[@class="mainInternalArticle__autor mb-10"]//a').text
    except:
        autor = None
    else:
        return autor
    
def get_fecha_sv(driver: sel.webdriver.Edge):
    """Función para obtener la fecha de publicación del artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        datetime (datetime): fecha en la que sepublicó el artículo
    """
    meses = {"Enero": "1","Febrero": "2", "Marzo": "3", "Abril": "4", "Mayo": "5", "Junio": "6", "Julio": "7", 
        "Agosto": "8", "Septiembre": "9", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"}
    try:
        fecha = driver.find_element(By.XPATH, './/time').text
        lst_fecha = fecha.split()
        dia = lst_fecha[1][:-1]
        mes = meses[lst_fecha[0]]
        ano = lst_fecha[2]
        
        fecha_pub = datetime.datetime.strptime(dia+"/"+mes+"/"+ano, "%d/%m/%Y")
    except:
        fecha_pub = None
    return fecha_pub

def get_imag_sv(driver: sel.webdriver.Edge):
    """Función para obtener el la url que contiene la imágen principal
    del artículo

    Args:
        driver (sel.webdriver.Edge): pagina en la que se buscara el elemento

    Returns:
        str: string con la url de la imágen
    """
    try:
        imagen = driver.find_element(By.XPATH, './/div[contains(@class, "mainHistoria-imagen")]//img').get_attribute('src')
    except:
        imagen = None
    return imagen

def get_contenido_sv(driver):
    """Función para obtener todos los párrafos que conforman
    el arículo

    Args:
        driver (_type_): página en la que se hará la búsqueda

    Returns:
        str: string con todos los párrafos del artículo
    """
    try:
        contenido = driver.find_element(By.XPATH, './/div[contains(@class, "p normal body-text-large mb-30 all")]').text
        if len(contenido) <= 300:
            parrafos = driver.find_elements(By.XPATH, './/div[contains(@class, "row")]//p') # 
            contenido = ' '.join(list(map(lambda x: x.text, parrafos)))
    except:
        contenido = ''
        
    if contenido == '':
        try:
            parrafos = driver.find_elements(By.XPATH, './/p')
            contenido = ' '.join(list(map(lambda x: x.text, parrafos)))
        except:
            contenido = None
            
    return contenido.rsplit('El periodismo independiente')[0]