import 'package:asada/model/cliente.dart';
import 'package:asada/model/cobro.dart';

abstract class ArchivoLocalDao {
  List<Cliente> getClientes();
  List<Cobro> getCobros(String fecha, bool primeraPasada);
  String getContenidoDelMes();
  bool crearArchivoClientes(String contenido);
  Future<bool> crearArchivoCobros(String contenido);
  bool actualizarArchivoClientes(String contenido);
  bool guardarCliente(Cliente c);
  bool agregarAbono(Cobro c, int monto, int fecha, int tipoPago);
  bool eliminarAbono(Cobro c, int index);
  bool archivoDelMesYaExiste(String tipo, String mes);
}
