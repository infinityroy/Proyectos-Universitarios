# Explorador para el lenguaje Ciruelas (scanner)
from enum import Enum, auto

import re


class TipoComponente(Enum):
    """
    Enum con los tipos de componentes disponibles

    Esta clase tiene mayormente un propósito de validación
    """
    COMENTARIO = auto()
    PUNTUACION = auto()
    PALABRA_CLAVE = auto()
    CONDICIONAL = auto()
    BLANCOS = auto()
    CAMBIO_LINEA = auto()
    CAMBIO_INSTRUCCION = auto()
    REPETICION = auto()
    ASIGNACION = auto()
    OPERADOR = auto()
    COMPARADOR = auto()
    TEXTO = auto()
    IDENTIFICADOR = auto()
    ENTERO = auto()
    FLOTANTE = auto()
    NINGUNO = auto()


class ComponenteLéxico:
    """
    Clase que almacena la información de un componente léxico
    """

    tipo: TipoComponente
    texto: str
    atributos: dict

    def __init__(self, tipo_nuevo: TipoComponente, texto_nuevo: str, fila_nueva: int, columna_nueva: int):
        self.tipo = tipo_nuevo
        self.texto = texto_nuevo
        self.atributos = dict()
        self.atributos['Fila'] = fila_nueva
        self.atributos['Columna'] = columna_nueva

    def attributesStr(self):
        """
        Da una representación en texto de los atributos usando string
        de formato de python.
        """
        resultado = ""
        band = True
        attibutosArray = self.atributos.items()
        for descripcion, atributo in attibutosArray:
            if not band:
                resultado += ", "
            band = False
            resultado += f'{descripcion}: {atributo}'
        return resultado

    def __str__(self):
        """
        Da una representación en texto de la instancia actual usando un
        string de formato de python (ver 'python string formatting' en
        google)
        """

        # resultado = f'{self.tipo:30} <{self.texto}>' #Formato anterior
        resultado = f'<"{self.tipo.name}", "{self.texto}", "{self.attributesStr()}">'  # formato según especificación del proyecto
        return resultado


class Explorador:
    """
    Clase que lleva el proceso principal de exploración y deja listos los 
    los componentes léxicos usando para ello los descriptores de
    componente.

    Un descriptor de componente es una tupla con dos elementos:
        - El tipo de componente
        - Un string de regex que describe los textos que son generados para
          ese componente
    """

    descriptores_componentes = [(TipoComponente.COMENTARIO, r'^\*/.*/\*'),
                                (TipoComponente.PUNTUACION, r'^([,{}()])'),
                                (TipoComponente.PALABRA_CLAVE,
                                 r'^(indefinir|quedarse|fin|inicio|colgar|(y(\s)+)|(o(\s)+))'),
                                (TipoComponente.CONDICIONAL, r'^(sino|ademas)'),
                                (TipoComponente.CAMBIO_LINEA, r'^((\n)+)'),
                                (TipoComponente.CAMBIO_INSTRUCCION, r'^(;+)'),
                                (TipoComponente.REPETICION, r'^(romper)'),
                                (TipoComponente.COMPARADOR,
                                 r'^(!==|==|>=|<=|>|<)'),
                                (TipoComponente.ASIGNACION, r'^(!=)'),
                                (TipoComponente.OPERADOR, r'^(-|\+|/|\*)'),
                                (TipoComponente.TEXTO, r'^(".*")'),
                                (TipoComponente.IDENTIFICADOR, r'^([a-z][a-zA-Z_0-9]*)'),
                                (TipoComponente.FLOTANTE, r'^((\+)?[0-9]+\.[0-9]+)'),
                                (TipoComponente.ENTERO, r'^((\+)?[0-9]+)'),
                                (TipoComponente.BLANCOS, r'^(\s)+')]

    def __init__(self, contenido_archivo):
        self.texto = contenido_archivo
        self.componentes = []

    def explorar(self):
        """
        Itera sobre cada una de las líneas y las va procesando de forma que
        se generan los componentes lexicos necesarios en la etapa de
        análisis
        """
        fila = 0
        for linea in self.texto:
            fila += 1
            resultado = self.procesar_linea(linea, fila)
            self.componentes = resultado + self.componentes

    def imprimir_componentes(self):
        """
        Imprime en pantalla en formato amigable al usuario los componentes
        léxicos creados a partir del archivo de entrada
        """

        for componente in self.componentes:
            print(componente)  # Esto funciona por que el print llama al
            # método __str__ de la instancia

    def procesar_linea(self, linea, fila):
        """
        Toma cada línea y la procesa extrayendo los componentes léxicos.
        """

        componentes = []
        columna = 0
        # Toma una línea y le va cortando pedazos hasta que se acaba
        while linea != "":
            # Separa los descriptores de componente en dos variables
            for tipo_componente, regex in self.descriptores_componentes:
                # Trata de hacer match con el descriptor actual
                respuesta = re.match(regex, linea)

                # Si hay coincidencia se procede a generar el componente
                # léxico final
                if respuesta is not None:
                    # si la coincidencia corresponde a un BLANCO o un
                    # COMENTARIO se ignora por que no se ocupa

                    if (tipo_componente is not TipoComponente.BLANCOS and
                            tipo_componente is not TipoComponente.COMENTARIO):
                        # Crea el componente léxico y lo guarda
                        nuevo_componente = ComponenteLéxico(tipo_componente, respuesta.group().strip(), fila, columna)
                        componentes.append(nuevo_componente)
                    columna += respuesta.end()
                    # Se elimina el pedazo que hizo match
                    linea = linea[respuesta.end():]

                    break
                else:
                    # Si ya se pasaron por todos los componentes se asume existe un error en la sintaxis
                    if tipo_componente is self.descriptores_componentes[-1][0]:
                        print(
                            f'Error en la linea {fila}, columna {columna}. {linea} se presenta un símbolo desconocido')
                        linea = linea[-1]
                        break
        return componentes
