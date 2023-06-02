# %%
import os
# %%

base_path = os.getcwd()
path_webscraping = os.path.join(
    "Medios_Comunicacion", "Web_Scraping", "Scripts")
path_nlp = os.path.join("Medios_Comunicacion", "NLP_Analitycs", "Scripts")
# Automatización del proceso de extracción y procesamiento de Medios de Comunicación
os.system(f"python {os.path.join(path_webscraping, 'master.py')}")
os.system(f"python {os.path.join(path_nlp, 'NLP.py')}")
os.system(f"python {os.path.join(path_nlp, 'Topicos.py')}")
# %%
