# Clases para el manejo de un árbol de sintáxis abstracta

from enum import Enum, auto

import copy


class TipoNodo(Enum):
    """
    Describe el tipo de nodo del árbol
    """
    PROGRAMA = auto()
    FUNCIÓN = auto()
    INICIO = auto()
    INSTRUCCIÓN = auto()
    ASIGNACIÓN = auto()
    LLAMADA = auto()
    IDENTIFICADOR = auto()
    EXPRESIÓN = auto()
    LITERAL = auto()
    NÚMERO = auto()
    ENTERO = auto()
    FLOTANTE = auto()
    TEXTO = auto()
    OPERACIÓN = auto()
    OPERADOR = auto()
    PARÁMETROS = auto()
    CONDICIONAL = auto()
    EXPRESIÓNCONDICIONAL = auto()
    COMPARACIÓN = auto()
    COMPARADOR = auto()
    REPETICIÓN = auto()
    RETORNO = auto()
    BLOQUEINSTRUCCIONES = auto()
    PARAMETROSLLAMADA = auto()
    VALOR = auto()
    OPERADORLÓGICO = auto()


class NodoÁrbol:
    tipo: TipoNodo
    nodos: list[object]
    contenido: str
    atributos: dict

    def __init__(self, tipo, contenido=None, nodos=[], atributos={}):

        self.tipo = tipo
        self.contenido = contenido
        self.nodos = nodos
        self.atributos = copy.deepcopy(atributos)

    def visitar(self, visitante):
        return visitante.visitar(self)

    def __str__(self):

        # Coloca la información del nodo
        resultado = '{:30}\t'.format(self.tipo)

        if self.contenido is not None:
            resultado += '{:10}\t'.format(self.contenido)
        else:
            resultado += '{:10}\t'.format('')

        if self.atributos != {}:
            resultado += '{:38}'.format(str(self.atributos))
        else:
            resultado += '{:38}\t'.format('')

        if self.nodos != []:
            resultado += '<'

            # Imprime los tipos de los nodos del nivel siguiente
            for nodo in self.nodos[:-1]:
                if nodo is not None:
                    resultado += '{},'.format(nodo.tipo)

            resultado += '{}'.format(self.nodos[-1].tipo)
            resultado += '>'

        return resultado


class ÁrbolSintáxisAbstracta:
    raiz: NodoÁrbol

    def imprimir_preorden(self):
        self.__preorden(self.raiz)

    def __preorden(self, nodo):

        print(nodo)

        if nodo is not None:
            for nodo in nodo.nodos:
                self.__preorden(nodo)
