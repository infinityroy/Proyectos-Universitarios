import 'package:asada/model/cobro.dart';
import 'package:asada/services/servicio_cobros.dart';

class ControladorCobros {
  final ServicioCobros _servicioCobros;

  ControladorCobros(this._servicioCobros);

  Future<List<Cobro>> generarListaC(String fecha) async {
    return await _servicioCobros.generarListaDeCobros(fecha);
  }

  Future<bool> tieneDatos(String fecha) async {
    return (await generarListaC(fecha)).isNotEmpty;
  }
}
