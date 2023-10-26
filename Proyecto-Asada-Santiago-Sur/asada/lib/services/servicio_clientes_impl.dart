import 'package:asada/services/servicio_clientes.dart';
import 'package:asada/model/cliente.dart';
import 'package:asada/dao/web_service_dao.dart';
import 'package:asada/dao/archivo_local_dao.dart';
import 'package:intl/intl.dart';

class ServicioClientesImpl implements ServicioClientes {
  final WebServiceDao webDao;
  final ArchivoLocalDao filedao;

  ServicioClientesImpl(this.webDao, this.filedao);

  @override
  Future<List<Cliente>> actualizarListaDeClientes() async {
    String contenido = await webDao.getContenidoSolicitudClientes();
    filedao.actualizarArchivoClientes(contenido);
    return filedao.getClientes();
  }

  @override
  Future<List<Cliente>> generarListaDeClientes() async {
    if (filedao.archivoDelMesYaExiste(
        "Cliente",
        DateFormat('yyyy-MM').format(DateTime.now()))) {
      return filedao.getClientes();
    }
    String contenido = await webDao.getContenidoSolicitudClientes();
    filedao.crearArchivoClientes(contenido);
    return filedao.getClientes();
  }

  @override
  bool guardarCliente(Cliente c) {
    return filedao.guardarCliente(c);
  }

  @override
  void subirDatos() {
    webDao.sincronizar(filedao.getContenidoDelMes());
  }
}
