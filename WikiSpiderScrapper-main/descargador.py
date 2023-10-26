import requests
from bs4 import BeautifulSoup


def hacer_solicitud(url):
    response = requests.get(url=url, )
    return response

def parse_response_links(response, diccionarioDeUrls, urlsVisitados, nivel, agregar):
    soup = BeautifulSoup(response.content, 'html.parser')

    if agregar:
        allLinks = soup.select('p > a')

        for link in allLinks:
            # nos aseguramos que el enlace sea a otro articulo en el tema
            if link['href'].find("/wiki/") == 0 \
                    and link['href'].find("/wiki/Ayuda") == -1\
                    and link['href'].find("/wiki/File:") == -1:
                if link.text in diccionarioDeUrls or link.text in urlsVisitados:
                    continue
                diccionarioDeUrls["https://en.wikipedia.org" + link['href']] = nivel+1


def parse_response(response):
    soup = BeautifulSoup(response.content, 'html.parser')

    # encontramos todos los parrafos y el titulo
    allLegibleText = '\n'.join([paragraph.text for paragraph in soup.select("p")])
    titulo = soup.find(id="firstHeading").text

    return [titulo, allLegibleText]

def get_links(url, diccionarioDeUrls, urlsVisitados, nivel, agregar):
    return parse_response((hacer_solicitud(url)), diccionarioDeUrls, urlsVisitados, nivel, agregar)

def parcear_articulo(url):
    return parse_response(hacer_solicitud(url))
