# Implementa el veficador de reverse

from utils.árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
# from árbol import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
from utils.tipo_datos import TipoDatos
# from tipo_datos import TipoDatos


class TablaSimbolos:
    """ 
    Almacena información auxiliar para decorar el árbol de sintáxis
    abstracta con información de tipo y alcance.

    La estructura de simbolos es una lista de diccionarios 
    """

    def __init__(self):  # revisar que esto funque
        pass

    simbolos: list[dict] = []
    profundidad: int = 0

    def abrir_bloque(self):
        """
        Inicia un bloque de alcance (scope)
        """
        self.profundidad += 1

    def cerrar_bloque(self):
        """
        Termina un bloque de alcance y al acerlo elimina todos los
        registros de la tabla que estan en ese bloque
        """

        for registro in self.simbolos:
            if registro['profundidad'] == self.profundidad:
                self.simbolos.remove(registro)

        self.profundidad -= 1

    def nuevo_registro(self, nodo, nombre_registro=''):
        """
        Introduce un nuevo registro a la tabla de simbolos
        """
        # El nombre del identificador + el nivel de profundidad 

        """
        Los atributos son: nombre, profundidad, referencia

        referencia es una referencia al nodo dentro del árbol
        (Técnicamente todo lo 'modificable (mutable)' en python es una
        referencia siempre y cuando use la POO... meh... más o menos.
        """

        diccionario = {'nombre': nodo.contenido, 'profundidad': self.profundidad, 'referencia': nodo}

        self.simbolos.append(diccionario)

    def verificar_existencia(self, nombre):
        """
        Verficia si un identificador existe cómo variable/función global o local
        """
        for registro in self.simbolos:

            # si es local
            if registro['nombre'] == nombre and \
                    registro['profundidad'] <= self.profundidad:
                return registro

        raise Exception(f'El identificador "{nombre}" no existe')

    def __str__(self):

        resultado = 'TABLA DE simbolos\n\n'
        resultado += 'Profundidad: ' + str(self.profundidad) + '\n\n'
        for registro in self.simbolos:
            resultado += str(registro) + '\n'

        return resultado


class Visitante:
    tabla_simbolos: TablaSimbolos

    def __init__(self, nueva_tabla_simbolos):
        self.tabla_simbolos = nueva_tabla_simbolos

    def visitar(self, nodo: NodoÁrbol):
        """
        Este método es necesario por que uso un solo tipo de nodo para
        todas las partes del árbol por facilidad... pero cómo lo hice
        tuanis allá... pues bueno... acá hay que pagar el costo.
        """

        if nodo.tipo is TipoNodo.PROGRAMA:
            self.__visitar_programa(nodo)

        elif nodo.tipo is TipoNodo.FUNCIÓN:
            self.__visitar_función(nodo)

        elif nodo.tipo is TipoNodo.INICIO:
            self.__visitar_inicio(nodo)

        elif nodo.tipo is TipoNodo.INSTRUCCIÓN:
            self.__visitar_instrucción(nodo)

        elif nodo.tipo is TipoNodo.ASIGNACIÓN:
            self.__visitar_asignación(nodo)

        elif nodo.tipo is TipoNodo.LLAMADA:
            self.__visitar_llamada(nodo)

        elif nodo.tipo is TipoNodo.IDENTIFICADOR:
            self.__visitar_identificador(nodo)

        elif nodo.tipo is TipoNodo.EXPRESIÓN:
            self.__visitar_expresión(nodo)

        elif nodo.tipo is TipoNodo.LITERAL:
            self.__visitar_literal(nodo)

        elif nodo.tipo is TipoNodo.NÚMERO:
            self.__visitar_número(nodo)

        elif nodo.tipo is TipoNodo.ENTERO:
            self.__visitar_entero(nodo)

        elif nodo.tipo is TipoNodo.FLOTANTE:
            self.__visitar_flotante(nodo)

        elif nodo.tipo is TipoNodo.TEXTO:
            self.__visitar_texto(nodo)

        elif nodo.tipo is TipoNodo.OPERACIÓN:
            self.__visitar_operación(nodo)

        elif nodo.tipo is TipoNodo.OPERADOR:
            self.__visitar_operador(nodo)

        elif nodo.tipo is TipoNodo.PARÁMETROS:
            self.__visitar_parámetros(nodo)

        elif nodo.tipo is TipoNodo.CONDICIONAL:
            self.__visitar_condicional(nodo)

        elif nodo.tipo is TipoNodo.EXPRESIÓNCONDICIONAL:
            self.__visitar_expresión_condicional(nodo)

        elif nodo.tipo is TipoNodo.COMPARACIÓN:
            self.__visitar_comparación(nodo)

        elif nodo.tipo is TipoNodo.COMPARADOR:
            self.__visitar_comparador(nodo)

        elif nodo.tipo is TipoNodo.REPETICIÓN:
            self.__visitar_repetición(nodo)

        elif nodo.tipo is TipoNodo.RETORNO:
            self.__visitar_retorno(nodo)

        elif nodo.tipo is TipoNodo.BLOQUEINSTRUCCIONES:
            self.__visitar_bloque_instrucciones(nodo)

        elif nodo.tipo is TipoNodo.PARAMETROSLLAMADA:
            self.__visitar_parámetros_llamada(nodo)

        elif nodo.tipo is TipoNodo.VALOR:
            self.__visitar_valor(nodo)

        elif nodo.tipo is TipoNodo.OPERADORLÓGICO:
            self.__visitar_operador_lógico(nodo)

        else:
            raise Exception('InternalError: Error Interno')

    # CHECK
    def __visitar_programa(self, nodo_actual):
        """
        Programa ::= (Comentario|Asignación|Funcion)*[( )\n]*Inicio
        """
        inicio = nodo_actual.nodos[0]
        for nodo in nodo_actual.nodos:
            if nodo.tipo is TipoNodo.INICIO:
                continue
            nodo.visitar(self)
        inicio.visitar(self)

    # CHECK
    def __visitar_asignación(self, nodo_actual):
        """
        Asignación ::= Identificador != (Expresión|Llamada)
        """
        # Metó la información en la tabla de simbolos (IDENTIFICACIÓN)
        self.tabla_simbolos.nuevo_registro(nodo_actual.nodos[0])

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # Si es una función verifico el tipo que retorna para incluirlo en
        # la asignación y si es un literal puedo anotar el tipo (TIPO) 

        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

        nodo_actual.nodos[0].atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

    # CHECK
    def __visitar_operación(self, nodo_actual):
        """
        Operación ::= (Valor Operador Valor)
        """
        # Si los 'Valor' son identificadores se asegura que existan (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_simbolos.verificar_existencia(nodo.contenido)
            nodo.visitar(self)

        # Verifico que los tipos coincidan (TIPO)
        valor_izq = nodo_actual.nodos[0]
        operador = nodo_actual.nodos[1]
        valor_der = nodo_actual.nodos[2]

        """ Posibles Operaciones
        Entero Operador Entero
        Flotante Operador Flotante
        Texto Operador Texto
        Flotante Operador Entero <-> Entero Operador Flotante
        """

        # Si alguno de los 2 valores, ya sea el izquierdo o derecho, son de tipo texto y el operador es +
        if operador.contenido == '-' and (
                valor_izq.atributos['tipo'] == TipoDatos.TEXTO or valor_der.atributos['tipo'] == TipoDatos.TEXTO):

            # Convierto el comparador a tipo texto
            operador.atributos['tipo'] = TipoDatos.TEXTO

            # Convierto el nodo a tipo texto
            nodo_actual.atributos['tipo'] = TipoDatos.TEXTO

        elif valor_izq.atributos['tipo'] == valor_der.atributos['tipo'] and valor_izq.atributos['tipo'] != TipoDatos.TEXTO:

            operador.atributos['tipo'] = valor_izq.atributos['tipo']

            nodo_actual.atributos['tipo'] = valor_izq.atributos['tipo']

        # Cuando se opera un entero o flotante el tipo sera flotante
        elif (valor_izq.atributos['tipo'] == TipoDatos.ENTERO and
              valor_der.atributos['tipo'] == TipoDatos.FLOTANTE) or \
                (valor_izq.atributos['tipo'] == TipoDatos.FLOTANTE and
                 valor_der.atributos['tipo'] == TipoDatos.ENTERO):

            operador.atributos['tipo'] = TipoDatos.FLOTANTE

            nodo_actual.atributos['tipo'] = TipoDatos.FLOTANTE

        # Cuando no se que tipo es ya que es parametro de funcion
        elif valor_izq.atributos['tipo'] == TipoDatos.CUALQUIERA or \
                valor_der.atributos['tipo'] == TipoDatos.CUALQUIERA:

            operador.atributos['tipo'] = TipoDatos.CUALQUIERA

            nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA

        else:
            raise Exception(
                f'TypeError: No se puede hacer una operacion "{operador.contenido}" entre un'
                f' {valor_izq.atributos["tipo"].name} y un {valor_der.atributos["tipo"].name}')

    # CHECK
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

        # Meto la función en la tabla de simbolos (IDENTIFICACIÓN)
        self.tabla_simbolos.nuevo_registro(nodo_actual)

        self.tabla_simbolos.abrir_bloque()

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        self.tabla_simbolos.cerrar_bloque()

        # Anoto el tipo de retorno (TIPO)
        # Pueden o no haber parametros por lo que se verifica primero
        index = 1
        if nodo_actual.nodos[1].tipo == TipoNodo.PARÁMETROS:
            index = 2
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[index].atributos['tipo']

    # CHECK
    def __visitar_llamada(self, nodo_actual):
        """
        Llamada ::= colgar Identificador(ParametrosLlamada)
        """
        # Verfica que el 'Identificador' exista (IDENTIFICACIÓN) y que sea
        registro = self.tabla_simbolos.verificar_existencia(nodo_actual.nodos[0].contenido)
        # Esto porque el identificador de la función no puede estar definida como una variable
        if registro['referencia'].tipo != TipoNodo.FUNCIÓN:
            raise Exception('No se puede llamar el objeto...', registro)

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
        # El tipo resultado de la invocación es el tipo inferido de una
        # función previamente definida
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA
        # Se aplica un parche temporal esto estaba antes en la asignacion registro['referencia'].atributos['tipo']

    # CHECK
    def __visitar_parámetros_llamada(self, nodo_actual):
        """
        ParametrosLlamada ::== (Valor(,Valor)*)?
        """
        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                self.tabla_simbolos.verificar_existencia(nodo.contenido)
            nodo.visitar(self)

    # CHECK
    def __visitar_parámetros(self, nodo_actual):
        """
        Parámetros ::= (Identificador(,Identificador)*)?
        """

        # Registro cada 'Identificador' en la tabla
        for nodo in nodo_actual.nodos:
            self.tabla_simbolos.nuevo_registro(nodo)
            nodo.visitar(self)

    # CHECK
    def __visitar_instrucción(self, nodo_actual):
        """
        Instrucción ::= (Asignación|Llamada|Retorno|Repetición|Condicional);
        """
        nodo_actual.nodos[0].visitar(self)

    # CHECK
    def __visitar_repetición(self, nodo_actual):
        """
        Original
        Repetición ::=  }( )*(\n)+BloqueInstrucciones( )*(\n)+romper( )*(ExpresionCondicional)( )*{

        Ya que invertimos el orden de los componentes se leerá
        Condicional ::= romper(ExpresionCondicional){BloqueInstrucciones}
        """
        # Se abre bloque de variables locales
        self.tabla_simbolos.abrir_bloque()

        # Visita la condición y el bloque de instrucciones
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        self.tabla_simbolos.cerrar_bloque()
        # Se cierra el bloque

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

    # CHECK
    def __visitar_condicional(self, nodo_actual):
        """
        Ya que invertimos el orden de los componentes se leerá
        Condicional ::= sino(ExpresionCondicional){BloqueInstrucciones*} (ademas{BloqueInstrucciones*})?
        """
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA

    # CHECK
    def __visitar_expresión_condicional(self, nodo_actual):
        """
        ExpresiónCondicional ::= Comparación( )*((y)|(o))( )*Comparación)?
        """
        self.tabla_simbolos.abrir_bloque()
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
        self.tabla_simbolos.cerrar_bloque()
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[0].atributos['tipo']

    # CHECK
    def __visitar_operador_lógico(self, nodo_actual):
        """
        OperadorLógico ::== y | o
        """
        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO

    # CHECK
    def __visitar_comparación(self, nodo_actual):
        """
        Comparación ::= Valor Comparador Valor
        """

        # Si los 'Valor' son identificadores se asegura que existan (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_simbolos.verificar_existencia(nodo.contenido)

            nodo.visitar(self)

        # Verifico que los tipos coincidan (TIPO)
        valor_izq = nodo_actual.nodos[0]
        comparador = nodo_actual.nodos[1]
        valor_der = nodo_actual.nodos[2]

        """
        Posibles comparaciones

        Texto Comparador Texto
        Entero Comparador Entero
        Flotante Comparador Flotante
        Texto Comparador Entero <-> Entero Comparador Texto 
        Entero Comparador Flotante <-> Flotante Comparador Entero
        """

        # Cuando los dos valores coinciden en tipo el valor del comparador sera el mismo
        if valor_izq.atributos['tipo'] == valor_der.atributos['tipo']:

            comparador.atributos['tipo'] = valor_izq.atributos['tipo']

        # Cuando se compara un entero o flotante el tipo sera flotante
        elif (valor_izq.atributos['tipo'] == TipoDatos.ENTERO and
              valor_der.atributos['tipo'] == TipoDatos.FLOTANTE) or \
                (valor_izq.atributos['tipo'] == TipoDatos.FLOTANTE and
                 valor_der.atributos['tipo'] == TipoDatos.ENTERO):

            comparador.atributos['tipo'] = TipoDatos.FLOTANTE

        # Cuando se compara un texto con cualquier otro tipo el tipo sera texto
        # Decidimos que aceptara comparacion de Texto y Numero y esto se hara
        # reemplazando el texto por len(texto) en la generacion de codigo
        elif (valor_izq.atributos['tipo'] == TipoDatos.TEXTO and
              valor_der.atributos['tipo'] != TipoDatos.NINGUNO) or \
                (valor_izq.atributos['tipo'] != TipoDatos.NINGUNO and
                 valor_der.atributos['tipo'] == TipoDatos.TEXTO):

            comparador.atributos['tipo'] = TipoDatos.TEXTO

        # Cuando no se que tipo es ya que es parametro de funcion
        elif valor_izq.atributos['tipo'] == TipoDatos.CUALQUIERA or \
                valor_der.atributos['tipo'] == TipoDatos.CUALQUIERA:
            comparador.atributos['tipo'] = TipoDatos.CUALQUIERA
        # Si no coincide en los casos anteriores hay un error de tipo
        else:
            raise Exception(
                f'TypeError: No se puede comparar un '
                f'{valor_izq.atributos["tipo"].name} y un {valor_der.atributos["tipo"].name}')

        # El tipo de la comparacion siempre debe ser VALOR_VERDAD aunque internamente no permitimos estos valores
        nodo_actual.atributos['tipo'] = TipoDatos.VALOR_VERDAD

    # CHECK
    def __visitar_valor(self, nodo_actual):
        """
        Valor ::= Literal|Identificador
        """
        # En realidad núnca se va a visitar por que lo saqué del árbol
        # duránte la etapa de análisis

    # CHECK
    def __visitar_retorno(self, nodo_actual):
        """
        Retorno ::= quedarse( )+Expresion
        """
        nodo = nodo_actual.nodos[0]
        nodo.visitar(self)
        if nodo.tipo == TipoNodo.IDENTIFICADOR:
            # Se verifica el identificador fue declarado
            registro = self.tabla_simbolos.verificar_existencia(nodo.contenido)
            # se le asigna el tipo de retorno
            nodo_actual.atributos['tipo'] = registro['referencia'].atributos['tipo']
        else:
            # se le asigna el tipo de retorno
            nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA
            # Esto es un parche que se pone antes estaba "nodo.atributos['tipo']"

    # CHECK
    def __visitar_inicio(self, nodo_actual):
        """
        Inicio ::= fin(BloqueInstrucciones)inicio
        """
        # Este mae solo va a tener un bloque de instrucciones que tengo que
        # ir a visitar

        # Lo pongo así por copy/paste... pero puede ser como el comentario
        # de más abajo.
        # Queda más bonito de esta forma:
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
        # nodo_actual.nodos[0].visitar(self)

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[0].atributos['tipo']

    # CHECK
    def __visitar_literal(self, nodo_actual):
        """
        Literal ::= Número | Texto
        """
        # Nunca se llega aqui ya que analizar_literal devuelve un numero o texto como tipo de nodo

    # CHECK
    def __visitar_número(self, nodo_actual):
        """
        Número ::= Entero | Flotante
        """
        # Nunca se llega aqui ya que analizar_número devuelve un entero o flotante como tipo de nodo

    # CHECK
    def __visitar_bloque_instrucciones(self, nodo_actual):
        """
        BloqueInstrucciones ::= ( )*(\n)+(Instruccion|Comentario)*( )*(\n)+
        """
        # Visita todas las instrucciones que contiene
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
        # Acá yo debería agarrar el tipo de datos del Retorno si lo hay
        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO

        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.RETORNO:
                nodo_actual.atributos['tipo'] = nodo.atributos['tipo']

    # CHECK
    def __visitar_operador(self, nodo_actual):
        """
        Operador ::= [-+/*]
        """
        # Operador para trabajar con números (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    # CHECK
    def __visitar_comparador(self, nodo_actual):
        """
        Comparador ::= (!==)|(==)|>|<|(<=)|(>=)
        """
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA

    # CHECK
    def __visitar_texto(self, nodo_actual):
        """
        Texto ::= "[a-zA-Z( )0-9]*"
        """
        # Texto (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.TEXTO

    # CHECK
    def __visitar_entero(self, nodo_actual):
        """
        Entero ::= (+)?[0-9]+
        """
        # Entero (TIPO) 
        nodo_actual.atributos['tipo'] = TipoDatos.ENTERO

    # CHECK
    def __visitar_flotante(self, nodo_actual):
        """
        Flotante ::= (+)?[0-9]+.[0-9]+
        """
        # Flotante (TIPO) 
        nodo_actual.atributos['tipo'] = TipoDatos.FLOTANTE

    # CHECK
    def __visitar_identificador(self, nodo_actual):
        """
        Identificador ::= [a-z][a-zA-Z]*
        """
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA


class Verificador:
    asa: ÁrbolSintáxisAbstracta
    visitador: Visitante
    tabla_simbolos: TablaSimbolos

    def __init__(self, nuevo_asa: ÁrbolSintáxisAbstracta):

        self.asa = nuevo_asa

        self.tabla_simbolos = TablaSimbolos()
        self.__cargar_ambiente_estándar()

        self.visitador = Visitante(self.tabla_simbolos)

    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """

        if self.asa.raiz is None:
            print([])
        else:
            self.asa.imprimir_preorden()

    def __cargar_ambiente_estándar(self):

        funciones_estandar = [ ('ocultar', TipoDatos.TEXTO),
                ('numero_seguro', TipoDatos.ENTERO)]

        for nombre, tipo in funciones_estandar:
            nodo = NodoÁrbol(TipoNodo.FUNCIÓN, contenido=nombre, atributos={'tipo': tipo})
            self.tabla_simbolos.nuevo_registro(nodo)

    def verificar(self):
        try:
            self.visitador.visitar(self.asa.raiz)
            return True
        except Exception as e:
            print(e)
