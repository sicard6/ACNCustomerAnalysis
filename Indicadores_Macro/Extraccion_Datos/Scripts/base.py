import selenium as sel
import os
import sys
import glob
import time

# ---------------------------------------------------------
# ------------- GLOBAL ------------------------------------
# ---------------------------------------------------------

base_path = os.getcwd()
path_indicadores = os.path.join(base_path, "Indicadores_Macro")


def ejecutar_driver(url: str):
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
        driver = sel.webdriver.Edge(
            executable_path=os.path.join(path_indicadores, "Extraccion_Datos", "msedgedriver.exe"))

    driver.get(url)
    time.sleep(2)

    return driver


def guardar_archivo(fuente_archivo: str, destino_archivo: str):
    try:
        os.rename(fuente_archivo, destino_archivo)
    except FileExistsError:
        os.remove(destino_archivo)
        os.rename(fuente_archivo, destino_archivo)


def obtener_nombre_descarga(carpeta: str):
    # * means all if need specific format then *.csv
    lista_de_archivos = glob.glob(carpeta+'/*')
    nombre_archivo = max(
        lista_de_archivos, key=os.path.getctime).replace('\\', '/')

    return nombre_archivo


def wait_for_downloads():
    while any([filename.endswith(".crdownload") for filename in
               os.listdir("/Users/"+os.getlogin()+"/Downloads")]):
        time.sleep(2)
