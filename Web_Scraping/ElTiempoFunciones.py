import selenium as sel
from selenium.webdriver.common.by import By
import pandas as pd
import time
import datetime
import base as bs
import ElTiempoFunciones as etf

import os as os
import csv
import json



def get_titulo(articulos):
    titulo = articulos.find_element(By.CLASS_NAME,"title-container").text
    return titulo

def get_resumen(articulos):
    return articulos.find_element(By.CLASS_NAME,"epigraph-container").text

def get_fechapu(articulos):
    return articulos.find_element(By.CLASS_NAME,"published-at").text

def get_tema(articulos):
    return articulos.find_element(By.CLASS_NAME,"category").text
