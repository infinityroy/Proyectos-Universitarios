import 'package:asada/controller/controlador_detalles_cliente.dart';
import 'package:asada/model/cliente.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

class VistaDetallesCliente extends StatefulWidget {
  final Cliente cliente;
  final ControladorDetallesCliente controladorCliente;
  const VistaDetallesCliente(
      {Key? key, required this.cliente, required this.controladorCliente})
      : super(key: key);

  @override
  VistaDetallesClienteState createState() => VistaDetallesClienteState();
}

class VistaDetallesClienteState extends State<VistaDetallesCliente> {
  final controller = TextEditingController();

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.cliente.nombre),
      ),
      body: Padding(
        padding: const EdgeInsetsDirectional.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Fecha: " + DateFormat('yyyy-MM').format(DateTime.now()),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Text(
              "Numero de medidor: " + widget.cliente.numeroMedidor.toString(),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Padding(
              padding: const EdgeInsetsDirectional.fromSTEB(0, 10, 0, 0),
              child: Row(
                children: [
                  const Text("Lectura anterior: ",
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  Text(
                    widget.cliente.datosMedidas[0].medida.toString(),
                    style: const TextStyle(fontSize: 18),
                  )
                ],
              ),
            ),
            Row(
              children: [
                const Text("Lectura Actual: ",
                    style:
                        TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.fromLTRB(16, 16, 16, 16),
                    child: TextField(
                      controller: controller,
                      decoration: InputDecoration(
                          hintText: getMedidaActual(),
                          hintStyle: const TextStyle(color: Colors.black),
                          border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(15),
                              borderSide:
                                  const BorderSide(color: Colors.black))),
                      keyboardType: TextInputType.number,
                      inputFormatters: <TextInputFormatter>[
                        FilteringTextInputFormatter.digitsOnly
                      ],
                    ),
                  ),
                ),
              ],
            ),
            ElevatedButton(
                onPressed: () async {
                  if (controller.text.isNotEmpty) {
                    showDialogLectura();
                  }
                },
                child: const Text("Confirmar cambio")),
          ],
        ),
      ),
    );
  }

  void showDialogLectura() {
    String title = "Alerta";
    String content;
    switch (editarMedida(controller.text)) {
      case -1:
        title = "¡Error!";
        content = "Error actualizando lectura en el archivo";
        break;
      case 0:
        content = "Medida actualizada existosamente!";
        break;
      case 1:
        content = "Medida agregada exitosamente!";
        break;
      case -2:
        title = "¡Error!";
        content = "Error agregando lectura en el archivo";
        break;
      case -3:
        title = "¡Error!";
        content = "La lectura no puede ser menor que la anterior!";
        break;
      default:
        content = "Error inesperado. Intentelo mas tarde";
    }

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text("OK")),
        ],
      ),
      barrierDismissible: true,
    );
  }

  String getMedidaActual() {
    if (widget.cliente.datosMedidas.length > 1) {
      return widget.cliente.datosMedidas[1].medida.toString();
    }
    return "";
  }

  int editarMedida(String me) {
    var m = int.parse(me);
    if (m <= widget.cliente.datosMedidas.first.getMedida()) {
      return -3;
    }
    if (widget.cliente.datosMedidas.length > 1) {
      //Si Hay una medida actual la edito
      widget.cliente.datosMedidas.last.setMedida(m);
      //Luego de editarla la guardo
      if (widget.controladorCliente.guardarCliente(widget.cliente)) {
        return 0;
      }
      return -1;
    }
    if (widget.controladorCliente.registrarNuevaMedida(widget.cliente,
        DatoMedida(DateTime.now().year * 100 + DateTime.now().month, m))) {
      return 1;
    }
    return -2;
  }
}
