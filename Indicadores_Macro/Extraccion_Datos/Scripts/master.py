# %%
from datetime import datetime
import pandas as pd
import json
import os
import sys
# %%

# Lee el archivo .json con los idicadores ecónomicos que s van a recolectar
path = 'C:/Users/' + os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Indicadores_Macro'
end_date = datetime.today().strftime('%d-%m-%Y')
with open(path+'/Extraccion_Datos/config.json') as f:
    data = json.load(f)

# Ciclo para correr los scripts y consolidar la información en un solo Data Frame
dataframes = []
for toImport in data['Indicadores']:
    exec(f'import {toImport["Indicador"]}')

    exec(
        f"df_aux = {toImport['Indicador']}.extraer('01-01-1990', '{end_date}')")

    dataframes.append(df_aux)

    print(
        f"----------------------{toImport['Indicador']}----------------------")

pd.concat(dataframes, ignore_index=True).to_csv(path+'/Data/Raw/database.csv')
# %%
