import 'package:asada/model/cobro.dart';
import 'package:asada/services/servicio_cobros.dart';

class ControladorDetallesCobro {
  final ServicioCobros _servicioCobros;

  ControladorDetallesCobro(this._servicioCobros);

  bool agregarAbono(Cobro c, int monto, int fecha, int tipoPago) {
    return _servicioCobros.agregarAbono(c, monto, fecha, tipoPago);
  }

  bool eliminarAbono(Cobro c, int index) {
    c.abonos.removeAt(index);
    return _servicioCobros.borrarAbono(c, index);
  }
}
