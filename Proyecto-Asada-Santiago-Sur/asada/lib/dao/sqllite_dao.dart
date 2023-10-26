import 'package:asada/dao/dao_usuario.dart';
import 'package:asada/model/user.dart';
import 'package:flutter/widgets.dart';
import 'dart:async';

import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class SqliteDao implements DaoUsuario {
  late final Future<Database> database;

  @override
  Future<User> verificarUsuario(String username, String password) async {
    List<Map<String, Object?>> uList = await users();
    for (var user in uList) {
      if (user['username'] as String == username) {
        if (user['password'] as String == password) {
          return User.from(user);
        }
        return const User(username: "", password: "", type: "NP");
      }
    }
    return const User(username: "", password: "", type: "NU");
  }

  SqliteDao() {
    database = initDatabase();
    //initDatabase().then((db) => database = db);
  }

  Future<Database> initDatabase() async {
    WidgetsFlutterBinding.ensureInitialized();
    // Open the database and store the reference.
    final database = openDatabase(
      // Set the path to the database. Note: Using the `join` function from the
      // `path` package is best practice to ensure the path is correctly
      // constructed for each platform.
      join(await getDatabasesPath(), 'users_database.db'),
      // When the database is first created, create a table to store users.
      onCreate: (db, version) {
        // Run the CREATE TABLE statement on the database.
        db.execute(
          'CREATE TABLE user(username TEXT PRIMARY KEY, password TEXT, type TEXT)',
        );
        db.execute(
          'INSERT INTO user(username, password, type) VALUES("admin2","admin2","C")',
        );
        return db.execute(
          'INSERT INTO user(username, password, type) VALUES("admin","admin","F")',
        );
      },
      // Set the version. This executes the onCreate function and provides a
      // path to perform database upgrades and downgrades.
      version: 1,
    );
    return database;
  }

  @override
  bool agregarUsuario(String username, String password, String type) {
    User usuario = User(username: username, password: password, type: type);
    bool inserted = false;
    _insertUser(usuario).then((value) => {inserted = value != 0});
    return inserted;
  }

  Future<int> _insertUser(User user) async {
    // Get a reference to the database.
    final db = await database;

    return await db.insert(
      'user',
      user.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Map<String, Object?>>> users() async {
    // Get a reference to the database.
    final db = await database;

    Future<List<Map<String, Object?>>> query = db.query('user');
    return query;
    /* Quito esto para ahorrar tiempo de ejecución, para limpiesa de codigo 
       se podria agregar

    // Query the table for all The Users.
    final List<Map<String, dynamic>> maps = await db.query('user');

    // Convert the List<Map<String, dynamic> into a List<User>.
    return List.generate(maps.length, (i) {
      return User(
        username: maps[i]['username'],
        password: maps[i]['password'],
        type: maps[i]['type'],
      );
    });
    */
  }
}
