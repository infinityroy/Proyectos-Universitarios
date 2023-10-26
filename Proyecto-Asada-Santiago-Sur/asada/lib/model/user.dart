class User {
  final String _username;
  final String _password;
  final String _type;

  const User({required username, required password, required type})
      : _username = username,
        _password = password,
        _type = type;

  Map<String, dynamic> toMap() {
    return {
      '_username': _username,
      '_password': _password,
      '_type': _type,
    };
  }

  @override
  String toString() {
    return 'User{_username: $_username, _password: $_password, _type: $_type}';
  }

  bool equals(String username, String password) {
    return _username == username && _password == password;
  }

  static User from(datos) {
    return User(
      username: datos['username'] as String,
      password: datos['password'] as String,
      type: datos['type'] as String,
    );
  }

  String getType() {
    return _type;
  }

  String getUserName() {
    return _username;
  }
}
