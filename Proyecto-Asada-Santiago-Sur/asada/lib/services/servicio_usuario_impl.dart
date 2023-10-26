import 'package:asada/dao/dao_usuario.dart';
import 'package:asada/model/user.dart';
import 'package:asada/services/servicio_usuario.dart';

class ServicioUsuarioImpl implements ServicioUsuario {
  DaoUsuario daoUsuario;

  @override
  Future<User> autentificar(String username, String password) async {
    return await daoUsuario.verificarUsuario(username, password);
  }

  @override
  bool create(String username, String password, String type) {
    return daoUsuario.agregarUsuario(username, password, type);
  }

  ServicioUsuarioImpl(this.daoUsuario);
}
