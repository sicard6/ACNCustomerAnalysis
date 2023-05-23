# %% [markdown]
# ### Extracción de Estadísticas de Recaudo Mensual por Tipo de Impuesto
# [Link](https://www.dian.gov.co/dian/cifras/Paginas/EstadisticasRecaudo.aspx)

# %%
import base as bs
from selenium.webdriver.common.by import By
import selenium as sel
import zipfile
import time
import glob
import sys
import os

cwd = os.getcwd()
cwd = cwd.replace("Notebooks", "Scripts")
sys.path.insert(0, cwd.replace("\\\\", "\\"))

# %%
path = 'C:/Users/'+os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Indicadores_Macro'

# %%
driver = bs.ejecutar_driver(
    'https://www.dian.gov.co/dian/cifras/Paginas/EstadisticasRecaudo.aspx')

# %%


def extraer_iva(driver: sel.webdriver.Edge):
    """Función que ingresa a la página de la DIAN y descarga las
    Estadísticas de Recaudo Mensual por Tipo de Impuesto. 
    Extrae el archico del zip y lo almacena en en la data cruda.

    Args:
        driver (sel.webdriver.Edge): driver de selenium
    """
    iva = driver.find_elements(
        By.XPATH, './/div[@class="panel panel-default"]')[3]
    nombre_archivo = iva.find_element(
        By.XPATH, './/a').text.replace('í', 'i').replace(' ', '-').replace('---', '-')
    sec = iva.find_element(
        By.XPATH, './/div[@class="panel-collapse collapse"]')
    url_archivo = sec.find_element(By.XPATH, './/a').get_attribute('href')

    driver.get(url_archivo)

    time.sleep(15)
    driver.quit()

    try:
        os.remove(path+'/Data/Raw/IVA.xlsx')
    except:
        pass

    path_to_zip_file = '/Users/'+os.getlogin()+'/Downloads/' + \
        nombre_archivo.capitalize()+'.zip'
    directory_to_extract_to = path+'/Data/Raw'

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)

    os.remove(path_to_zip_file)

    lista_de_archivos = glob.glob(path+'/Data/Raw/*')
    fuente = max(lista_de_archivos, key=os.path.getctime).replace('\\', '/')

    os.rename(fuente, '/'.join(fuente.split('/')[:-1])+'/IVA.xlsx')


# %%
extraer_iva(driver)
