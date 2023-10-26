# Este es el archivo que agarro para limpiarlo y genero uno nuevo.txt
"""
1. Analisis léxico
2. Eliminar stp word
3. Lematizacion
4. Seleccion de terminos
5. Dinosaurios
"""

# Instalar esto XD
# pip install -U gensim
# pip install -U spacy
# pip install -U nltk

from ast import Try
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader.wordnet import WordNetError


# Descomentar las siguientes 3 lineas para instalar nltk
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')
# Aqui se hace la lematización y se tokeniza
def lematizeWord(tokens):
    lemmatizer = WordNetLemmatizer()
    r = []
    for i in tokens:
        r += [lemmatizer.lemmatize(i)]
    return r


# eliminador de stop words
# https://stackabuse.com/removing-stop-words-from-strings-in-python/
def eliminar_stopwords(tokens, stop_words):
    r = [w for w in tokens if not w.lower() in stop_words]
    return r


# Filtro
def selection(tokens):
    r = []
    for i in tokens:
        if not re.match(r"^[0-9 , .]", i):
            r += [i]
    return r


# TESAURUS-----------------------------
# https://es.acervolima.com/como-obtener-sinonimos-antonimos-de-nltk-wordnet-en-python/
def getsynonyms(word):
    # Genera una lista de sinonimos para una palabra
    synonyms = []
    try:
        for syn in wordnet.synsets(word):
            for i in syn.lemmas():
                synonyms.append(i.name())
    except:
        return []

    return list(set(synonyms))


# 🦖🦖🦖
def Tesauros(tokens):
    tokens_synonyms = []
    for i in tokens:
        tokens_synonyms.append(getsynonyms(i))
    return tokens_synonyms


def preprocesarTexto(t, stop_words):
    tokens = word_tokenize(t)
    not_stop_words = eliminar_stopwords(tokens, stop_words)
    lematize = lematizeWord(not_stop_words)
    selc = selection(lematize)
    tesaurus = Tesauros(selc)

    return [selc, tesaurus]
