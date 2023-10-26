import 'package:asada/controller/controlador_login.dart';
import 'package:asada/model/user.dart';
import 'package:flutter/material.dart';

class LoginWidget extends StatefulWidget {
  final ControladorLogin controlador;
  const LoginWidget({Key? key, required this.controlador}) : super(key: key);

  @override
  _LoginWidgetState createState() => _LoginWidgetState();
}

class _LoginWidgetState extends State<LoginWidget> {
  late bool passwordVisibility;
  final _formKey = GlobalKey<FormState>();
  final scaffoldKey = GlobalKey<ScaffoldState>();
  bool _loading = false;
  String userName = "";
  String password = "";

  String _errorMessage = "";

  @override
  void initState() {
    super.initState();
    passwordVisibility = false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: scaffoldKey,
      backgroundColor: Colors.white,
      body: Form(
        key: _formKey,
        //autovalidateMode: AutovalidateMode.onUserInteraction,
        child: Stack(
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 30),
              child: Image.asset(
                "assets/logo.jpeg",
                height: 200,
              ),
            ),
            Center(
              child: SingleChildScrollView(
                child: Card(
                  elevation: 15,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)),
                  margin: const EdgeInsets.only(
                      left: 20, right: 20, top: 120, bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 35, vertical: 20),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        TextFormField(
                          onSaved: (value) {
                            userName = value!;
                          },
                          obscureText: false,
                          decoration: InputDecoration(
                            labelText: 'Usuario',
                            hintText: 'Su usuario...',
                            labelStyle: const TextStyle(color: Colors.black),
                            hintStyle: const TextStyle(color: Colors.grey),
                            border: OutlineInputBorder(
                              borderSide: const BorderSide(
                                color: Colors.black,
                                width: 4,
                              ),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            filled: true,
                            fillColor: Colors.white,
                            prefixIcon: const Icon(
                              Icons.email_outlined,
                              color: Colors.black,
                            ),
                          ),
                          style: const TextStyle(color: Colors.black),
                          keyboardType: TextInputType.emailAddress,
                          validator: (val) {
                            if (val!.isEmpty) {
                              return 'Ingrese su usuario';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 20),
                        TextFormField(
                          obscureText: !passwordVisibility,
                          decoration: InputDecoration(
                            labelText: 'Contraseña',
                            hintText: 'Su contraseña...',
                            labelStyle: const TextStyle(color: Colors.black),
                            hintStyle: const TextStyle(color: Colors.grey),
                            border: OutlineInputBorder(
                              borderSide: const BorderSide(
                                color: Colors.black,
                                width: 4,
                              ),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            filled: true,
                            fillColor: Colors.white,
                            prefixIcon: const Icon(
                              Icons.lock_outline,
                              color: Colors.black,
                            ),
                            suffixIcon: InkWell(
                              onTap: () => setState(
                                () => passwordVisibility = !passwordVisibility,
                              ),
                              child: Icon(
                                passwordVisibility
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                                color: const Color(0x80FFFFFF),
                                size: 22,
                              ),
                            ),
                          ),
                          style: const TextStyle(color: Colors.black),
                          onSaved: (value) {
                            password = value!;
                          },
                          validator: (val) {
                            if (val!.isEmpty) {
                              return 'Ingrese su contraseña';
                            }

                            return null;
                          },
                        ),
                        Padding(
                          padding: const EdgeInsets.only(top: 30),
                          child: ElevatedButton(
                            onPressed: () async {
                              if (_formKey.currentState?.validate() as bool) {
                                _formKey.currentState?.save();
                                _login(context);
                              }
                            },
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Text("Iniciar sesión"),
                                if (_loading)
                                  Container(
                                    height: 20,
                                    width: 20,
                                    margin: const EdgeInsets.only(left: 20),
                                    child: const CircularProgressIndicator(
                                        color: Colors.white),
                                  )
                              ],
                            ),
                          ),
                        ),
                        if (_errorMessage.isNotEmpty)
                          Padding(
                              padding: const EdgeInsets.all(8),
                              child: Text(
                                _errorMessage,
                                style: const TextStyle(
                                  color: Colors.red,
                                  fontWeight: FontWeight.bold,
                                ),
                                textAlign: TextAlign.center,
                              )),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text('¿Has olvidado tu contraseña?'),
                            TextButton(
                                onPressed: () {
                                  // _showRegister(context);
                                },
                                child: const Text("Recuperar"))
                          ],
                        )
                      ],
                    ),
                  ),
                ),
              ),
            )
          ],
        ),
      ),
    );
  }

  void _login(BuildContext context) async {
    if (!_loading) {
      setState(() {
        _loading = true;
      });
      User usuario = await widget.controlador.iniciarSesion(userName, password);
      switch (usuario.getType()) {
        case "F":
          setState(() {
            _loading = false;
          });
          Navigator.of(context).pushNamed("/fontanero", arguments: usuario);
          break;
        case "C":
          setState(() {
            _loading = false;
          });
          Navigator.of(context).pushNamed("/cobros", arguments: usuario);
          break;
        case "NP":
          setState(() {
            _errorMessage = "Contraseña incorrecta";
            _loading = false;
          });
          break;
        case "NU":
          setState(() {
            _errorMessage = "El usuario no existe";
            _loading = false;
          });
          break;
        default:
          setState(() {
            _loading = false;
          });
      }
    }
  }
}
