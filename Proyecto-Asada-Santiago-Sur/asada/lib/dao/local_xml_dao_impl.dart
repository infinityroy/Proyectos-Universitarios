import 'dart:developer';

import 'package:asada/dao/archivo_local_dao.dart';
import 'package:asada/model/cliente.dart';
import 'package:asada/model/cobro.dart';
import 'package:intl/intl.dart';
import 'package:xml/xml.dart';
import 'dart:io';

class LocalXmlDaoImpl implements ArchivoLocalDao {
  final String clientefolderPath;
  final String cobrofolderPath;

  LocalXmlDaoImpl(this.clientefolderPath, this.cobrofolderPath);

  @override
  List<Cliente> getClientes() {
    List<Cliente> clientesEncontrados = [];
    String thisMonthsFile = getNameForThisMonthsFile();
    String newFilePath = clientefolderPath + "/" + thisMonthsFile;

    if (!File(newFilePath).existsSync()) {
      return clientesEncontrados;
    }

    File file = File(newFilePath);
    XmlDocument document = XmlDocument.parse(file.readAsStringSync());
    Iterable<XmlElement> datos = document.findAllElements('Detalles_Linea');
    for (var item in datos) {
      clientesEncontrados.add(Cliente(
          int.parse(item.findElements('Hidrometro').single.text),
          item.findElements('Cliente').single.text, [
        DatoMedida(
            (DateTime.now().year * 100 +
                DateTime.now().month -
                1), //-1 para tomar la fecha del mes anterior
            int.parse(item.findElements('Lectura_Anterior').single.text)),
      ]));
      if (item.findElements('Lectura_Actual').single.innerText != '') {
        clientesEncontrados.last.agregarDatosMedida(
            (DateTime.now().year * 100 + DateTime.now().month),
            int.parse(item.findElements('Lectura_Actual').single.text));
      }
    }
    return clientesEncontrados;
  }

  @override
  String getContenidoDelMes() {
    String thisMonthsFile = getNameForThisMonthsFile();
    String newFilePath = clientefolderPath + '/' + thisMonthsFile;
    if (!File(newFilePath).existsSync()) {
      return '';
    }
    File file = File(newFilePath);
    XmlDocument document = XmlDocument.parse(file.readAsStringSync());
    return document.toString();
  }

  @override
  bool crearArchivoClientes(String contenido) {
    String nombre = getNameForThisMonthsFile();
    try {
      Future<File> newFile =
          File(clientefolderPath + '/' + nombre).create(recursive: true);
      newFile.then((file) => file.writeAsString(contenido));
    } on Exception {
      return false;
    }
    return true;
  }

  @override
  bool actualizarArchivoClientes(String contenido) {
    XmlDocument nuevaInfo = XmlDocument.parse(contenido);
    String thisMonthsFile = getNameForThisMonthsFile();
    File file = File(clientefolderPath + '/' + thisMonthsFile);

    file.writeAsString(nuevaInfo.toXmlString());
    return true;
  }

  @override
  bool guardarCliente(Cliente c) {
    int medidorPorBuscar = c.getNumeroMedidor();
    String thisMonthsFile = getNameForThisMonthsFile();
    try {
      File file = File(clientefolderPath + '/' + thisMonthsFile);
      XmlDocument document = XmlDocument.parse(file.readAsStringSync());
      final datos = document.findAllElements('Detalles_Linea');
      for (var item in datos) {
        if (int.parse(item.findAllElements('Hidrometro').single.text) ==
            medidorPorBuscar) {
          item.findAllElements('Lectura_Actual').single.innerText =
              c.datosMedidas.last.medida.toString();
          break;
        }
      }
      file.writeAsString(document.toXmlString());
      return true;
    } catch (e, s) {
      log("Error: " + e.toString());
      log("StackTrace: \n" + s.toString());
      return false;
    }
  }

  @override
  bool archivoDelMesYaExiste(String tipo, String fecha) {
    if (tipo == 'Cliente') {
      String filePath = clientefolderPath + '/' + fecha;
      return File(filePath).existsSync();
    } else {
      String filePath = cobrofolderPath + '/' + fecha;
      return File(filePath).existsSync();
    }
  }

  String getNameForThisMonthsFile() {
    String thisMonthsFile = DateFormat('yyyy-MM').format(DateTime.now());
    return thisMonthsFile;
  }

  @override
  List<Cobro> getCobros(String fecha, bool primeraPasada) {
    List<Cobro> cobrosEncontrados = [];
    String thisMonthsFile = fecha;
    String newFilePath = cobrofolderPath + "/" + thisMonthsFile;
    File file = File(newFilePath);
    if (!file.existsSync()) {
      return cobrosEncontrados;
    }

    XmlDocument document = XmlDocument.parse(file.readAsStringSync());
    Iterable<XmlElement> datos = document.findAllElements('Detalles_Linea');
    for (var item in datos) {
      cobrosEncontrados.add(Cobro(
          item.findElements('Cliente').single.text,
          int.parse(item.findElements('Hidrometro').single.text),
          (DateTime.now().year * 100 + DateTime.now().month),
          int.parse(item.findElements('Monto').single.text), []));

      if (primeraPasada) {
        XmlElement abonosXml = XmlElement(XmlName("Abonos"));
        item.children.add(abonosXml);
        log("se agrego abonos");
      } else {
        final abonos = item.findAllElements('Abono');
        int fecha;
        int monto;
        int tipoPago;
        for (var abono in abonos) {
          abono.getElement("Fecha");
          fecha = int.parse(abono.getElement("Fecha")!.text);
          monto = int.parse(abono.getElement("Monto")!.text);
          tipoPago = int.parse(abono.getElement("TipoPago")!.text);
          cobrosEncontrados.last.agregarDatoAbono(fecha, monto, tipoPago);
        }
      }
    }
    if (primeraPasada) {
      file.writeAsString(document.toXmlString());
    }
    return cobrosEncontrados;
  }

  @override
  Future<bool> crearArchivoCobros(String contenido) async {
    String nombre = getNameForThisMonthsFile();
    try {
      File file =
          await File(cobrofolderPath + '/' + nombre).create(recursive: true);

      await file.writeAsString(contenido);
    } on Exception {
      return false;
    }
    return true;
  }

  @override
  bool eliminarAbono(Cobro c, int index) {
    int medidorPorBuscar = c.getNumeroMedidor();
    String thisMonthsFile = DateFormat('yyyy-MM')
        .format(DateTime.utc(c.getFecha() ~/ 100, c.getFecha() % 100));
    try {
      File file = File(cobrofolderPath + '/' + thisMonthsFile);
      XmlDocument document = XmlDocument.parse(file.readAsStringSync());
      // TODO implementar el acceso directo
      final datos = document.findAllElements('Detalles_Linea');
      for (var item in datos) {
        if (int.parse(item.findElements('Hidrometro').single.text) ==
            medidorPorBuscar) {
          final abonos = item.findElements('Abonos');
          log(abonos.single.children.toString());
          abonos.single.children.removeAt(index);
          break;
        }
      }
      file.writeAsString(document.toXmlString());
      return true;
    } catch (e, s) {
      log("Error: " + e.toString());
      log("StackTrace: \n" + s.toString());
      return false;
    }
  }

  @override
  bool agregarAbono(Cobro c, int monto, int fecha, int tipoPago) {
    int medidorPorBuscar = c.getNumeroMedidor();
    String thisMonthsFile = DateFormat('yyyy-MM')
        .format(DateTime.utc(c.getFecha() ~/ 100, c.getFecha() % 100));

    XmlElement montoXml = XmlElement(XmlName("Monto"));
    montoXml.innerText = monto.toString();
    XmlElement fechaXml = XmlElement(XmlName("Fecha"));
    fechaXml.innerText = fecha.toString();
    XmlElement tipoPagoXml = XmlElement(XmlName("TipoPago"));
    tipoPagoXml.innerText = tipoPago.toString();

    XmlElement nodeToAdd = XmlElement(XmlName("Abono"));
    nodeToAdd.children.addAll([montoXml, fechaXml, tipoPagoXml]);

    try {
      File file = File(cobrofolderPath + '/' + thisMonthsFile);
      XmlDocument document = XmlDocument.parse(file.readAsStringSync());
      // TODO implementar el acceso directo
      final datos = document.findAllElements('Detalles_Linea');
      for (var item in datos) {
        if (int.parse(item.findElements('Hidrometro').single.text) ==
            medidorPorBuscar) {
          final abonos = item.findElements('Abonos');
          //Nodo lista que contiene los abonos individuales
          abonos.single.children.add(nodeToAdd);
          break;
        }
      }
      log(document.toXmlString());
      file.writeAsString(document.toXmlString());
      return true;
    } catch (e, s) {
      log("Error: " + e.toString());
      log("StackTrace: \n" + s.toString());
      return false;
    }
  }
}
