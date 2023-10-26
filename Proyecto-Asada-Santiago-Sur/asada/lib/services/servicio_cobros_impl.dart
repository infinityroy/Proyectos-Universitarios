import 'package:asada/services/servicio_cobros.dart';
import 'package:asada/model/cobro.dart';
import 'package:asada/dao/archivo_local_dao.dart';

class ServicioCobrosImpl implements ServicioCobros {
  final ArchivoLocalDao filedao;

  ServicioCobrosImpl(this.filedao);

  @override
  Future<List<Cobro>> generarListaDeCobros(String mes) async {
    //String contenido = webDao.getContenidoSolicitudCobros();
    // TODO cambiar el string horrible por el contenido de arriba
    if (filedao.archivoDelMesYaExiste("Cobro", mes)) {
      return filedao.getCobros(mes, false);
    }
    await filedao.crearArchivoCobros(
        "<Facturas><ID_Factura>100</ID_Factura><ID_ASADA>4</ID_ASADA><Facturas_Lista><Detalles_Linea><ID_Servicio>1</ID_Servicio><Codigo_Servicio>00120</Codigo_Servicio><Cliente>Denis Rodriguez P</Cliente><Hidrometro>00001</Hidrometro><Metros_Consumidos>0052</Metros_Consumidos><Monto>11570</Monto></Detalles_Linea><Detalles_Linea><ID_Servicio>2</ID_Servicio><Codigo_Servicio>02501</Codigo_Servicio><Cliente>Alice Hidalgo Mata</Cliente><Hidrometro>00002</Hidrometro><Metros_Consumidos>00045</Metros_Consumidos><Monto>10400</Monto></Detalles_Linea><Detalles_Linea><ID_Servicio>3</ID_Servicio><Cliente>Pedro Mora Mora</Cliente><Codigo_Servicio>0239</Codigo_Servicio><Hidrometro>00003</Hidrometro><Metros_Consumidos>0000</Metros_Consumidos><Monto>0</Monto></Detalles_Linea></Facturas_Lista></Facturas>");
    return filedao.getCobros(mes, true);
  }

  @override
  bool agregarAbono(Cobro c, int monto, int fecha, int tipoPago) {
    DatoAbono abono = DatoAbono(fecha, monto, tipoPago);
    c.abonos.add(abono);
    return filedao.agregarAbono(c, monto, fecha, tipoPago);
  }

  @override
  bool borrarAbono(Cobro c, int index) {
    return filedao.eliminarAbono(c, index);
  }
}
