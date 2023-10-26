import 'package:asada/model/cliente.dart';

abstract class ServicioClientes {
  Future<List<Cliente>> generarListaDeClientes();
  Future<List<Cliente>> actualizarListaDeClientes();
  bool guardarCliente(Cliente c);
  void subirDatos();
}
