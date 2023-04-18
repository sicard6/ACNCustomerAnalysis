# %%
# Librerías
from gensim.corpora.dictionary import Dictionary
from gensim.models import CoherenceModel
from gensim.models import LdaMulticore
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
    # spacy.cli.download('es_core_news_md')
    es = spacy.load('es_core_news_md')

    # Etiquetas a remover del texto lematizado
    # Tags I want to remove from the text
    removal = ['ADV', 'PRON', 'CCONJ', 'PUNCT',
               'PART', 'DET', 'ADP', 'SPACE', 'NUM', 'SYM']

    # Convertir a objeto spaCy
    aux = df[columna].str.lower().apply(es)

    # Tokenización
    df[f'{columna} procesado'] = aux.apply(
        lambda x: [token for token in x])
    # Normalización (minuscula, tamaño > 3 y solo letras)
    df[f'{columna} procesado'] = df[f'{columna} procesado'].apply(
        lambda x: [token for token in x if len(token) > 3 and token.is_alpha])
    # Remover stopwords (combinación de contexto y spacy).
    # Convertir Token a str
    with open('./NLP_Analitycs/sw_es.txt', 'r', encoding='utf-8') as file:
        stop_words_contexto = {line.split(None, 1)[0] for line in file}
    es.Defaults.stop_words |= stop_words_contexto
    df[f'{columna} procesado'] = df[f'{columna} procesado'].apply(
        lambda x: [token for token in x if not token.is_stop])

    # Segmentación en oraciones
    df[f'{columna} segmentado'] = aux.apply(
        lambda x: ", ".join([segment.orth_ for segment in x.sents]))

    # Extracción de entidades
    df[f'Entidades de {columna}'] = aux.apply(
        lambda x: ", ".join([ent.text for ent in x.ents]))

    # Radicalización (stemming)
    stemmer = nltk.SnowballStemmer('spanish')
    df[f'{columna} radicalizado'] = df[f'{columna} procesado'].apply(
        lambda x: ", ".join([stemmer.stem(token.orth_) for token in x]))

    # Lemmatization
    df[f'{columna} lematizado'] = df[f'{columna} procesado'].apply(
        lambda x: ", ".join([token.lemma_ for token in x if token.pos_ not in removal]))

    # Procesado a string
    df[f'{columna} procesado'] = df[f'{columna} procesado'].apply(
        lambda x: ", ".join([token.orth_ for token in x]))


def lista_ngramas(val_ent: str, val_pal: str, indice: int, n: int):
    """Función que genera la lista de todas las palabras del conjunto
    de datos y obtiene la frecuencia de cada una por artículo, 
    especifica a que artículo pertenece y si es una entidad (1) o no
    (0).

    Args:
        val_ent (str): cadena de entidades obtenida en el procesamiento
        val_pal (str): cadena de palabras obtenida en el procesamiento
        indice (int): indice del artículo al que corresponden las cadenas
        n (int): tamaño de la subsecuencia del n-grama

    Returns:
        pd.DataFrame: DataFrame con el indice, la palabra, frecuencia de
        aparición, ID del artículo al que pertenece. Si es solo una palabra
        se incluye la columna de entidad que indica si lo es o no
    """
    if type(val_ent) == float:
        entidades = {}
    else:
        entidades = set(val_ent.split(', '))
    palabras = val_pal.split(', ')
    ngrams = list(nltk.ngrams(palabras, n))
    freq_pal = dict(nltk.FreqDist(ngrams))

    if n == 1:
        lista = []
        for key, value in freq_pal.items():
            word = ", ".join(list(key))
            if word in entidades:
                lista.append([word, value, indice, 1])
            else:
                lista.append([word, value, indice, 0])
        df_frec = pd.DataFrame(
            lista, columns=['Palabra', 'Frecuencia', 'ID_Articulo', 'Entidad'])
    else:
        lista = []
        for key, value in freq_pal.items():
            lista.append([", ".join(list(key)), value, indice])
        df_frec = pd.DataFrame(
            lista, columns=['Palabra', 'Frecuencia', 'ID_Articulo'])

    df_frec.index.name = 'ID_Token'
    return df_frec


def mejor_puntaje(topicos: list, puntaje_umass: list):
    """Función para determinar cúal es el menor tópico con mejor puntaje de 
    coherencia.
    Valor mas a la izquierda que sea <= puntaje minimo por 0.9 (entre 2 y 12 topicos)

    Args:
        topicos (list): lista del número de tópicos considerados en los puntajes de 
        coherencia
        puntaje_umass (list): list de puntajes para cada uno de los tópicos

    Returns:
        int: mejor número de tópicos según criterio definido
    """
    puntaje_min = min(puntaje_umass)
    for n in range(len(puntaje_umass)):
        if puntaje_umass[n] <= puntaje_min*(0.9):
            break
    return topicos[n]


def n_topicos(corpus: list, diccionario: Dictionary, n_iterations: int = 10,
              n_workers: int = 4, n_passes: int = 10, n_random_state: int = 100,
              max_topicos: int = 12, min_topicos: int = 2):
    """Función para recolectar los puntajes de coherencia de diferentes modelos y
    luego determinar el mejor número de tópicos según el criterio definido y el 
    rango dado.

    Args:
        corpus (list): colección de textos
        diccionario (Dictionary): mapa de todas las palabras (tokens) con su id único.
        n_iterations (int, optional): número de iteraciones. Defaults to 10.
        n_workers (int, optional): equivale al número de cores del computador. 
        Defaults to 4.
        n_passes (int, optional): número de veces que pasa por el corpus para entrenarse. 
        Defaults to 10.
        n_random_state (int, optional): semilla para un generador de números 
        pseudoaleatorios. Defaults to 100.
        max_topicos (int, optional): número máximo de tópicos a considerar. Defaults to 12.
        min_topicos (int, optional): número mínimo de tópicos a considerar. Defaults to 2.

    Returns:
        int: número de topicos a considerar en el modelo LDA
    """
    topicos = []
    puntaje_umass = []
    # score_v = []
    for i in range(min_topicos, max_topicos + 1, 1):
        lda_model = LdaMulticore(corpus=corpus, id2word=diccionario, iterations=n_iterations,
                                 num_topics=i, workers=n_workers, passes=n_passes, random_state=n_random_state)
        cm_umass = CoherenceModel(
            model=lda_model, corpus=corpus, dictionary=diccionario, coherence='u_mass')
        # cm_v = CoherenceModel(
        #     model=lda_model, texts=df[f'{columna} lematizado'], corpus=corpus, dictionary=diccionario, coherence='c_v')
        topicos.append(i)
        puntaje_umass.append(cm_umass.get_coherence())
        # score_v.append(cm_v.get_coherence())
    n = mejor_puntaje(topicos, puntaje_umass)
    return n


def lda_model(df: pd.DataFrame, columna: str, filtro_inf: int = 1, filtro_sup: float = 0.2,
              iteraciones: int = 50, workers: int = 4, passes: int = 10, n_palabras: int = None):
    """Creación y ejecución del modelo LDA para la definición de tópicos y asignación de los
    mismos a los artículos

    Args:
        df (pd.DataFrame): dataframe que contiene los textos ya lematizados
        columna (str): columna de la que se obtendrán los tópicos
        filtro_inf (int, optional): número mínimo de apariciones de una palabra para ser 
        considerada. Defaults to 1.
        filtro_sup (float, optional): proporción máxima de artíulos en los que puede 
        aparecer una palabra. Defaults to 0.2.
        n_iterations (int, optional): número de iteraciones. Defaults to 50. 
        n_workers (int, optional): equivale al número de cores del computador. Defaults to 4.
        n_passes (int, optional): número de veces que pasa por el corpus para entrenarse. 
        Defaults to 10.
        n_palabras (int, optional): número máximo de palabras a considerar en el diccionario. 
        Defaults to None.

    Returns:
        _type_: _description_
    """
    # El limite inferior se establece en 1 puesto que hay empresas con pocos artículos (2) como AES chivor
    df[f'{columna} lematizado'] = df[f'{columna} lematizado'].apply(
        lambda x: x.replace('[', '').replace(']', '').replace('\'', '').split(','))
    diccionario = Dictionary(df[f'{columna} lematizado'])
    diccionario.filter_extremes(
        no_below=filtro_inf, no_above=filtro_sup, keep_n=n_palabras)
    corpus = [diccionario.doc2bow(doc) for doc in df[f'{columna} lematizado']]

    n = n_topicos(corpus=corpus, diccionario=diccionario)

    lda_model = LdaMulticore(corpus=corpus, id2word=diccionario,
                             iterations=iteraciones, num_topics=n, workers=workers, passes=passes)

    topicos = []
    for i in range(n):
        aux = lda_model.print_topic(i).split("\"")
        aux_ = [aux[i] for i in range(len(aux) - 1) if i % 2 != 0]
        topicos.append([i, ", ".join(aux_)])

    df['Topicos'] = [sorted(lda_model[corpus][text])[0][0]
                     for text in range(len(df[columna]))]

    return topicos, df[['index', 'Topicos']]


def dataframe_topicos(empresa_topicos: dict, topicos_general: dict):
    """Función para transformar los tópicos obtenidos asignando un ID
    diferente a cada uno de ellos y relacionarlos con los artículos para
    guardarlos como archivos csv.

    Args:
        empresa_topicos (dict): diccionario que relaciona los artículos
        con los tópicos por empresas.
        topicos_general (dict): diccionario que relaciona los tópicos con
        las palabras que lo componen por empresa.
    """
    count = 0
    topicos_mod = []
    df_topicos = pd.DataFrame()
    for i in topicos_general.keys():
        count_top = 0
        empresa_topicos[i]['Topicos'] = empresa_topicos[i]['Topicos'] + count
        df_topicos = pd.concat(
            [df_topicos, empresa_topicos[i]], ignore_index=True)
        for j in topicos_general[i]:
            topicos_mod.append([count + count_top, j[1]])
            count_top += 1
        count += count_top

    df_dict_topicos = pd.DataFrame(
        topicos_mod, columns=['ID_Topicos', 'Palabras_Topicos'])

    df_topicos = df_topicos.set_index('index')
    df_dict_topicos = df_dict_topicos.set_index('ID_Topicos')

    df_topicos.to_csv('../data/curated/topicos.csv', encoding='utf-8-sig')
    df_dict_topicos.to_csv(
        '../data/curated/dict_topicos.csv', encoding='utf-8-sig')


def topicos(df: pd.DataFrame, columna: str):
    """Función para separar el dataframe por empresas.

    Args:
        df (pd.DataFrame): dataframe que contiene los textos ya lematizados
        columna (str): columna de la que se obtendrán los tópicos
    """
    topicos_general = {}
    empresa_topicos = {}

    empresas = df['Empresa'].unique()
    for empresa in empresas:
        df_aux = df[df['Empresa'] == empresa].reset_index()

        topicos_general[empresa], empresa_topicos[empresa] = lda_model(
            df=df_aux, columna=columna)

    dataframe_topicos(empresa_topicos, topicos_general)


# %% LECTURA Y PREPARACIÓN DE LOS DATOS
# LEER ARCHIVOS CON DATOS
df_raw = pd.read_csv('./data/raw/database.csv',
                     encoding='utf-8-sig', index_col=[0])
df_curated = pd.read_csv(
    './data/curated/curated_database.csv', encoding='utf-8-sig', index_col=[0])

# Verificar cuales articulos no han sido procesados
df = df_raw[~df_raw['Titulo'].isin(df_curated['Titulo'])]
# %%
if len(df) > 0:
    # Estandarización formato fechas
    df['Contenido'] = df['Contenido'].str.replace(
        '\r|\n|\f|\v', ' ')
    df['Titulo'] = df['Titulo'].str.replace('\r|\n|\f|\v', ' ')
    df['Resumen'] = df['Resumen'].str.replace('\r|\n|\f|\v', ' ')
    df['Autor'] = df['Autor'].str.replace('\r|\n|\f|\v', ' ')
    df['Fecha Publicacion'] = pd.to_datetime(
        df['Fecha Publicacion']).dt.strftime('%d-%m-%Y')
    df['Fecha Extraccion'] = pd.to_datetime(
        df['Fecha Extraccion']).dt.strftime('%d-%m-%Y')

    # ELIMINACIÓN COLUMNAS Y FILAS NO RELEVANTES
    # Eliminar filas sin información en la columna Contenido
    df = df.drop(df[df['Contenido'] == "SIN PARRAFOS"].index).reset_index(
        drop=True)
    df = df.drop(df[df['Contenido'].isna()].index).reset_index(drop=True)
    df = df.drop(df[df['Fuente'].isna()].index).reset_index(drop=True)
    df = df.drop(df[df.Contenido.str.len() < 500].index).reset_index(drop=True)
# %%
procesamiento('Contenido', df)
df_palabras = pd.DataFrame()
df_bigramas = pd.DataFrame()
df_trigramas = pd.DataFrame()

len_df = len(df)
len_curated = len(df_curated)

for i in range(len_curated, len_curated + len_df):
    aux_palabras = lista_ngramas(df.loc[i - len_curated, 'Entidades de Contenido'],
                                 df.loc[i - len_curated, 'Contenido procesado'], i, 1)
    df_palabras = pd.concat([df_palabras, aux_palabras], ignore_index=True)

    aux_bigramas = lista_ngramas(df.loc[i - len_curated, 'Entidades de Contenido'],
                                 df.loc[i - len_curated, 'Contenido procesado'], i, 2)
    df_bigramas = pd.concat([df_bigramas, aux_bigramas], ignore_index=True)

    aux_trigramas = lista_ngramas(df.loc[i - len_curated, 'Entidades de Contenido'],
                                  df.loc[i - len_curated, 'Contenido procesado'], i, 3)
    df_trigramas = pd.concat([df_trigramas, aux_trigramas], ignore_index=True)

df_curated = pd.concat([df_curated, df], ignore_index=True)
df_curated.index.name = 'ID_Articulo'
df_curated.to_csv('./data/curated/curated_database.csv', encoding='utf-8-sig')

palabras_csv = pd.read_csv(
    './data/curated/palabras.csv', encoding='utf-8-sig', index_col=[0])
df_palabras = pd.concat([palabras_csv, df_palabras], ignore_index=True)
df_palabras.to_csv('./data/curated/palabras.csv', encoding='utf-8-sig')

bigramas_csv = pd.read_csv(
    './data/curated/bigramas.csv', encoding='utf-8-sig', index_col=[0])
df_bigramas = pd.concat([bigramas_csv, df_bigramas], ignore_index=True)
df_bigramas.to_csv('./data/curated/bigramas.csv', encoding='utf-8-sig')

trigramas_csv = pd.read_csv(
    './data/curated/trigramas.csv', encoding='utf-8-sig', index_col=[0])
df_trigramas = pd.concat([trigramas_csv, df_trigramas], ignore_index=True)
df_trigramas.to_csv('./data/curated/trigramas.csv', encoding='utf-8-sig')

# topicos(df_curated, 'Contenido')
# %%
