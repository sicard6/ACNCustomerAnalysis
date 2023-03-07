# %%
# Librerías
import matplotlib.pyplot as plt
import pandas as pd
import spacy
import nltk


# %% Funciones

def procesamiento(columna: str, df: pd.DataFrame):
    """Función para procesar el texto y obtener columnas tokenizada y radicalizada

    Args:
        columna (str): columna a procesar
        df (pd.DataFrame): dataframe en donde se encuentra el texto a procesar

    Returns:
        pd.DataFrame: Data Frame con columna procesada
    """
    # Modelo de spacy que se utilizará
    spacy.cli.download('es_core_news_md')
    es = spacy.load('es_core_news_md')

    df_aux = pd.DataFrame()
    # Caracteres a minúscula
    df_aux[columna] = df[columna].str.lower()

    # Convertir a objeto spaCy
    aux = df[columna].apply(es)

    # Tokenización
    df_aux[f'{columna} procesado'] = aux.apply(
        lambda x: [token for token in x])
    # Normalización (minuscula, tamaño > 3 y solo letras)
    df_aux[f'{columna} procesado'] = df_aux[f'{columna} procesado'].apply(
        lambda x: [token for token in x if len(token) > 3 and token.is_alpha])
    # Remover stopwords (combinación de contexto y spacy).
    # Convertir Token a str
    with open('./NLP_Analitycs/sw_es.txt', 'r', encoding='utf-8') as file:
        stop_words_contexto = {line.split(None, 1)[0] for line in file}
    es.Defaults.stop_words |= stop_words_contexto
    df_aux[f'{columna} procesado'] = df_aux[f'{columna} procesado'].apply(
        lambda x: [token for token in x if not token.is_stop])

    # Segmentación en oraciones
    df_aux[f'{columna} segmentado'] = aux.apply(
        lambda x: [segment for segment in x.sents])

    return df_aux


def stemming(columna: str, df: pd.DataFrame):
    """Función para radicalizar las palabras (eliminación de plurales)

    Args:
        columna (str): columna a procesar
        df (pd.DataFrame): dataframe en donde se encuentra el texto a procesar
    """

    if f'{columna} procesado' not in df.columns:
        procesamiento(columna, df)

    stemmer = nltk.SnowballStemmer('spanish')
    df[f'{columna} radicalizado'] = df[f'{columna} procesado'].apply(
        lambda x: [stemmer.stem(token.orth_) for token in x])


def lemmatization(columna: str, df: pd.DataFrame):
    """Función para lematiizar las palabras (llevar a la raíz)

    Args:
        columna (str): columna a procesar
        df (pd.DataFrame): dataframe en donde se encuentra el texto a procesar
    """

    if f'{columna} procesado' not in df.columns:
        procesamiento(columna, df)

    df[f'{columna} lemmatizado'] = df[f'{columna} procesado'].apply(
        lambda x: {token.orth_: token.lemma_ for token in x})


def palabras_mas_comunes(empresa: str, columna: str, num: int, df: pd.DataFrame):
    """Función para obtener las frecuencias de las palabras mas repetidas en una 
    empresa

    Args:
        empresa (str): cliente a analizar
        columna (str): nombre de la columna de la que se obtendrán las palabras 
        más comunes
        num (int): top de palabras más comunes
        df (pd.DataFrame): data frame con la información
    """
    if f'{columna} procesado' not in df.columns:
        procesamiento(columna, df)

    df_ = df[df['Empresa'] == empresa]

    palabras = [str(token) for tokenlist in df_[
        f'{columna} procesado'].values for token in tokenlist]

    frecuencia = nltk.FreqDist(palabras)
    return frecuencia.most_common(num)


def ngramas_mas_comunes(empresa: str, columna: str, num: int, df: pd.DataFrame, n: int):
    """Función para obtener las frecuencias de los ngramas mas repetidos en una 
    empresa

    Args:
        empresa (str): cliente a analizar
        columna (str): nombre de la columna de la que se obtendrán las palabras 
        más comunes
        num (int): top de palabras más comunes
        df (pd.DataFrame): data frame con la información
        n (int): tamaño de la subsecuencia
    """
    if f'{columna} procesado' not in df.columns:
        procesamiento(columna, df)

    df_ = df[df['Empresa'] == empresa]

    palabras = [str(token) for tokenlist in df_[
        f'{columna} procesado'].values for token in tokenlist]

    ngrams = list(nltk.ngrams(palabras, n))
    frecuencia = nltk.FreqDist(ngrams)

    return frecuencia.most_common(num)


def entidades_mas_comunes(empresa: str, columna: str, num: int, df: pd.DataFrame, n: int):
    """Función para obtener las frecuencias de las entidades mas repetidos en una 
    empresa

    Args:
        empresa (str): cliente a analizar
        columna (str): nombre de la columna de la que se obtendrán las palabras 
        más comunes
        num (int): top de palabras más comunes
        df (pd.DataFrame): data frame con la información
        n (int): tamaño de la subsecuencia
    """
    spacy.cli.download('es_core_news_md')
    es = spacy.load('es_core_news_md')

    df_ = df[df['Empresa'] == empresa]

    # Caracteres a minúscula
    texto = " ".join([cont for cont in df_[columna]])
    # Tokenización
    entidades = {ent.text for ent in es(texto).ents}
    frecuencia = nltk.FreqDist(entidades)
    return frecuencia.most_common(num)


def conteo_ngramas(columna: str, n: int, df_: pd.DataFrame):
    if f'{columna} procesado' not in df_.columns:
        df_ = procesamiento(columna, df)

    palabras = [str(token) for tokenlist in df_[
        f'{columna} procesado'].values for token in tokenlist]
    ngrams = list(nltk.ngrams(palabras, n))
    frecuencia = nltk.FreqDist(ngrams)
    llaves = [list(i) for i in frecuencia.keys()]
    valores = frecuencia.values()

    return pd.DataFrame({'Palabras': llaves, 'Frecuecia': valores})


# %% LECTURA Y PREPARACIÓN DE LOS DATOS
# LEER ARCHIVOS CON DATOS
df = pd.read_csv('./data/raw/database.csv',
                 encoding='utf-8-sig', index_col=[0])
# df_curated = pd.read_csv(
#     '/data/curated/curated_database.csv', encoding='latin', index_col=[0])
# # Verificar cuales articulos no han sido procesados
# df = df_raw[~df_raw['Titulo'].isin(df_curated['Titulo'])]

if len(df) > 0:
    # Estandarización formato fechas
    df['Fecha Publicacion'] = pd.to_datetime(
        df['Fecha Publicacion']).dt.strftime('%d-%m-%Y')
    df['Fecha Extraccion'] = pd.to_datetime(
        df['Fecha Extraccion']).dt.strftime('%d-%m-%Y')

    # ELIMINACIÓN COLUMNAS Y FILAS NO RELEVANTES
    # Eliminar filas sin información en la columna Contenido
    df = df.drop(df[df['Contenido'] == "SIN PARRAFOS"].index).reset_index(
        drop=True)
    df = df.drop(df[df['Contenido'].isna()].index).reset_index(drop=True)

#   df = pd.concat([df, df_curated], ignore_index=True)
    df.to_csv(f'./data/curated/curated_database.csv')

# %%
df_contenido = procesamiento('Contenido', df)
print(df_contenido.head())
df_palabras = conteo_ngramas('Contenido', 1, df_contenido)
df_bigramas = conteo_ngramas('Contenido', 2, df_contenido)
df_trigramas = conteo_ngramas('Contenido', 3, df_contenido)

df_contenido.to_csv(
    './data/curated/contenido_procesado.csv', encoding='utf-8-sig')
df_palabras.to_csv('./data/curated/palabras.csv', encoding='utf-8-sig')
df_bigramas.to_csv('./data/curated/bigramas.csv', encoding='utf-8-sig')
df_trigramas.to_csv('./data/curated/trigramas.csv', encoding='utf-8-sig')
# print(palabras_mas_comunes('ecopetrol', 'Contenido', 10, df))
# print(ngramas_mas_comunes('ecopetrol', 'Contenido', 10, df, 2))
# print(ngramas_mas_comunes('ecopetrol', 'Contenido', 10, df, 3))
# %%
