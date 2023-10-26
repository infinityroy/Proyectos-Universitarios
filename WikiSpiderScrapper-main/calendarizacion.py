import datetime as DateTime
from YamlFile import load_yaml, save_yaml

import cordinador_de_hilos

CONFIGPATH = "config.yaml"
DEFAULTURL = "https://en.wikipedia.org/wiki/Arachnida"
URLSPATH = "urls.yaml"
DEBUG = False


def calendarizar():
    config = load_yaml(CONFIGPATH)
    totalUrls = load_yaml(URLSPATH)
    urls = [k for k, v in totalUrls.items() if v <= DateTime.date.today()]
    todayUrls = urls[:config['maxPerDay']]
    tomorrowUrls = urls[config['maxPerDay']:]
    for url in todayUrls:
        totalUrls[url] = totalUrls[url] + DateTime.timedelta(days=config['revisitTime'])
    for url in tomorrowUrls:
        totalUrls[url] = totalUrls[url] + DateTime.timedelta(days=1)
    if not todayUrls:
        print("Nada calendarizado para hoy")
        return
    if DEBUG:
        print("\nAll Urls: ")
        for i in urls:
            print(i)
        print("\nToday Urls: ")
        for i in todayUrls:
            print(i)
        print("\nTomorrow Urls: ")
        for i in tomorrowUrls:
            print(i)
        print("\nUrls:")
        for k, v in totalUrls.items():
            print(k, "->", v)
    cordinador_de_hilos.inicio(config['requestAtSameTime'], config['requestWaitTime'], config['treeDepth'],
                               config['revisitTime'], True, todayUrls)
    save_yaml(totalUrls, URLSPATH)


calendarizar()
