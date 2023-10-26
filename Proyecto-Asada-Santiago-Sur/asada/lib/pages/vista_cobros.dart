import 'dart:developer';
import 'package:asada/controller/controlador_cobros.dart';
import 'package:asada/model/cobro.dart';
import 'package:asada/model/user.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class VistaCobrosWidget extends StatefulWidget {
  final ControladorCobros controlador;
  final User usuario;

  const VistaCobrosWidget(
      {Key? key, required this.controlador, required this.usuario})
      : super(key: key);

  @override
  _VistaCobrosWidget createState() => _VistaCobrosWidget();
}

class _VistaCobrosWidget extends State<VistaCobrosWidget> {
  final formKey = GlobalKey<FormState>();
  final scaffoldKey = GlobalKey<ScaffoldState>();
  List<Cobro> allCobros = [];
  List<Cobro> filteredCobros = [];
  final controller = TextEditingController();
  late String fecha;
  late DateTime date;
  int direccion = 0;

  @override
  void initState() {
    super.initState();
    date = DateTime.now();
    fecha = DateFormat('yyyy-MM').format(date);
    //cobros = Cobro.cobros;
    WidgetsBinding.instance?.addPostFrameCallback((_) {
      _actualizarCobros(fecha, date, direccion);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
            //title: Text(DateFormat('yyyy-MM').format(date)),
            leading: const BackButton(
              color: Colors.white,
            ),
            actions: [
              IconButton(
                icon: const Icon(
                  Icons.arrow_left,
                  color: Colors.white,
                  size: 40,
                ),
                onPressed: () {
                  DateTime tempDate =
                      DateTime(date.year, date.month - 1, date.day);
                  String tempFecha = DateFormat('yyyy-MM').format(tempDate);
                  _actualizarCobros(tempFecha, tempDate, direccion - 1);
                },
              ),
              Center(
                child: Text(
                  DateFormat('yyyy-MM').format(date),
                  style: const TextStyle(
                      fontSize: 20, fontWeight: FontWeight.bold),
                ),
              ),
              //const SizedBox(width: 15),
              IconButton(
                icon: const Icon(
                  Icons.arrow_right,
                  color: Colors.white,
                  size: 40,
                ),
                onPressed: () {
                  DateTime tempDate =
                      DateTime(date.year, date.month + 1, date.day);
                  String tempFecha = DateFormat('yyyy-MM').format(tempDate);
                  _actualizarCobros(tempFecha, tempDate, direccion + 1);
                },
              ),
              const SizedBox(width: 35),
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
            Expanded(
              child: Scrollbar(
                isAlwaysShown: true,
                interactive: true,
                hoverThickness: 30,
                child: ListView.separated(
                  separatorBuilder: (context, index) => const Divider(
                    color: Colors.black,
                    indent: 15,
                    endIndent: 15,
                  ),
                  itemCount: filteredCobros.length,
                  itemBuilder: (context, index) {
                    final cobro = filteredCobros[index];

                    return ListTile(
                      leading: CircleAvatar(
                        radius: 25,
                        backgroundImage: Image.asset("assets/money.png").image,
                      ),
                      title: Text(
                        cobro.nombreCliente.toUpperCase(),
                        style: const TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(
                        cobro.numeroMedidor.toString(),
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          obtenerBoton(cobro),
                          const Icon(Icons.keyboard_arrow_right),
                        ],
                      ),
                      onTap: () {
                        //log(cobro.nombreCliente);
                        Navigator.of(context)
                            .pushNamed("/vistaDetallesCobro", arguments: cobro);
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
                  _actualizarCobros(fecha, date, direccion);
                },
                child: const Text("Actualizar Lista")),
          ],
        ));
  }

  ElevatedButton obtenerBoton(Cobro cobro) {
    int deuda = obtenerDeudaActual(cobro);
    if (deuda <= 0) {
      return ElevatedButton(
        onPressed: () {},
        style: ElevatedButton.styleFrom(
          elevation: 5,
          primary: const Color.fromARGB(255, 93, 176, 116),
        ),
        child: const Text(
          "Cancelado",
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
      );
    }
    return ElevatedButton(
      onPressed: () {},
      style: ElevatedButton.styleFrom(
        elevation: 5,
        primary: const Color.fromARGB(255, 228, 228, 228),
      ),
      child: Text(
        deuda.toString(),
        style: const TextStyle(
          color: Colors.black,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  int obtenerDeudaActual(Cobro cobro) {
    int deuda = cobro.totalDeuda;
    for (DatoAbono abono in cobro.abonos) {
      deuda -= abono.getMonto();
    }
    return deuda;
  }

  void searchClient(String query) {
    final suggestions = allCobros.where((cobro) {
      final nombreCliente = cobro.nombreCliente.toLowerCase();
      final input = query.toLowerCase();

      int intInput = -1;
      try {
        intInput = int.parse(query);
        return nombreCliente.contains(input) ||
            cobro.numeroMedidor.toString().contains(intInput.toString());
      } catch (e) {
        log(e.toString());
      }

      return nombreCliente.contains(input);
    }).toList();
    setState(() => filteredCobros = suggestions);
  }

  void showDialogMes(DateTime date) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("¡Error!"),
        content: Text(
            "No existen cobros del mes: " + DateFormat("yyyy-MM").format(date)),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: const Text("OK"),
          ),
        ],
      ),
      barrierDismissible: true,
    );
  }

  _actualizarCobros(String fecha, DateTime date, int direccion) async {
    var cobrosNuevos = await widget.controlador.generarListaC(fecha);
    if (cobrosNuevos.isEmpty && direccion != 0 && direccion != 1) {
      showDialogMes(date);
      return;
    }
    setState(() {
      this.direccion = direccion;
      this.fecha = fecha;
      this.date = date;
      allCobros = cobrosNuevos;
      filteredCobros = cobrosNuevos;
    });
  }
}
