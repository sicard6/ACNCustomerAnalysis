# %%
from datetime import datetime
import pandas as pd
import json
import os
import sys
# %%
path = 'C:/Users/' + os.getlogin() + \
    '/OneDrive - Accenture/ACNCustomerAnalysis/Indicadores_Macro'
end_date = datetime.today().strftime('%d-%m-%Y')
with open(path+'/Extraccion_Datos/config.json') as f:
    data = json.load(f)
# %%
dataframes = []
for toImport in data['Indicadores']:
    exec(f'import {toImport["Indicador"]}')

    exec(
        f"df_aux = {toImport['Indicador']}.extraer('01-01-1990', '{end_date}')")

    dataframes.append(df_aux)

print(pd.concat(dataframes, ignore_index=True))

# %%
