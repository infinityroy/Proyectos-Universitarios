import 'package:asada/dao/web_service_dao.dart';
import 'package:asada/dao/web_service_dao_impl.dart';
import 'package:test/test.dart';

void main() async {
  test("Valor retornado no es vacio", () async {
    WebServiceDao dao = WebServiceDaoImpl();
    String content = await dao.getContenidoSolicitudClientes();

    expect(content, isNot(equals("")));
  });
}
