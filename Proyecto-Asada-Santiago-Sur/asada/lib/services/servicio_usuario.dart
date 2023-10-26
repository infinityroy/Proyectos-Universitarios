import 'package:asada/model/user.dart';

abstract class ServicioUsuario {
  bool create(String username, String password, String type);
  Future<User> autentificar(String username, String password);
}
