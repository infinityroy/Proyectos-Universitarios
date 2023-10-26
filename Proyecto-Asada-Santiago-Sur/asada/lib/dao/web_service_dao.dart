abstract class WebServiceDao {
  Future<String> getContenidoSolicitudClientes();
  void sincronizar(String clientXmlContent);
}
