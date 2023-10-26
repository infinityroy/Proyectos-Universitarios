import 'package:asada/model/user.dart';
import 'package:asada/services/servicio_usuario.dart';

class ControladorLogin {
  final ServicioUsuario _servicioUsuario;

  ControladorLogin(this._servicioUsuario);

  Future<User> iniciarSesion(String nombreDeUsuario, String contrasena) async {
    return await _servicioUsuario.autentificar(nombreDeUsuario, contrasena);
  }

  bool registrarce(String nuevoNombreUsuario, String nuevaContra, String tipo) {
    return _servicioUsuario.create(nuevoNombreUsuario, nuevaContra, tipo);
  }
}
