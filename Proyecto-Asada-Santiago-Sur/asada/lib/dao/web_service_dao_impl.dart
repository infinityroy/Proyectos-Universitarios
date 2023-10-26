import 'package:asada/dao/web_service_dao.dart';
import 'package:http/http.dart' as http;

class WebServiceDaoImpl implements WebServiceDao {
  var envelope = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ConsultarListaLectura xmlns="http://adaacr.com">
      <Cod_ASADA>04</Cod_ASADA>
    </ConsultarListaLectura>
  </soap:Body>
</soap:Envelope>
''';

  @override
  void sincronizar(String clientXmlContent) {
    // TODO: implement sincronizar
  }

  @override
  Future<String> getContenidoSolicitudClientes() async {
    http.Response response = await http.post(
        Uri.parse('http://adaacr.com/apis.asmx?op=ConsultarListaLectura'),
        headers: {
          "Content-Type": "text/xml; charset=utf-8",
          "SOAPAction": "http://adaacr.com/ConsultarListaLectura",
          "Host": "adaacr.com"
        },
        body: envelope);
    if (response.statusCode == 200) {
      return response.body;
    }
    return "";
  }
}
