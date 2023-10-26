# Analizador de Ciruelas (el lenguaje de programación)

from explorador.explorador import TipoComponente, ComponenteLéxico

# from árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
from utils.árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo


class Analizador:
    componentes_léxicos: list
    cantidad_componentes: int
    posición_componente_actual: int
    componente_actual: ComponenteLéxico

    def __init__(self, lista_componentes):

        self.componentes_léxicos = lista_componentes
        self.cantidad_componentes = len(lista_componentes)

        self.posición_componente_actual = 0

        self.componente_actual = lista_componentes[0]

        self.asa = ÁrbolSintáxisAbstracta()

    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """

        if self.asa.raiz is None:
            print([])
        else:
            self.asa.imprimir_preorden()

    def analizar(self):
        """
        Método principal que inicia el análisis siguiendo el esquema de
        análisis por descenso recursivo
        """
        try:
            self.asa.raiz = self.__analizar_programa()
            return True
        except SyntaxError as e:
            print(e)

    def __analizar_programa(self):
        """
        Programa ::= (Comentario|Asignación| Funcion)*[( )\n]*Inicio
        """
        nodos_nuevos = []
        # Al final debe de haber una funcion principal
        if self.componente_actual.texto == 'inicio':
            nodos_nuevos += [self.__analizar_inicio()]
        else:
            raise self.__obtener_error_completo(f'Se esperaba "inicio" para la funcion principal y se obtuvo',
                                                "Error Sintáctico")

        # pueden venir múltiples asignaciones o funciones
        while True:
            # Si es asignación
            if self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
                nodos_nuevos += [self.__analizar_instrucción()]

            # Si es función
            elif self.componente_actual.texto == 'indefinir':
                nodos_nuevos += [self.__analizar_función()]

            else:
                if self.posición_componente_actual+1 < self.cantidad_componentes:
                    raise self.__obtener_error_completo(f'Se esperaba una función o una asignación y se obtuvo',
                                                "Error Sintáctico")
                break
        return NodoÁrbol(TipoNodo.PROGRAMA, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_asignación(self):
        """
        Asignación ::= Identificador != (Expresión|Llamada)
        """
        # El identificador en esta posición es obligatorio
        nodos_nuevos = []

        nodos_nuevos += [self.__verificar_identificador()]

        # Igual el !=
        self.__verificar('!=')

        # Hay que arreglar las expresiones asi que dejo la lista vacia hasta que veamos como lo arreglamos
        if self.componente_actual.tipo in [TipoComponente.PUNTUACION, TipoComponente.ENTERO, TipoComponente.FLOTANTE,
                                           TipoComponente.TEXTO, TipoComponente.IDENTIFICADOR]:
            nodos_nuevos += [self.__analizar_expresión()]

        elif self.componente_actual.texto == 'colgar':
            nodos_nuevos += [self.__analizar_llamada()]

        else:
            raise self.__obtener_error_completo(
                f'Se esperaba un numero, texto, variable o una llamada a funcion y se obtuvo', "Error Sintáctico")
        return NodoÁrbol(TipoNodo.ASIGNACIÓN, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_operación(self):
        """
        Operación ::= Operación ::= (Valor[ \n]*Operador [ \n]*Valor)
        """

        # Acá no hay nada que hacer todas son obligatorias en esas
        # posiciones
        nodos_nuevos = []

        self.__verificar('(')
        nodos_nuevos += [self.__analizar_valor()]
        nodos_nuevos += [self.__verificar_operador()]
        nodos_nuevos += [self.__analizar_valor()]
        self.__verificar(')')

        return NodoÁrbol(TipoNodo.OPERACIÓN, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_función(self):
        """
        Gramatica Original: (BloqueInstrucciones)indefinir( )+(Identificador)( )*(Parametros)
        Ya que invertimos el orden de los componentes se leera
        Función ::=  indefinir Identificador (Parámetros) { BloqueInstrucciones* (quedarse Expresion)? }
        """
        nodos_nuevos = []
        # Esta sección es obligatoria en este orden
        self.__verificar('indefinir')

        nodos_nuevos += [self.__verificar_identificador()]
        nombre_funcion = nodos_nuevos[0].contenido
        self.__verificar('(')
        # Revisamos si hay parametros por verificar
        if self.componente_actual.tipo is TipoComponente.IDENTIFICADOR:
            nodos_nuevos += [self.__analizar_parámetros()]
        self.__verificar(')')
        self.__verificar('{')
        nodos_nuevos += [self.__analizar_bloque_instrucciones()]
        self.__verificar('}')

        return NodoÁrbol(TipoNodo.FUNCIÓN,contenido=nombre_funcion, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_llamada(self):
        """
        Llamada ::= colgar Identificador((Literal|Identificador)?(,(Literal|Identificador)*)?)
        """
        # Definimos los tipos aceptados para los parametros de la llamada en una lista para asi no tener ifs enormes
        nodos_nuevos = []
        aceptados = [TipoComponente.IDENTIFICADOR, TipoComponente.ENTERO, TipoComponente.FLOTANTE, TipoComponente.TEXTO]
        self.__verificar('colgar')
        nodos_nuevos += [self.__verificar_identificador()]
        self.__verificar('(')
        # Reviso que exista un parametro que verificar
        if self.componente_actual.tipo in aceptados:
            # Verifico los parametros
            nodos_nuevos += [self.__analizar_parámetros_llamada()]
        self.__verificar(')')

        return NodoÁrbol(TipoNodo.LLAMADA, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_parámetros(self):
        """
        Parámetros ::= (( )*Identificador( )*(,Identificador)*( )*)?
        """
        nodos_nuevos = []

        # Puede o no puede haber parámetros
        if self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:

            # Verifico el identificador
            nodos_nuevos += [self.__verificar_identificador()]

            # y luego verifico si hay más identificadores
            while self.componente_actual.texto == ',':
                self.__verificar(',')
                if self.componente_actual.tipo is TipoComponente.IDENTIFICADOR:
                    nodos_nuevos += [self.__verificar_identificador()]
                else:
                    raise self.__obtener_error_completo(f'Parámetro no válido se obtuvo', "Error Sintáctico")
        else:
            raise self.__obtener_error_completo(f'Parámetro no válido se obtuvo', "Error Sintáctico")
        return NodoÁrbol(TipoNodo.PARÁMETROS, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_parámetros_llamada(self):

        nodos_nuevos = []

        nodos_nuevos += [self.__analizar_valor()]

        # y luego verifico si hay más parametros por sus tipos
        while self.componente_actual.texto == ',':
            self.__verificar(',')
            try:
                nodos_nuevos += [self.__analizar_valor()]
            except SyntaxError:
                raise self.__obtener_error_completo(f'Parámetro de invocación no válido', "Error Sintáctico")
        return NodoÁrbol(TipoNodo.PARAMETROSLLAMADA, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_instrucción(self):
        """
        Instrucción ::= (Asignación|Llamada|Retorno|Repetición|Condicional);
        """

        if self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
            nodo = self.__analizar_asignación()

        elif self.componente_actual.texto == 'colgar':
            nodo = self.__analizar_llamada()

        elif self.componente_actual.texto == 'quedarse':
            nodo = self.__analizar_retorno()

        elif self.componente_actual.texto == 'romper':
            nodo = self.__analizar_repetición()

        elif self.componente_actual.texto == 'sino':
            nodo = self.__analizar_condicional()

        else:
            raise self.__obtener_error_completo(
                f'Se esperaba uno de los siguientes: variable, "colgar", "quedarse", "romper" o "sino" y se obtuvo',
                "Error Sintáctico")
        self.__verificar(';')

        return nodo

    def __analizar_repetición(self):
        """
        Original
        Repetición ::=  }( )*(\n)+BloqueInstrucciones( )*(\n)+romper( )*(ExpresionCondicional)( )*{

        Ya que invertimos el orden de los componentes se leerá
        Condicional ::= romper(ExpresionCondicional){BloqueInstrucciones}
        """

        nodos_nuevos = []
        # Todos presentes en ese orden... sin opciones
        self.__verificar('romper')
        self.__verificar('(')
        nodos_nuevos += [self.__analizar_expresión_condicional()]
        self.__verificar(')')
        self.__verificar('{')
        nodos_nuevos += [self.__analizar_bloque_instrucciones()]
        self.__verificar('}')
        return NodoÁrbol(TipoNodo.REPETICIÓN, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_condicional(self):
        """
            Ya que invertimos el orden de los componentes se leerá
            Condicional ::= sino(ExpresionCondicional){BloqueInstrucciones*} (ademas{BloqueInstrucciones*})?
            """
        nodos_nuevos = []
        self.__verificar('sino')
        self.__verificar('(')
        nodos_nuevos += [self.__analizar_expresión_condicional()]
        self.__verificar(')')
        self.__verificar('{')
        nodos_nuevos += [self.__analizar_bloque_instrucciones()]
        self.__verificar('}')

        # el ademas es opcional

        if self.componente_actual.texto == 'ademas':
            self.__verificar('ademas')
            self.__verificar('{')
            nodos_nuevos += [self.__analizar_bloque_instrucciones()]
            # Nota: de querer mas claridad en el arbol editar el EBNF para diferenciar sino y ademas como otros objetos
            # y por ende distintas funciones que agregan nodos de diferentes tipos
            self.__verificar('}')

        return NodoÁrbol(TipoNodo.CONDICIONAL, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_expresión_condicional(self):

        """
        ExpresiónCondicional ::= Comparación( )*((y)|(o))( )*Comparación)?
        """
        nodos_nuevos = []

        # La primera sección obligatoria la comparación
        nodos_nuevos += [self.__analizar_comparación()]

        while self.componente_actual.tipo == TipoComponente.PALABRA_CLAVE:
            # Verifica que este el y o el o
            nodos_nuevos += [self.__analizar_operador_lógico()]
            # verifica que exista otra comparación
            nodos_nuevos += [self.__analizar_comparación()]

        return NodoÁrbol(TipoNodo.EXPRESIÓNCONDICIONAL, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_operador_lógico(self):
        """
        OperadorLógico ::== y | o
        """

        if self.componente_actual.texto == 'y':
            componente = self.__verificar('y')
            nodo = NodoÁrbol(TipoNodo.OPERADORLÓGICO, contenido=componente.texto,
                                    atributos=self.componente_actual.atributos)

        elif self.componente_actual.texto == 'o':
            componente = self.__verificar('o')
            nodo = NodoÁrbol(TipoNodo.OPERADORLÓGICO, contenido=componente.texto,
                                    atributos=self.componente_actual.atributos)
        else:
            raise self.__obtener_error_completo(f'Se necesita un "y" o un "o" y se obtuvo un', "Error Sintáctico")

        return nodo

    def __analizar_comparación(self):
        """
        Comparación ::= Valor comparador Valor
        """
        nuevos_nodos = []
        nuevos_nodos += [self.__analizar_valor()]
        nuevos_nodos += [self.__verificar_comparador()]
        nuevos_nodos += [self.__analizar_valor()]

        return NodoÁrbol(TipoNodo.COMPARACIÓN, nodos=nuevos_nodos, atributos=self.componente_actual.atributos)

    def __analizar_valor(self):
        """
        Valor ::= Literal | Identificador
        """
        if self.componente_actual.tipo is TipoComponente.ENTERO \
                or self.componente_actual.tipo is TipoComponente.FLOTANTE \
                or self.componente_actual.tipo is TipoComponente.TEXTO:
            nodo = self.__analizar_literal()
        else:
            nodo = self.__verificar_identificador()
        return nodo

    def __analizar_retorno(self):
        """
        Retorno ::= quedarse( )+Expresion
        """
        # así estaba antes: comienza
        # self.__verificar('quedarse')
        # Verificar si este manejo esta bien para errores
        # self.__analizar_expresión()
        # termina
        nodos_nuevos = []

        self.__verificar('quedarse')

        nodos_nuevos += [self.__analizar_expresión()]

        return NodoÁrbol(TipoNodo.RETORNO, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_expresión(self):
        """
        Expresión ::=  Operación|Literal|Identificador
        """
        # Necesita arreglo hay ambiguedad y no se sabe donde entrar
        if self.componente_actual.texto == '(':
            nodo = self.__analizar_operación()

        elif self.componente_actual.tipo in [TipoComponente.ENTERO, TipoComponente.FLOTANTE, TipoComponente.TEXTO]:
            nodo = self.__analizar_literal()

        elif self.componente_actual.tipo is TipoComponente.IDENTIFICADOR:
            nodo = self.__verificar_identificador()

        elif self.componente_actual.texto == 'colgar':
            nodo = self.__analizar_llamada()
        else:
            raise self.__obtener_error_completo(f'Se esperaba un numero, texto, variable o "(" y se obtuvo',
                                                "Error Sintáctico")
        return nodo

    def __analizar_inicio(self):
        """
        Gramatica original:
            Inicio ::= fin(BloqueInstrucciones)inicio
        Gramatica que interpreta el compilador:
            Inicio ::= inicio(BloqueInstrucciones)fin
        """
        nodos_nuevos = []

        self.__verificar('inicio')

        nodos_nuevos += [self.__analizar_bloque_instrucciones()]

        self.__verificar('fin')

        return NodoÁrbol(TipoNodo.INICIO, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __analizar_literal(self):
        """
        Literal ::= (Número|Texto)
        """

        if self.componente_actual.tipo is TipoComponente.TEXTO:
            nodo = self.__verificar_texto()

        elif self.componente_actual.tipo in [TipoComponente.ENTERO, TipoComponente.FLOTANTE]:

            nodo = self.__analizar_número()
        else:
            raise self.__obtener_error_completo(f'Se esperaba un Numero o un Texto y se obtuvo', "Error Sintáctico")

        return nodo

    def __analizar_número(self):
        """
        Número ::= Entero|Flotante

        Analiza y verifica si el tipo de componente actual es ENTERO o FLOTANTE
        """

        if self.componente_actual.tipo == TipoComponente.ENTERO:
            nodo = self.__verificar_entero()
        else:
            nodo = self.__verificar_flotante()
        return nodo

    def __analizar_bloque_instrucciones(self):
        """
        BloqueInstrucciones ::= ( )*(\n)+(Instruccion|Comentario)*( )*(\n)+
        """
        aceptados = ['colgar', 'quedarse', 'romper', 'sino']
        nodos_nuevos = []
        while self.componente_actual.tipo is TipoComponente.IDENTIFICADOR or self.componente_actual.texto in aceptados:
            nodos_nuevos += [self.__analizar_instrucción()]
        return NodoÁrbol(TipoNodo.BLOQUEINSTRUCCIONES, nodos=nodos_nuevos, atributos=self.componente_actual.atributos)

    def __verificar_operador(self):
        """
        Operador ::= [-+/*]
        """
        componente = self.__verificar_tipo_componente(TipoComponente.OPERADOR)
        return NodoÁrbol(TipoNodo.OPERADOR, contenido=componente.texto, atributos=self.componente_actual.atributos)

    def __verificar_comparador(self):
        """
        Verifica si el tipo del componente léxico actual es de tipo COMPARADOR

        Comparador ::= (!==)|(==)|>|<|(<=)|(>=)
        """
        componente = self.__verificar_tipo_componente(TipoComponente.COMPARADOR)
        return NodoÁrbol(TipoNodo.COMPARADOR, contenido=componente.texto, atributos=self.componente_actual.atributos)

    def __verificar_texto(self):
        """
        Verifica si el tipo del componente léxico actual es de tipo TEXTO

        Texto ::= "[a-zA-Z( )0-9]*"
        """
        componente = self.__verificar_tipo_componente(TipoComponente.TEXTO)
        return NodoÁrbol(TipoNodo.TEXTO, contenido=componente.texto, atributos=self.componente_actual.atributos)

    def __verificar_entero(self):
        """
        Verifica si el tipo del componente léxico actuales de tipo ENTERO

        Entero ::= (+)?[0-9]+
        """
        componente = self.__verificar_tipo_componente(TipoComponente.ENTERO)
        return NodoÁrbol(TipoNodo.ENTERO, contenido=componente.texto, atributos=self.componente_actual.atributos)

    def __verificar_flotante(self):
        """
        Verifica si el tipo del componente léxico actuales de tipo FLOTANTE
        Flotante ::= (+)?[0-9]+.[0-9]+
        """
        componente = self.__verificar_tipo_componente(TipoComponente.FLOTANTE)
        return NodoÁrbol(TipoNodo.FLOTANTE, contenido=componente.texto, atributos=self.componente_actual.atributos)

    def __verificar_identificador(self):
        """
        Verifica si el tipo del componente léxico actuales de tipo
        IDENTIFICADOR

        Identificador ::= [a-z][a-zA-Z]*
        """
        componente = self.__verificar_tipo_componente(TipoComponente.IDENTIFICADOR)
        return NodoÁrbol(TipoNodo.IDENTIFICADOR, contenido=componente.texto, atributos=self.componente_actual.atributos)

    def __verificar(self, texto_esperado):

        """
        Verifica si el texto del componente léxico actual corresponde con
        el esperado cómo argumento
        """

        if self.componente_actual.texto != texto_esperado:
            raise self.__obtener_error_completo(f'Se esperaba "{texto_esperado}" y se obtuvo', "Error Sintáctico")
        return self.__pasar_siguiente_componente()

    def __obtener_error_completo(self, mensaje, tipo_excepcion):
        return SyntaxError(
            f'{tipo_excepcion}: {mensaje}: "{self.componente_actual.texto}".\
              Linea:{self.componente_actual.atributos["Fila"]} Columna: {self.componente_actual.atributos["Columna"]}')

    def __verificar_tipo_componente(self, tipo_esperado):

        if self.componente_actual.tipo is not tipo_esperado:
            raise self.__obtener_error_completo(
                f'Se esperaba un {tipo_esperado.name} y se obtuvo {self.componente_actual.tipo.name} con el texto',
                "Error Sintáctico")

        return self.__pasar_siguiente_componente()

    def __pasar_siguiente_componente(self):
        """
        Pasa al siguiente componente léxico

        Esto revienta por ahora
        """
        self.posición_componente_actual += 1

        if self.posición_componente_actual >= self.cantidad_componentes:
            return

        self.componente_actual = \
            self.componentes_léxicos[self.posición_componente_actual]

        return self.componentes_léxicos[self.posición_componente_actual - 1]

    def __componente_venidero(self, avance=1):
        """
        Retorna el componente léxico que está 'avance' posiciones más
        adelante... por default el siguiente. Esto sin adelantar el
        contador del componente actual.
        """
        return self.componentes_léxicos[self.posición_componente_actual + avance]
