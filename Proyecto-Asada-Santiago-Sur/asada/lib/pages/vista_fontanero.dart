import 'dart:developer';

import 'package:asada/controller/controlador_detalles_cliente.dart';
import 'package:asada/controller/controlador_fontanero.dart';
import 'package:asada/model/cliente.dart';
import 'package:asada/model/user.dart';
import 'package:asada/pages/vista_detalles_cliente.dart';
import 'package:flutter/material.dart';

class VistaFontaneroWidget extends StatefulWidget {
  final ControladorFontanero controlador;
  final ControladorDetallesCliente controladorCliente;
  final User usuario;

  const VistaFontaneroWidget(
      {Key? key,
      required this.controlador,
      required this.controladorCliente,
      required this.usuario})
      : super(key: key);

  @override
  _VistaFontaneroWidget createState() => _VistaFontaneroWidget();
}

class _VistaFontaneroWidget extends State<VistaFontaneroWidget> {
  final formKey = GlobalKey<FormState>();
  final scaffoldKey = GlobalKey<ScaffoldState>();
  List<Cliente> allClients = [];
  List<Cliente> filteredClients = [];
  final controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance?.addPostFrameCallback((_) {
      _actualizarClientes();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        resizeToAvoidBottomInset: false,
        appBar: AppBar(
            title: const Text('Clientes'),
            leading: const BackButton(
              color: Colors.white,
            ),
            actions: [
              Padding(
                padding: const EdgeInsetsDirectional.fromSTEB(0, 0, 10, 0),
                child: Row(
                  children: [
                    const CircleAvatar(
                      radius: 13,
                      child: Icon(Icons.person, size: 20),
                    ),
                    Text(
                      widget.usuario.getUserName(),
                      style: const TextStyle(
                        fontSize: 15,
                      ),
                    )
                  ],
                ),
              ),
            ]),
        key: scaffoldKey,
        backgroundColor: Colors.white,
        body: Column(
          children: [
            Container(
              margin: const EdgeInsets.fromLTRB(16, 16, 16, 16),
              child: TextField(
                controller: controller,
                decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.search),
                    hintText: 'Nombre del cliente o numero del medidor',
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: const BorderSide(color: Colors.black))),
                onChanged: searchClient,
              ),
            ),
            const Text("Nombre    N°Medidor"),
            Expanded(
              child: Scrollbar(
                isAlwaysShown: true,
                interactive: true,
                hoverThickness: 30,
                child: ListView.separated(
                  keyboardDismissBehavior:
                      ScrollViewKeyboardDismissBehavior.onDrag,
                  separatorBuilder: (context, index) => const Divider(
                    color: Colors.black,
                    indent: 15,
                    endIndent: 15,
                  ),
                  itemCount: filteredClients.length,
                  itemBuilder: (context, index) {
                    final cliente = filteredClients[index];

                    return ListTile(
                      leading: CircleAvatar(
                        radius: 25,
                        backgroundImage: Image.asset("assets/client.png").image,
                      ),
                      title: obtenerWidgetNombre(cliente),
                      subtitle: Text(
                        cliente.numeroMedidor.toString(),
                      ),
                      trailing: const Icon(Icons.keyboard_arrow_right),
                      onTap: () {
                        // ignore: avoid_print
                        print(cliente.nombre);
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => VistaDetallesCliente(
                                cliente: cliente,
                                controladorCliente: widget.controladorCliente),
                          ),
                        );
                      },
                      dense: true,
                      selected: false,
                      enabled: true,
                    );
                  },
                ),
              ),
            ),
            ElevatedButton(
                onPressed: () {
                  _actualizarClientes();
                },
                child: const Text("Actualizar Lista")),
            TextButton(
                onPressed: () async {
                  log("Enviar");
                },
                // TODO CONECTAR
                child: const Text("Enviar"))
          ],
        ));
  }

  RichText obtenerWidgetNombre(Cliente cliente) {
    String note = "";
    String nameText = cliente.nombre.toUpperCase();
    double size = 18;
    int maxStringLen = 25; //35
    if (nameText.contains("[") && nameText.contains("]")) {
      int firstIndex = nameText.indexOf("[");
      int secondIndex = nameText.indexOf("]");
      note = cliente.nombre.substring(firstIndex, secondIndex + 1);
      nameText = nameText.substring(0, firstIndex);

      if (cliente.nombre.length >= maxStringLen) {
        size = 18;
        nameText = nameText.substring(
              0,
              maxStringLen - (secondIndex - firstIndex) - 4,
            ) +
            "... ";
      }
    }
    //nameText.characters.getRange(0, 20).string + "...";
    return RichText(
      text: TextSpan(
          text: nameText,
          style: TextStyle(
              fontSize: size, fontWeight: FontWeight.bold, color: Colors.black),
          children: [
            TextSpan(
                text: note,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color.fromARGB(255, 93, 176, 116),
                ))
          ]),
    );
  }

  void searchClient(String query) {
    //log("entra en search");
    final suggestions = allClients.where((cliente) {
      final nombreCliente = cliente.nombre.toLowerCase();
      final input = query.toLowerCase();

      int intInput = -1;
      try {
        intInput = int.parse(query);
        return nombreCliente.contains(input) ||
            cliente.numeroMedidor.toString().contains(intInput.toString());
      } catch (e) {
        log(e.toString());
      }
      return nombreCliente.contains(input);
    }).toList();
    setState(() => filteredClients = suggestions);
  }

  _actualizarClientes() async {
    var clientesNuevos = await widget.controlador.generarListaC();
    setState(() {
      allClients = clientesNuevos;
      filteredClients = clientesNuevos;
    });
  }
}
