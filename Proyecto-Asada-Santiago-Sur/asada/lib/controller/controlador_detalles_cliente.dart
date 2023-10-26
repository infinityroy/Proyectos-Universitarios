import 'package:asada/model/cliente.dart';
import 'package:asada/services/servicio_clientes.dart';

class ControladorDetallesCliente {
  final ServicioClientes _servicioClientes;

  ControladorDetallesCliente(this._servicioClientes);

  bool registrarNuevaMedida(Cliente c, DatoMedida m) {
    if (c.datosMedidas.last.fecha !=
        DateTime.now().year * 100 + DateTime.now().month) {
      c.datosMedidas.add(m);
      _servicioClientes.guardarCliente(c);
      return true;
    }
    return false;
  }

  bool eliminarMedida(Cliente c) {
    if (c.datosMedidas.last.fecha ==
        DateTime.now().year * 100 + DateTime.now().month) {
      c.datosMedidas.removeLast();
      _servicioClientes.guardarCliente(c);
      return true;
    }
    return false;
  }

  bool guardarCliente(Cliente c) {
    return _servicioClientes.guardarCliente(c);
  }
}
