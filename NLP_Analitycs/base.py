from mimetypes import init
import os, re, pandas as pd, numpy as np, gensim, matplotlib.pyplot as plt, warnings, spacy
from gensim.models import LdaMulticore
from gensim.corpora import Dictionary

warnings.filterwarnings("ignore")


def read_data(path: str,columns: list):
    """Permite leer la información del WS, ajustar encoding convenientemente. 
       # TODO Encoding de raw data
    args:
        path (str): Ruta del archivo
        columns (list): Lista de columnas a traer del archivo
    Returns:
        df (DataFrame()): Genera un solo DF con el compilado de todas las fuentes ".csv"
    """
    fuentes = list(pd.Series(os.listdir(path))[pd.Series(os.listdir(path)).str.contains('.csv')])
    df = pd.DataFrame(columns=columns)
    
    for fuente in fuentes:
        if (fuente == "larepublica.csv"):
            df_ = pd.read_csv(path+fuente, sep = ',', encoding = 'latin_1')
            df_['Fuente'] = fuente
        else:
            df_ = pd.read_csv(path+fuente, sep = ',', encoding = 'latin_1')
            df_['Fuente'] = fuente
        df = pd.concat([df, df_], axis=0)
    df = df.drop(df[df['Contenido'] == "SIN PARRAFOS"].index).reset_index(drop=True)
    return df

def pre_proc_text(df_: pd.DataFrame, tipo: str):
    '''
    Estandariza, elimina bugs de cada texto
    Args:
        df_ (Object): DataFrame resultado del WS
        tipoc (Str): Tipo de segmento de informacion a analizar ("Titulo", "Resumen", "Contenido")
    output:
        lemma_words (List): Lista con palabras lematizadas
        lda_words: 
    '''
    es = spacy.load('es_core_news_lg')
    stop_words = es.Defaults.stop_words
    # stop_words.extend([]) # Agregar palabras de ser necesario
    a,b = 'áéíóúü','aeiouu'
    trans = str.maketrans(a,b)
    # Filtrado de informacion para analisis
    texto = df_[tipo]
    
    texts = texto.str.lower()
    #texts = texts.str.replace(cliente_.lower(), '', regex=True)
    texts = texts.str.replace('[0-9]', '', regex=True)
    texts = texts.str.replace('\W', ' ', regex=True).str.strip()
    texts = texts.str.replace(' {2,}', ' ', regex=True)
    texts = texts.apply(lambda x: str(x).translate(trans))
    texts = texts.apply(
        lambda x: ' '.join(pd.Series(re.split(' ', x))[~pd.Series(re.split(' ', x)).isin(stop_words)].tolist())
    )
    lda_words = texts.str.split('\W')
    return lda_words

def useLDA(texts: list, n: int):
    """ Ejecuta LDA por texto analizado
    Args:
        texts (list): Texto luego de pre-procesamiento
        n (int): Numero de topics a encontrar
    """
    dictionary = Dictionary(texts)
    bow_corpus = [dictionary.doc2bow(doc) for doc in texts]
    lda_model = LdaMulticore(bow_corpus, num_topics=n, id2word=dictionary, passes=2, workers=2)
    return lda_model.show_topics(num_topics=1, num_words=5, log=False, formatted=False)  # show_topics()[0][1]