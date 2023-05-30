# %%
import json
import os
# %%

# Leer el archivo json con los nombres de los medios y clientes
with open('Medios_Comunicacion/Web_Scraping/config.json') as f:
    data = json.load(f)

# Ciclo para correr los scripts que se encargan del web scraping
for i in data["medios"]:
    for j in i["clientes"]:
        if " " in j:
            j = j.strip().replace(" ", "_")
            os.system(
                f"python Medios_Comunicacion/Web_Scraping/Scripts/{i['fuente']}.py {j}")
# %%
