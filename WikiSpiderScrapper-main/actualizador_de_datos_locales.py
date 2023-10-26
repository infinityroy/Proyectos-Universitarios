import os
from datetime import datetime
import yaml


# Genera archivos con el texto ya limpio y con sus metadatos
# Contenido es una tupla (Titulo,texto) y metadatos es una arreglo de tuplas (nombreMetadato, valorMetadato) 
# tokens es una lista de Strings ["mamifero","insecto"],
# sinonimos es una lista de sinonimos de los tokens [["ballena","perro"],["escorpion","garrapata"]]

def generar(Contenido, Metadatos, tokens, sinonimos):
    rutaContenido = "archivos/" + Contenido[0] + ".txt"  # Ruta para archivo de contenido
    rutaMetadatos = "metadatos/" + Contenido[0] + "-metadatos.txt"  # Ruta para archivo de metadatos
    rutaTokens = "tokens/" + Contenido[0] + "-Tokens.txt"
    rutaSinonimos = "sinonimos/" + Contenido[0] + "-Sinonimos.txt"
    if os.path.exists(rutaContenido):  # Si existe entonces actualiza los datos.

        # Actualiza archivo de contenido
        generarArchivoContenido(Contenido[1], rutaContenido)
        # Obtiene la fecha de creacion
        file = open(rutaMetadatos)
        lines = file.read()
        first = lines.split('\n', 1)[0]
        file.close()
        # Actualizar archivo metadatos
        generarArchivoMetadatos(Metadatos, rutaMetadatos, first)
        guardarPreProcesamiento(tokens, rutaTokens)
        guardarPreProcesamiento(sinonimos, rutaSinonimos)

    else:  # Si no existe crear los dos archivos.
        # Crea archivo de metadatos
        FechaCreacion = "Fecha de creacion: " + datetime.today().strftime('%Y-%m-%d') + "\n"
        generarArchivoMetadatos(Metadatos, rutaMetadatos, FechaCreacion)
        generarArchivoContenido(Contenido[1], rutaContenido)
        guardarPreProcesamiento(tokens, rutaTokens)
        guardarPreProcesamiento(sinonimos, rutaSinonimos)


def generarArchivoMetadatos(Metadatos, rutaMetadatos, FechaCreacion):
    # Crea archivo de metadatos
    file = open(rutaMetadatos, "w")
    file.write(FechaCreacion)
    for i in Metadatos:
        file.write(i[0] + ": " + i[1] + "\n")
    file.close()


def generarArchivoContenido(Contenido, rutaContenido):
    # Crea archivo de contenido
    file = open(rutaContenido, "w", encoding='utf8')
    file.write(Contenido)
    file.close()


# Crea archivos de preprocesamiento, llega una estructura python y una ruta. Guarda tokens y sinonimos.
def guardarPreProcesamiento(data, path):
    with open(path, 'w') as f:
        yaml.dump(data, f)