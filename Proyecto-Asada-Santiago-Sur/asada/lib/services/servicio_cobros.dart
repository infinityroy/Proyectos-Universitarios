import 'package:asada/model/cobro.dart';

abstract class ServicioCobros {
  Future<List<Cobro>> generarListaDeCobros(String mes);
  bool agregarAbono(Cobro c, int monto, int fecha, int tipoPago);
  bool borrarAbono(Cobro c, int index);
}
