class Cobro {
  List<DatoAbono> abonos;
  int numeroMedidor;
  int totalDeuda;
  int fecha;
  String nombreCliente;
  Cobro(this.nombreCliente, this.numeroMedidor, this.fecha, this.totalDeuda,
      this.abonos);

  void agregarDatoAbono(int fecha, int monto, int tipoPago) {
    abonos.add(DatoAbono(fecha, monto, tipoPago));
  }

  int getNumeroMedidor() {
    return numeroMedidor;
  }

  String getNombreCliente() {
    return nombreCliente;
  }

  List<DatoAbono> getAbonos() {
    return abonos;
  }

  int getFecha() {
    return fecha;
  }

  int obtenerDeudaActual() {
    int deuda = totalDeuda;
    for (DatoAbono abono in abonos) {
      deuda -= abono.getMonto();
    }
    return deuda;
  }
}

class DatoAbono {
  final int _fecha; // Formato: dd-MM-yyyy
  final int _monto;
  int tipoPago;

  DatoAbono(this._fecha, this._monto, this.tipoPago);

  int getFecha() {
    return _fecha;
  }

  int getMonto() {
    return _monto;
  }

  int getTipoPago() {
    return tipoPago;
  }

  @override
  String toString() {
    return "  Fecha: " +
        _fecha.toString() +
        "\n  Monto: " +
        _monto.toString() +
        "\n";
  }
}
