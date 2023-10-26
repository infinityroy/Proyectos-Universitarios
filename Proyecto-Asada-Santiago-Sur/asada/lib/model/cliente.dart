import 'dart:core';

class Cliente {
  List<DatoMedida> datosMedidas;
  int numeroMedidor;
  String nombre;

  void agregarDatosMedida(int fecha, int medida) {
    datosMedidas.add(DatoMedida(fecha, medida));
  }

  int getNumeroMedidor() {
    return numeroMedidor;
  }

  String getNombre() {
    return nombre;
  }

  DatoMedida getLastMedida() {
    return datosMedidas.last;
  }

  @override
  String toString() {
    String result = "Nombre: " +
        nombre +
        "\nNumero de medidor: " +
        numeroMedidor.toString();
    for (var medida in datosMedidas) {
      result += medida.toString();
    }
    return result;
  }

  Cliente(this.numeroMedidor, this.nombre, this.datosMedidas);
}

class DatoMedida {
  int fecha; //formato de la fecha YYYYMM
  int medida;

  DatoMedida(this.fecha, this.medida);

  int getFecha() {
    return fecha;
  }

  int getMedida() {
    return medida;
  }

  void setFecha(int nuevaFecha) {
    fecha = nuevaFecha;
  }

  void setMedida(int nuevaMedida) {
    medida = nuevaMedida;
  }

  @override
  String toString() {
    return "\n  Fecha: " +
        fecha.toString() +
        "\n  Medida: " +
        medida.toString();
  }
}
