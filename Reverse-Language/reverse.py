# Archivo principal para el compilador
# import sys
import argparse

# sys.path.append('C:/Users/Meta/Desktop/U/Compi/learn-gitlab/utils')
# sys.path.append('C:/Users/Meta/Desktop/U/Compi/learn-gitlab/analizador')
# import archivos as utils
from utils import archivos as utils
from explorador.explorador import Explorador
# from analizador import Analizador
from analizador.analizador import Analizador
from verificador.verificador import Verificador
from generador.generador import Generador

parser = argparse.ArgumentParser(description='Interprete para Ciruelas (el lenguaje)')

parser.add_argument('--solo-explorar', dest='explorador', action='store_true',
                    help='ejecuta solo el explorador y retorna una lista de componentes léxicos')

parser.add_argument('--solo-analizar', dest='analizador', action='store_true',
                    help='ejecuta hasta el analizador y retorna un preorden del árbol sintáctico')

parser.add_argument('--solo-verificar', dest='verificador', action='store_true',
                    help='''ejecuta hasta el verificador y retorna un preorden del árbol
        sintáctico y estructuras de apoyo generadas en la verificación''')

parser.add_argument('--generar-python', dest='python', action='store_true',
                    help='''Genera código python''')

parser.add_argument('--guardar', dest='guardar',
                    help='''guarda código python''')

parser.add_argument('archivo',
                    help='Archivo de código fuente')


def reverse():
    args = parser.parse_args()
    args_vars = vars(args)

    if args.explorador is True:

        # Carga el archivo .rvs
        texto = utils.cargar_archivo(args.archivo)

        # Crea el Explorador con el archivo .rvs
        exp = Explorador(texto)

        # Explora el archivo .rvs
        exp.explorar()

        # Imprime los componentes encontrados en la exploración
        exp.imprimir_componentes()
    elif args.analizador is True:

        # Carga el archivo .rvs
        texto = utils.cargar_archivo(args.archivo)

        # Crea el Explorador con el archivo .rvs
        exp = Explorador(texto)

        # Explora el archivo .rvs
        exp.explorar()

        # Crea el Analizador con los componentes encontrandos en la exploración
        analizador = Analizador(exp.componentes)

        # Analiza el archivo .rvs
        if analizador.analizar():
            # Imprime el Árbol de Sintáxis Abstracta (A.S.A)
            analizador.imprimir_asa()
    elif args.verificador is True: 

        texto = utils.cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        analizador = Analizador(exp.componentes)
        if not analizador.analizar():
            return

        verificador = Verificador(analizador.asa)
        if verificador.verificar():
            verificador.imprimir_asa()
    
    elif args.python is True:

        texto = utils.cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        analizador = Analizador(exp.componentes)
        if not analizador.analizar():
            return

        verificador = Verificador(analizador.asa)
        if not verificador.verificar():
            return

        generador = Generador(verificador.asa)
        generador.generar()
        if args.guardar != None:
            generador.guardar(args.guardar)

    else:
        # Imprime ayuda para utilizar reverse
        parser.print_help()


if __name__ == '__main__':
    reverse()
