# %%
import os
# %%

path = "C:/Users/' + os.getlogin() + '/OneDrive - Accenture/ACNCustomerAnalysis/Medios_Comunicacion"

os.system(f"python" + path + "/Web_Scraping/Scripts/master.py")
os.system(f"python" + path + "/NLP_Analitycs/Scripts/NLP.py")
os.system(f"python" + path + "/NLP_Analitycs/Scripts/Topicos.py")
