import 'dart:developer';

import 'package:asada/controller/controlador_detalles_cobro.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../model/cobro.dart';

class VistaDetallesCobro extends StatefulWidget {
  final Cobro cobro;
  final ControladorDetallesCobro controladorCobro;
  const VistaDetallesCobro(
      {Key? key, required this.cobro, required this.controladorCobro})
      : super(key: key);

  @override
  VistaDetallesCobroState createState() => VistaDetallesCobroState();
}

class VistaDetallesCobroState extends State<VistaDetallesCobro> {
  final TextEditingController dateController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  late DateTime selectedDate;
  late String fechaActual;
  List<DatoAbono> abonos = [];

  int monto = 0;
  int fecha = 0;
  String tipoPago = "Efectivo";
  String _errorMessage = "";
  @override
  void initState() {
    super.initState();
    selectedDate = DateTime.now();
    fechaActual = DateFormat('dd-MM-yyyy').format(selectedDate);
    dateController.text = fechaActual;
    WidgetsBinding.instance?.addPostFrameCallback((_) {
      setState(() {
        abonos = widget.cobro.abonos;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.cobro.nombreCliente),
      ),
      body: Padding(
        padding: const EdgeInsetsDirectional.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Fecha: " +
                  DateFormat('yyyy-MM').format(DateTime(
                      widget.cobro.fecha ~/ 100,
                      (((widget.cobro.fecha / 100) -
                                  (widget.cobro.fecha ~/ 100)) *
                              100)
                          .round(),
                      1)),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Text(
              "Numero de medidor: " + widget.cobro.numeroMedidor.toString(),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Padding(
              padding: const EdgeInsetsDirectional.fromSTEB(0, 10, 0, 0),
              child: Row(
                children: [
                  const Text("Deuda total: ",
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  Text(
                    widget.cobro.totalDeuda.toString(),
                    style: const TextStyle(fontSize: 18),
                  )
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsetsDirectional.fromSTEB(0, 10, 0, 0),
              child: Row(
                children: [
                  const Text("Deuda actual: ",
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  Text(
                    widget.cobro.obtenerDeudaActual().toString(),
                    style: const TextStyle(fontSize: 18),
                  )
                ],
              ),
            ),
            Expanded(
              child: Card(
                elevation: 15,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20)),
                margin: const EdgeInsets.only(
                    left: 20, right: 20, top: 20, bottom: 20),
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
                    itemCount: abonos.length,
                    itemBuilder: (context, index) {
                      final datoAbono = abonos[index];

                      return ListTile(
                        title: Text(
                          DateFormat('dd/MM/yyyy').format(DateTime(
                              (datoAbono.getFecha() -
                                      (datoAbono.getFecha() ~/
                                          1000000 *
                                          1000000)) ~/
                                  100,
                              (datoAbono.getFecha() -
                                      (datoAbono.getFecha() ~/
                                          1000000 *
                                          1000000)) -
                                  ((datoAbono.getFecha() -
                                          (datoAbono.getFecha() ~/
                                              1000000 *
                                              1000000)) ~/
                                      100 *
                                      100),
                              datoAbono.getFecha() ~/ 1000000)),
                          style: const TextStyle(fontSize: 18),
                        ),
                        subtitle: RichText(
                          text: TextSpan(
                            text: "₡" + datoAbono.getMonto().toString(),
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Color.fromARGB(255, 93, 176, 116),
                            ),
                            children: [
                              TextSpan(
                                text: " - " +
                                    _obtenerTipoPagoStr(
                                        datoAbono.getTipoPago()),
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Color.fromARGB(255, 45, 136, 189),
                                ),
                              ),
                            ],
                          ),
                        ),
                        leading: const Icon(
                          Icons.attach_money,
                          color: Colors.black,
                          size: 20,
                        ),
                        trailing: IconButton(
                          onPressed: () {
                            widget.controladorCobro
                                .eliminarAbono(widget.cobro, index);
                            setState(() {
                              abonos = widget.cobro.abonos;
                            });
                          },
                          icon: const Icon(
                            Icons.delete,
                            color: Colors.black,
                          ),
                        ),
                        minLeadingWidth: 20,
                        dense: true,
                        selected: false,
                        enabled: true,
                      );
                    },
                  ),
                ),
              ),
            ),
            ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      String tipoPagoDialog = "Efectivo";
                      String _errorMessageDialog = "";
                      return StatefulBuilder(builder: (context, setState) {
                        return AlertDialog(
                          content: Stack(
                            clipBehavior: Clip.none,
                            children: <Widget>[
                              Positioned(
                                right: -40.0,
                                top: -40.0,
                                child: InkResponse(
                                  borderRadius: BorderRadius.circular(50),
                                  onTap: () {
                                    log("Salgo");
                                    Navigator.of(context).pop();
                                  },
                                  child: const CircleAvatar(
                                    child: Icon(Icons.close),
                                    backgroundColor: Colors.red,
                                  ),
                                ),
                              ),
                              Form(
                                key: _formKey,
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: <Widget>[
                                    Padding(
                                      padding: const EdgeInsets.only(top: 8),
                                      child: TextFormField(
                                        controller: dateController,
                                        enabled: true,
                                        decoration: InputDecoration(
                                          labelText: 'Fecha',
                                          hintText: 'Fecha del abono',
                                          labelStyle: const TextStyle(
                                              color: Colors.black),
                                          hintStyle: const TextStyle(
                                              color: Colors.grey),
                                          border: OutlineInputBorder(
                                            borderSide: const BorderSide(
                                              color: Colors.black,
                                              width: 4,
                                            ),
                                            borderRadius:
                                                BorderRadius.circular(8),
                                          ),
                                          filled: true,
                                          fillColor: Colors.white,
                                          prefixIcon: IconButton(
                                            onPressed: () {
                                              _selectDate(context);
                                            },
                                            icon: const Icon(
                                              Icons.calendar_month,
                                              color: Colors.black,
                                              size: 20,
                                            ),
                                          ),
                                        ),
                                        keyboardType: TextInputType.number,
                                        validator: (val) {
                                          if (val!.isEmpty) {
                                            return "Ingrese una fecha";
                                          }
                                          RegExp dateRegex = RegExp(
                                              r'^[0-9]{2}-[0-9]{2}-[0-9]{4}$');
                                          if (!dateRegex.hasMatch(val)) {
                                            return "Formato de fecha invalido";
                                          }
                                          return null;
                                        },
                                        onSaved: (value) {
                                          if (value == null) {
                                            return;
                                          }
                                          DateTime tempDate =
                                              DateFormat('dd-MM-yyyy')
                                                  .parse(value);
                                          fecha = int.parse(
                                              DateFormat('ddyyyyMM')
                                                  .format(tempDate));
                                        },
                                      ),
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.only(top: 8),
                                      child: TextFormField(
                                        decoration: InputDecoration(
                                          labelText: 'Monto',
                                          hintText: 'Monto del abono',
                                          labelStyle: const TextStyle(
                                              color: Colors.black),
                                          hintStyle: const TextStyle(
                                              color: Colors.grey),
                                          border: OutlineInputBorder(
                                            borderSide: const BorderSide(
                                              color: Colors.black,
                                              width: 4,
                                            ),
                                            borderRadius:
                                                BorderRadius.circular(8),
                                          ),
                                          filled: true,
                                          fillColor: Colors.white,
                                          prefixIcon: const Icon(
                                            Icons.attach_money,
                                            color: Colors.black,
                                          ),
                                        ),
                                        keyboardType: TextInputType.number,
                                        validator: (val) {
                                          if (val!.isEmpty) {
                                            return "Ingrese un monto";
                                          }
                                          try {
                                            int montoAbono = int.parse(val);
                                            if (montoAbono <= 0) {
                                              return "Monto no valido";
                                            }
                                          } catch (e) {
                                            return null;
                                          }
                                          return null;
                                        },
                                        onSaved: (value) {
                                          if (value == null) {
                                            return;
                                          }
                                          monto = int.parse(value);
                                        },
                                      ),
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.only(top: 8),
                                      child: DropdownButtonFormField(
                                        value: tipoPagoDialog,
                                        items: dropdownItems,
                                        onChanged: (String? newValue) {
                                          setState(() {
                                            tipoPagoDialog = newValue!;
                                            tipoPago = newValue;
                                            log("Guardo tipo de pago");
                                          });
                                        },
                                        isExpanded: true,
                                        style: const TextStyle(
                                          color: Colors.black,
                                          fontSize: 18,
                                        ),
                                        decoration: InputDecoration(
                                          labelStyle: const TextStyle(
                                              color: Colors.black),
                                          hintStyle: const TextStyle(
                                              color: Colors.grey),
                                          border: OutlineInputBorder(
                                            borderSide: const BorderSide(
                                              color: Colors.black,
                                              width: 4,
                                            ),
                                            borderRadius:
                                                BorderRadius.circular(8),
                                          ),
                                          filled: true,
                                          fillColor: Colors.white,
                                        ),
                                      ),
                                    ),
                                    if (_errorMessageDialog.isNotEmpty)
                                      Padding(
                                          padding: const EdgeInsets.all(8),
                                          child: Text(
                                            _errorMessageDialog,
                                            style: const TextStyle(
                                              color: Colors.red,
                                              fontWeight: FontWeight.bold,
                                            ),
                                            textAlign: TextAlign.center,
                                          )),
                                    Padding(
                                      padding: const EdgeInsets.only(top: 8),
                                      child: ElevatedButton(
                                        onPressed: () async {
                                          if (_formKey.currentState != null &&
                                              _formKey.currentState?.validate()
                                                  as bool) {
                                            _formKey.currentState?.save();
                                            if (_agregarAbono(context)) {
                                              Navigator.of(context).pop();
                                              setState(() {
                                                _errorMessage = "";
                                                _errorMessageDialog = "";
                                              });
                                            } else {
                                              setState(() {
                                                _errorMessage =
                                                    "¡Monto es mayor a la deuda actual!";
                                                _errorMessageDialog =
                                                    "¡Monto es mayor a la deuda actual!";
                                              });
                                            }
                                          }
                                        },
                                        child: const Center(
                                            child: Text("Agregar")),
                                      ),
                                    )
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      });
                    },
                  );
                },
                child: const Center(child: Text("Agregar abono"))),
          ],
        ),
      ),
    );
  }

  _selectDate(BuildContext context) async {
    DateTime firstDateTemp = DateTime(
        widget.cobro.fecha ~/ 100,
        (((widget.cobro.fecha / 100) - (widget.cobro.fecha ~/ 100)) * 100)
            .round(),
        1);

    final DateTime? selected = await showDatePicker(
      context: context,
      initialDate: selectedDate,
      firstDate: firstDateTemp,
      lastDate: DateTime.now().add(const Duration(days: 1)),
    );
    if (selected != null && selected != selectedDate) {
      setState(() {
        selectedDate = selected;
        fechaActual = DateFormat('dd-MM-yyyy').format(selected);
        dateController.text = fechaActual;
      });
    }
  }

  bool _agregarAbono(BuildContext context) {
    if ((widget.cobro.obtenerDeudaActual() - monto) < 0) {
      return false;
    }
    widget.controladorCobro
        .agregarAbono(widget.cobro, monto, fecha, _obtenerTipoPago(tipoPago));
    setState(() {
      abonos = widget.cobro.abonos;
    });
    return true;
  }

  _obtenerTipoPago(String tipoPago) {
    switch (tipoPago) {
      case "Efectivo":
        return 0;
      case "Sinpe":
        return 1;
      case "Deposito Bancario":
        return 2;
      default:
        return 3;
    }
  }

  _obtenerTipoPagoStr(int tipoPago) {
    switch (tipoPago) {
      case 0:
        return "Efectivo";
      case 1:
        return "Sinpe";
      case 2:
        return "Deposito Bancario";
      default:
        return "Otro";
    }
  }

  List<DropdownMenuItem<String>> get dropdownItems {
    const List<DropdownMenuItem<String>> menuItems = [
      DropdownMenuItem(
          child: Center(child: Text("Efectivo")), value: "Efectivo"),
      DropdownMenuItem(child: Center(child: Text("Sinpe")), value: "Sinpe"),
      DropdownMenuItem(
          child: Center(child: Text("Depósito Bancario")),
          value: "Deposito Bancario"),
      DropdownMenuItem(child: Center(child: Text("Otro")), value: "Otro"),
    ];
    return menuItems;
  }
}
