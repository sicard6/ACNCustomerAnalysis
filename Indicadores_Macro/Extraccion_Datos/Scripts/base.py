import selenium as sel
import os as os
import time

# ---------------------------------------------------------
# ------------- GLOBAL ------------------------------------
# ---------------------------------------------------------

path = 'C:/Users/'+os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Medios_Comunicacion'


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
            driver = sel.webdriver.Edge(
                executable_path=path.replace("\\\\", "/"))
        else:
            driver = sel.webdriver.Edge(
                executable_path=r"Medios_comunicacion/Web_Scraping/Scripts/msedgedriver.exe")

    driver.get(url)
    time.sleep(2)

    return driver
