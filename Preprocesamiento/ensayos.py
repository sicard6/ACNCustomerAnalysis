import pandas as pd

df_raw = pd.read_csv('./data/raw/database.csv',
                     encoding='utf-8-sig', index_col=[0])
df_curated = pd.read_csv(
    './data/curated/curated_database.csv', encoding='utf-8-sig', index_col=[0])
len_curated = len(df_curated)
# Verificar cuales articulos no han sido procesados
df = df_raw[~df_raw['Titulo'].isin(df_curated['Titulo'])]
len_df = len(df)
print(df_raw.loc[len(df_raw)-1, :])
