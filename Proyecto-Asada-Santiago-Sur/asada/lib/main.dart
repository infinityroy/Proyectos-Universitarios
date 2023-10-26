import 'dart:io';

import 'package:asada/controller/controlador_cobros.dart';
import 'package:asada/controller/controlador_detalles_cliente.dart';
import 'package:asada/controller/controlador_detalles_cobro.dart';
import 'package:asada/controller/controlador_fontanero.dart';
import 'package:asada/controller/controlador_login.dart';
import 'package:asada/dao/archivo_local_dao.dart';
import 'package:asada/dao/dao_usuario.dart';
import 'package:asada/dao/local_xml_dao_impl.dart';
import 'package:asada/dao/web_service_dao_impl.dart';
import 'package:asada/model/cobro.dart';
import 'package:asada/model/user.dart';
import 'package:asada/pages/vista_cobros.dart';
import 'package:asada/pages/vista_detalles_cobro.dart';
import 'package:asada/pages/vista_fontanero.dart';
import 'package:asada/pages/vista_login.dart';
import 'package:asada/services/servicio_clientes.dart';
import 'package:asada/services/servicio_clientes_impl.dart';
import 'package:asada/services/servicio_cobros.dart';
import 'package:asada/services/servicio_cobros_impl.dart';
import 'package:asada/services/servicio_usuario.dart';
import 'package:asada/services/servicio_usuario_impl.dart';
import 'package:flutter/material.dart';
import 'dao/sqllite_dao.dart';
import 'dao/web_service_dao.dart';
import 'package:path_provider/path_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  Directory appDocDir = await getApplicationDocumentsDirectory();
  String appDocPath = appDocDir.path;
  runApp(MyApp(folderPath: appDocPath));
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key, required this.folderPath}) : super(key: key);
  final String folderPath;
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    Map<int, Color> color = {
      50: Colors.grey[50]!,
      100: Colors.grey[100]!,
      200: Colors.grey[200]!,
      300: Colors.grey[300]!,
      400: Colors.grey[400]!,
      500: Colors.grey[500]!,
      600: Colors.grey[600]!,
      700: Colors.grey[700]!,
      800: Colors.grey[800]!,
      900: Colors.grey[900]!,
    };
    WebServiceDao wsd = WebServiceDaoImpl();
    ArchivoLocalDao ald =
        LocalXmlDaoImpl(folderPath + "/lecturas", folderPath + "/cobros");
    ServicioClientes sc = ServicioClientesImpl(wsd, ald);
    DaoUsuario du = SqliteDao();

    ServicioUsuario su = ServicioUsuarioImpl(du);
    ControladorLogin cli = ControladorLogin(su);
    ControladorFontanero cf = ControladorFontanero(sc);
    ControladorDetallesCliente cdc = ControladorDetallesCliente(sc);

    ServicioCobros sco = ServicioCobrosImpl(ald);
    ControladorCobros cc = ControladorCobros(sco);

    ControladorDetallesCobro cdco = ControladorDetallesCobro(sco);

    return MaterialApp(
      title: 'Aplicacion ASADA Santiago Sur',
      theme: ThemeData(
        brightness: Brightness.light,
        primarySwatch: MaterialColor(0xFF00838F, color),
      ),
      //home: const LoginWidget(),
      initialRoute: '/',
      routes: {
        '/': (BuildContext context) => LoginWidget(controlador: cli),
        '/fontanero': (BuildContext context) {
          User usuario = ModalRoute.of(context)?.settings.arguments as User;
          return VistaFontaneroWidget(
            controlador: cf,
            controladorCliente: cdc,
            usuario: usuario,
          );
        },
        '/cobros': (BuildContext context) {
          User usuario = ModalRoute.of(context)?.settings.arguments as User;
          return VistaCobrosWidget(controlador: cc, usuario: usuario);
        },
        '/vistaDetallesCobro': (BuildContext context) {
          Cobro cobro = ModalRoute.of(context)?.settings.arguments as Cobro;
          return VistaDetallesCobro(
            controladorCobro: cdco,
            cobro: cobro,
          );
        },
      },
    );
  }
}
