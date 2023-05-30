# %%
import os
# %%
# Automatización del proceso de extracción y procesamiento de Medios de Comunicación
os.system("python Medios_Comunicacion/Web_Scraping/Scripts/master.py")
os.system("python Medios_Comunicacion/NLP_Analitycs/Scripts/NLP.py")
os.system("python Medios_Comunicacion/NLP_Analitycs/Scripts/Topicos.py")
# %%
