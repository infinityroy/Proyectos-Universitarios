import 'package:asada/model/cliente.dart';
import 'package:asada/services/servicio_clientes.dart';

class ControladorFontanero {
  final ServicioClientes _servicioClientes;

  ControladorFontanero(this._servicioClientes);

  Future<List<Cliente>> generarListaC() async {
    return await _servicioClientes.generarListaDeClientes();
  }

  void subirDatos() {
    return _servicioClientes.subirDatos();
  }
}
