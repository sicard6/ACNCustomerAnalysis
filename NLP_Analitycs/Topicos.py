# %%
# Librerías
import pyLDAvis.gensim_models
from tqdm import tqdm
from gensim.models import CoherenceModel
from gensim.models import LdaMulticore
from gensim.corpora.dictionary import Dictionary
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
pyLDAvis.enable_notebook()

# %%
# Funciones


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


def n_topicos(df: pd.DataFrame, columna: str, corpus: list, diccionario: Dictionary, n_iterations: int = 10, n_workers: int = 4, n_passes: int = 10, n_random_state: int = 100, max_topicos: int = 12, min_topicos: int = 2):
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
    for i in tqdm(range(min_topicos, max_topicos + 1, 1)):
        lda_model = LdaMulticore(corpus=corpus, id2word=diccionario, iterations=n_iterations,
                                 num_topics=i, workers=n_workers, passes=n_passes, random_state=n_random_state)
        cm_umass = CoherenceModel(
            model=lda_model, corpus=corpus, dictionary=diccionario, coherence='u_mass')
        # cm_v = CoherenceModel(model=lda_model, texts = df[f'{columna} lematizado'], corpus=corpus, dictionary=diccionario, coherence='c_v')
        topicos.append(i)
        puntaje_umass.append(cm_umass.get_coherence())
        # score_v.append(cm_v.get_coherence())

    n = mejor_puntaje(topicos, puntaje_umass)
    return n


def lda_model(df: pd.DataFrame, columna: str, filtro_inf: int = 1, filtro_sup: float = 0.5, iteraciones: int = 50, workers: int = 4, passes: int = 10, n_palabras: int = None):
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
    df[f'{columna} lematizado'] = df[f'{columna} lematizado'].apply(
        lambda x: x.replace('[', '').replace(']', '').replace('\'', '').split(','))
    diccionario = Dictionary(df[f'{columna} lematizado'])
    diccionario.filter_extremes(
        no_below=filtro_inf, no_above=filtro_sup, keep_n=n_palabras)
    corpus = [diccionario.doc2bow(doc) for doc in df[f'{columna} lematizado']]

    n = n_topicos(df=df, columna=columna, corpus=corpus,
                  diccionario=diccionario)

    lda_model = LdaMulticore(corpus=corpus, id2word=diccionario,
                             iterations=iteraciones, num_topics=n, workers=workers, passes=passes)

    topicos = []
    for i in range(n):
        aux = lda_model.print_topic(i).split("\"")
        aux_ = [aux[i].replace(" ", "")
                for i in range(len(aux) - 1) if i % 2 != 0]
        topicos.append([i, ", ".join(aux_)])

    df['ID_Topico'] = [sorted(lda_model[corpus][text])[0][0]
                       for text in range(len(df[columna]))]

    return topicos, df[['ID_Articulo', 'ID_Topico']]


def main():
    df = pd.read_csv('../data/curated/curated_database.csv',
                     encoding='utf-8-sig', index_col=[0])

    topicos_general = {}
    empresa_topicos = {}

    empresas = df['Empresa'].unique()
    for empresa in tqdm(empresas):
        df_aux = df[df['Empresa'] == empresa].reset_index()

        topicos_general[empresa], empresa_topicos[empresa] = lda_model(
            df=df_aux, columna='Contenido')

    count = 0
    topicos_mod = []
    df_topicos = pd.DataFrame()
    for i in topicos_general.keys():
        count_top = 0
        empresa_topicos[i]['ID_Topico'] = empresa_topicos[i]['ID_Topico'] + count
        df_topicos = pd.concat(
            [df_topicos, empresa_topicos[i]], ignore_index=True)
        for j in topicos_general[i]:
            topicos_mod.append([count + count_top, j[1]])
            count_top += 1
        count += count_top

    df_dict_topicos = pd.DataFrame(
        topicos_mod, columns=['ID_Topico', 'Topico'])

    df_topicos = df_topicos.set_index('ID_Articulo')
    df_dict_topicos = df_dict_topicos.set_index('ID_Topico')

    df_topicos.to_csv('../data/curated/topicos.csv', encoding='utf-8-sig')
    df_dict_topicos.to_csv(
        '../data/curated/dict_topicos.csv', encoding='utf-8-sig')


if __name__ == "__main__":
    main()
