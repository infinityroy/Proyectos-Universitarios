import datetime
import time
import random

from threading import Thread, Semaphore
from YamlFile import save_yaml
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from actualizador_de_datos_locales import generar
from descargador import get_links, parcear_articulo
from pre_procesamiento_de_texto import preprocesarTexto

diccionarioDeUrls = {'https://en.wikipedia.org/wiki/Arachnid': 1}
listaUrls = []
visitados = {}

semaforo_lista_urls = Semaphore(1)
semaforo_visitados = Semaphore(1)
semaforo_diccionario = Semaphore(1)


def inicio(canthilos, tiempo_de_espera, nivel_maximo, dias_proxima_revision, exploración, lista_de_urls):
    listaUrls.extend(lista_de_urls)
    wn.ensure_loaded()
    stop_words = stopwords.words("english")

    hilos = []
    for i in range(canthilos):
        t = Thread(target=hilo, args=[tiempo_de_espera, nivel_maximo, dias_proxima_revision, exploración, stop_words])
        hilos.append(t)
        t.start()
    for i in hilos:
        i.join()
    if exploración:
        save_yaml(visitados, "urlsNuevos.yaml")
    # Guardar nuevas fechas de urls
    return 0


def hilo(tiempo_de_espera, nivel_maximo, dias_proxima_revision, exploración, stop_words):
    while listaUrls:
        semaforo_lista_urls.acquire()

        if (exploración):
            url, nivel = random.choice(list(diccionarioDeUrls.items()))
            agregar = nivel != nivel_maximo

            semaforo_visitados.acquire()
            visitados[url] = datetime.date.today() + datetime.timedelta(days=dias_proxima_revision)
            semaforo_visitados.release()

            semaforo_diccionario.acquire()
            get_links(url, diccionarioDeUrls, visitados, nivel, agregar)
            semaforo_diccionario.release()

            semaforo_lista_urls.release()
            time.sleep(tiempo_de_espera)
            continue

        url = listaUrls.pop()

        semaforo_lista_urls.release()

        titulo, allLegibleText = parcear_articulo(url)

        tokens, sinonimos = preprocesarTexto(allLegibleText, stop_words)

        metadatos = [["url", url], ["Ultima actualizacion", datetime.date.today().strftime("%Y-%m-%d")],
                     ["Fecha de revisitacion",
                      (datetime.date.today() + datetime.timedelta(days=dias_proxima_revision)).strftime("%Y-%m-%d")]]

        generar([titulo, allLegibleText], metadatos, tokens, sinonimos)
        time.sleep(tiempo_de_espera)

    return
