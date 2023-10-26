import 'package:flutter/material.dart';

class RouteManager {
  static const String loginRoute = '/';
  static const String fontaneroRoute = '/fontanero';
  static const String detallesClienteRoute = '/detallescliente';
  //static const String cobradorRoute = '/cobrador';
  //static const String detalleCobroRoute = '/datallescobro';

  static Route<dynamic> generarRuta(RouteSettings settings) {
    switch (settings.name) {
      /*case loginRoute:
        return MaterialPageRoute(
          builder: (context)=>LoginWidget()
          );
      case fontaneroRoute:
        return MaterialPageRoute(
          builder: (context)=>VistaFontaneroWidget()
          );
      case detallesClienteRoute:
        return MaterialPageRoute(
          builder: (context)=>VistaDetallesCliente(cliente: cliente)
          );
      */
      default:
        throw const FormatException("Ruta no encontrada");
    }
  }
}
