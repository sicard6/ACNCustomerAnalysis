# %%
import json
import os
# %%
with open('Web_Scraping\config.json') as f:
    data = json.load(f)
# %%
for i in data["medios"]:
    for j in i["clientes"]:
        if " " in j:
            j = j.strip().replace(" ", "_")
        os.system(f"python Web_Scraping\{i['fuente']}.py {j}")
# %%
