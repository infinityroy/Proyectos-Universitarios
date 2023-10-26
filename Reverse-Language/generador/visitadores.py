# python3.9 reverse.py --generar-python docs/ejemplos/factorial.rvs

# from árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
#from utils.tipo_datos import TipoDatos
from utils.árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
from utils.tipo_datos import TipoDatos


class VisitantePython:

    def __init__(self):
        pass

    tabuladores = 0

    def visitar(self, nodo: TipoNodo):
        """
        Este método es necesario por que uso un solo tipo de nodo para
        todas las partes del árbol por facilidad... pero cómo lo hice
        tuanis allá... pues bueno... acá hay que pagar el costo.
        """

        resultado = ''

        if nodo.tipo is TipoNodo.PROGRAMA:
            resultado = self.__visitar_programa(nodo)

        elif nodo.tipo is TipoNodo.FUNCIÓN:
            resultado = self.__visitar_función(nodo)

        elif nodo.tipo is TipoNodo.INICIO:
            resultado = self.__visitar_inicio(nodo)

        elif nodo.tipo is TipoNodo.INSTRUCCIÓN:
            resultado = self.__visitar_instrucción(nodo)

        elif nodo.tipo is TipoNodo.ASIGNACIÓN:
            resultado = self.__visitar_asignación(nodo)

        elif nodo.tipo is TipoNodo.LLAMADA:
            resultado = self.__visitar_llamada(nodo)

        elif nodo.tipo is TipoNodo.IDENTIFICADOR:
            resultado = self.__visitar_identificador(nodo)

        elif nodo.tipo is TipoNodo.EXPRESIÓN:
            resultado = self.__visitar_expresión(nodo)

        elif nodo.tipo is TipoNodo.LITERAL:
            resultado = self.__visitar_literal(nodo)

        elif nodo.tipo is TipoNodo.NÚMERO:
            resultado = self.__visitar_número(nodo)

        elif nodo.tipo is TipoNodo.ENTERO:
            resultado = self.__visitar_entero(nodo)

        elif nodo.tipo is TipoNodo.FLOTANTE:
            resultado = self.__visitar_flotante(nodo)

        elif nodo.tipo is TipoNodo.TEXTO:
            resultado = self.__visitar_texto(nodo)

        elif nodo.tipo is TipoNodo.OPERACIÓN:
            resultado = self.__visitar_operación(nodo)

        elif nodo.tipo is TipoNodo.OPERADOR:
            resultado = self.__visitar_operador(nodo)

        elif nodo.tipo is TipoNodo.PARÁMETROS:
            resultado = self.__visitar_parámetros(nodo)

        elif nodo.tipo is TipoNodo.CONDICIONAL:
            resultado = self.__visitar_condicional(nodo)

        elif nodo.tipo is TipoNodo.EXPRESIÓNCONDICIONAL:
            resultado = self.__visitar_expresión_condicional(nodo)

        elif nodo.tipo is TipoNodo.COMPARACIÓN:
            resultado = self.__visitar_comparación(nodo)

        elif nodo.tipo is TipoNodo.COMPARADOR:
            resultado = self.__visitar_comparador(nodo)

        elif nodo.tipo is TipoNodo.REPETICIÓN:
            resultado = self.__visitar_repetición(nodo)

        elif nodo.tipo is TipoNodo.RETORNO:
            resultado = self.__visitar_retorno(nodo)

        elif nodo.tipo is TipoNodo.BLOQUEINSTRUCCIONES:
            resultado = self.__visitar_bloque_instrucciones(nodo)

        elif nodo.tipo is TipoNodo.PARAMETROSLLAMADA:
            resultado = self.__visitar_parámetros_llamada(nodo)

        elif nodo.tipo is TipoNodo.VALOR:
            resultado = self.__visitar_valor(nodo)

        elif nodo.tipo is TipoNodo.OPERADORLÓGICO:
            resultado = self.__visitar_operador_lógico(nodo)

        else:
            raise Exception('InternalError: Error Interno')

        return resultado

    # CHECK
    def __visitar_programa(self, nodo_actual):
        """
        Programa ::= (Comentario|Asignación|Funcion)*[( )\n]*Inicio
        """

        instrucciones = []
        pos_inicio = -1
        i = 0
        for nodo in nodo_actual.nodos:
            if(nodo.tipo is TipoNodo.INICIO):
                pos_inicio = i
            instrucciones.append(nodo.visitar(self))
            i+=1
        if(pos_inicio != -1):
            instrucciones.append(instrucciones[pos_inicio])
            del instrucciones[pos_inicio]
        return '\n'.join(instrucciones)

    # CHECK
    def __visitar_asignación(self, nodo_actual):
        """
        Asignación ::= Identificador != (Expresión|Llamada)
        """

        resultado = """{} = {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0], instrucciones[1])

    # CHECK
    def __visitar_operación(self, nodo_actual):
        """
        Operación ::= (Valor Operador Valor)
        """
        sumaTexto = False

        if nodo_actual.atributos['tipo'] == TipoDatos.TEXTO:
            sumaTexto = True

        resultado = """{} {} {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            if sumaTexto and nodo.atributos['tipo'] != TipoDatos.TEXTO:
                instrucciones.append('str(' + nodo.visitar(self) + ')')
            else:
                instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0], instrucciones[1], instrucciones[2])

    def __visitar_expresión_matemática(self, nodo_actual):
        """
        ExpresiónMatemática ::= (Expresión) | Número | Identificador

        Ojo esto soportaría un texto
        """

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return ' '.join(instrucciones)

    def __visitar_expresión(self, nodo_actual):
        """
        Expresión ::= Operación|Literal|Identificador
        """
        # Nunca se llega aqui ya que analizar_expresion devuelve un nodo de tipo operacion, literal o identificador

    # CHECK
    def __visitar_función(self, nodo_actual):
        """
        Función ::= (BloqueInstrucciones)indefinir( )+(Identificador)( )*(Parametros)
        """

        resultado = """\ndef {}({}):\n{}"""

        resultado2 = """\ndef {}():\n{}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]
        if len(instrucciones) == 2:
            return resultado2.format(instrucciones[0], '\n'.join(instrucciones[1]))
        return resultado.format(instrucciones[0], instrucciones[1], '\n'.join(instrucciones[2]))

    # CHECK
    def __visitar_llamada(self, nodo_actual):
        """
        Llamada ::= colgar Identificador ( ParametrosLlamada )
        """

        resultado = """{}({})"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return resultado.format(instrucciones[0], instrucciones[1])

    # CHECK
    def __visitar_parámetros_llamada(self, nodo_actual):
        """
        ParametrosLlamada ::== (Valor(,Valor)*)?
        """

        parametros = []

        for nodo in nodo_actual.nodos:
            parametros.append(nodo.visitar(self))

        if len(parametros) > 0:
            return ','.join(parametros)

        else:
            return ''

    # CHECK
    def __visitar_parámetros(self, nodo_actual):
        """
        Parámetros ::= (Identificador(,Identificador)*)?
        """

        parámetros = []

        for nodo in nodo_actual.nodos:
            parámetros.append(nodo.visitar(self))

        if len(parámetros) > 0:
            return ','.join(parámetros)

        else:
            return ''

    # CHECK
    def __visitar_instrucción(self, nodo_actual):
        """
        Instrucción ::= (Asignación|Llamada|Retorno|Repetición|Condicional);
        """

        valor = ""

        for nodo in nodo_actual.nodos:
            valor = nodo.visitar(self)

        return valor

    # CHECK
    def __visitar_repetición(self, nodo_actual):
        """
        Original
        Repetición ::=  }( )*(\n)+BloqueInstrucciones( )*(\n)+romper( )*(ExpresionCondicional)( )*{

        Ya que invertimos el orden de los componentes se leerá
        Condicional ::= romper(ExpresionCondicional){BloqueInstrucciones}
        """

        resultado = """while {}:\n{}"""

        instrucciones = []

        # Visita la condición
        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0], '\n'.join(instrucciones[1]))

    # CHECK
    def __visitar_condicional(self, nodo_actual):
        """
        Ya que invertimos el orden de los componentes se leerá
        Condicional ::= sino(ExpresionCondicional){BloqueInstrucciones*} (ademas{BloqueInstrucciones*})?
        """
        resultado_if = """if {}:\n{}"""
        resultado_else = """\n{}else:\n{}"""

        resultado = """{}{}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        if len(instrucciones) > 2:
            if_string = resultado_if.format(instrucciones[0], '\n'.join(instrucciones[1]))
            else_string = resultado_else.format(self.__retornar_tabuladores(), '\n'.join(instrucciones[2]))
            return resultado.format(if_string, else_string)
        else:
            return resultado_if.format(instrucciones[0], '\n'.join(instrucciones[1]))

    # CHECK #TODO revisar que funcione bien
    def __visitar_expresión_condicional(self, nodo_actual):
        """
        ExpresiónCondicional ::= Comparación( )*((y)|(o))( )*Comparación)?
        """

        resultado = ""

        for nodo in nodo_actual.nodos:
            resultado += nodo.visitar(self) + " "

        return resultado[:-1]

    # CHECK
    def __visitar_comparación(self, nodo_actual):
        """
        Comparación ::= Valor Comparador Valor
        """

        resultado = '{} {} {}'

        elementos = []

        for nodo in nodo_actual.nodos:
            elementos.append(nodo.visitar(self))

        return resultado.format(elementos[0], elementos[1], elementos[2])

    # CHECK
    def __visitar_valor(self, nodo_actual):
        """
        Valor ::= (Identificador | Literal)
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisiss

    # CHECK
    def __visitar_retorno(self, nodo_actual):
        """
        Retorno ::= quedarse( )+Expresion
        """

        resultado = 'return {}'
        valor = ''

        for nodo in nodo_actual.nodos:
            valor = nodo.visitar(self)

        return resultado.format(valor)

    # CHECK
    def __visitar_inicio(self, nodo_actual):
        """
        Inicio ::= fin(BloqueInstrucciones)inicio
        """
        # Este mae solo va a tener un bloque de instrucciones que tengo que
        # ir a visitar

        resultado = """\ndef principal():\n{}\n

if __name__ == '__main__':
    principal()
"""

        instrucciones = []

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return resultado.format('\n'.join(instrucciones[0]))

    # CHECK
    def __visitar_literal(self, nodo_actual):
        """
        Literal ::= Número | Texto
        """
        # Nunca se llega aqui ya que analizar_literal devuelve un numero o texto como tipo de nodo

    # CHECK
    def __visitar_número(self, nodo_actual):
        """
        Número ::= (Entero | Flotante)
        """
        # Nunca se llega aqui ya que analizar_número devuelve un entero o flotante como tipo de nodo

    # CHECK TODO revisar que este bien
    def __visitar_bloque_instrucciones(self, nodo_actual):
        """
        BloqueInstrucciones ::= ( )*(\n)+(Instruccion|Comentario)*( )*(\n)+
        """
        self.tabuladores += 2

        instrucciones = []
        # Visita todas las instrucciones que contiene
        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        instrucciones_tabuladas = []

        for instruccion in instrucciones:
            instrucciones_tabuladas += [self.__retornar_tabuladores() + instruccion]

        self.tabuladores -= 2

        return instrucciones_tabuladas

    # CHECK
    def __visitar_operador(self, nodo_actual):
        """
        Operador ::= [-+/*]
        """
        if nodo_actual.contenido == '+':
            return '-'
        elif nodo_actual.contenido == '-':
            return '+'
        elif nodo_actual.contenido == '/':
            return '*'
        else:
            return '/'

    # CHECK
    def __visitar_operador_lógico(self, nodo_actual):

        if nodo_actual.contenido == 'y':
            return 'and'

        elif nodo_actual.contenido == 'o':
            return 'or'

        else:
            # Nunca llega aquí, es para que se vea bonito
            return 'jijiji'

    def __visitar_valor_verdad(self, nodo_actual):
        """
        ValorVerdad ::= (True | False)
        """
        return nodo_actual.contenido

    # CHECK
    def __visitar_comparador(self, nodo_actual):
        """
        Comparador ::= (!==)|(==)|>|<|(<=)|(>=)
        """
        if nodo_actual.contenido == '<':
            return '>'

        elif nodo_actual.contenido == '>':
            return '<'

        elif nodo_actual.contenido == '!==':
            return '=='

        elif nodo_actual.contenido == '==':
            return '!='

        elif nodo_actual.contenido == '>=':
            return '<='

        elif nodo_actual.contenido == '<=':
            return '>='

    # CHECK
    def __visitar_texto(self, nodo_actual):
        """
        Texto ::= "[a-zA-Z( )0-9]*"
        """
        return nodo_actual.contenido

    # CHECK
    def __visitar_entero(self, nodo_actual):
        """
        Entero ::= (+)?[0-9]+
        """
        return nodo_actual.contenido

    # CHECK
    def __visitar_flotante(self, nodo_actual):
        """
        Flotante ::= (+)?[0-9]+.[0-9]+
        """
        return nodo_actual.contenido

    # CHECK
    def __visitar_identificador(self, nodo_actual):
        """
        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        return nodo_actual.contenido

    def __retornar_tabuladores(self):
        return " " * self.tabuladores
