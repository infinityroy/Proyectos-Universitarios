# Implementa el veficador de ciruelas
import os

from utils.árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
# from árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
from generador.visitadores import VisitantePython


class Generador:
    asa: ÁrbolSintáxisAbstracta
    visitador: VisitantePython
    resultado: str

    ambiente_estandar = """\nimport sys \nimport random


def numero_seguro(inicio, fin):
    r1 = random.randint(inicio, fin)
    return r1

def ocultar(texto):
    print(texto)
"""

    def __init__(self, nuevo_asa: ÁrbolSintáxisAbstracta):

        self.asa = nuevo_asa
        self.visitador = VisitantePython()

    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """

        if self.asa.raiz is None:
            print([])
        else:
            self.asa.imprimir_preorden()

    def guardar(self, nombre):
        file = open(f'{nombre}.py', "w")
        file.write(self.ambiente_estandar)
        file.write(self.resultado)
        file.close()

    def ejecutar(self):
        exec(self.resultado)

    def generar(self):
        self.resultado = self.visitador.visitar(self.asa.raiz)
        print(self.ambiente_estandar)
        print(self.resultado)
