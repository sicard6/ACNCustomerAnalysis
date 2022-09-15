#In[]
import pandas as pd
import gensim 
from gensim import corpora
import pyLDAvis.gensim_models
import nltk
nltk.download('omw-1.4')
nltk.download('stopwords')
from nltk.corpus import stopwords
import string
from nltk.stem.wordnet import WordNetLemmatizer
from googletrans import Translator
translator = Translator()
import warnings
warnings.simplefilter('ignore')
from itertools import chain
#In[]

df = pd.read_csv(r'C:\Users\nicolas.gomez.garzon\Desarrollos\NLP\ACNCustomerAnalysis\data\raw\semana.csv')[['Empresa','Contenido']]
df['Contenido']=df['Contenido'].apply(lambda x: translator.translate(x[:4000], dest='en').text)
df['Languaje']=df['Contenido'].apply(lambda x: translator.detect(x).lang)
df.rename(columns={'Contenido':'text'},inplace=True)
df.rename(columns={'Empresa':'topic'},inplace=True)
df.drop_duplicates(inplace=True)
df = df[~df.text.isin(['NO PARAGRAPHS']) & df.Languaje.isin(['en'])]
df
#In[]

#clean the data
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def clean(text):
    stop_free = ' '.join([word for word in text.lower().split() if word not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = ' '.join([lemma.lemmatize(word) for word in punc_free.split()])
    return normalized.split()

#In[]

df['text_clean']=df['text'].apply(clean)
#In[]
df
# %%

dictionary = corpora.Dictionary(df['text_clean'])

print(dictionary.num_nnz)
# %%

doc_term_matrix = [dictionary.doc2bow(doc) for doc in df['text_clean'] ]
print(len(doc_term_matrix))
# %%

lda = gensim.models.ldamodel.LdaModel
# %%
num_topics=7
ldamodel = lda(doc_term_matrix,num_topics=num_topics,id2word=dictionary,passes=50,minimum_probability=0)
# %%
ldamodel.print_topics(num_topics=num_topics)
# %%
lda_display = pyLDAvis.gensim_models.prepare(ldamodel, doc_term_matrix, dictionary, sort_topics=False, mds='mmds')
pyLDAvis.display(lda_display)
# %%

lda_corpus = ldamodel[doc_term_matrix]
# %%
scores = list(chain(*[[score for topic_id,score in topic] \
                    for topic in [doc for doc in lda_corpus]]))

# %%
clusters = []
for  a in range (num_topics):
    clusters.append([j for i,j in zip(lda_corpus,df.index) if i[a][1] > 0.9]) 

# %%
for cluster in clusters:
    df=df.assign(**{'cluster{}'.format(clusters.index(cluster)):df.index.isin(cluster)})
df.drop(columns=['text_clean','Languaje'],inplace=True)
df.to_csv(r'C:\Users\nicolas.gomez.garzon\Desarrollos\NLP\ACNCustomerAnalysis\data\curated\semana.csv',index=False)
# %%
