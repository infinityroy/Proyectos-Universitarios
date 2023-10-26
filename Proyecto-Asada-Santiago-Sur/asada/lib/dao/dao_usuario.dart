import 'package:asada/model/user.dart';

abstract class DaoUsuario {
  Future<User> verificarUsuario(String username, String password);

  bool agregarUsuario(String username, String password, String type);
}
