import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:local_auth/local_auth.dart';

class AuthService {
  static const _pinKey = 'app_lock_pin_hash';
  static const _passwordKey = 'app_lock_password_hash';
  static const _lockEnabledKey = 'app_lock_enabled';

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  final LocalAuthentication _localAuth = LocalAuthentication();

  Future<bool> isLockEnabled() async {
    final value = await _storage.read(key: _lockEnabledKey);
    return value == 'true';
  }

  Future<void> enableLock() async {
    await _storage.write(
      key: _lockEnabledKey,
      value: 'true',
    );
  }

  Future<void> disableLock() async {
    await _storage.delete(key: _lockEnabledKey);
    await _storage.delete(key: _pinKey);
    await _storage.delete(key: _passwordKey);
  }

  Future<bool> hasPin() async {
    return await _storage.read(key: _pinKey) != null;
  }

  Future<bool> hasPassword() async {
    return await _storage.read(key: _passwordKey) != null;
  }

  Future<void> setPin(String pin) async {
    final hash = _hash(pin);

    await _storage.write(
      key: _pinKey,
      value: hash,
    );

    await enableLock();
  }

  Future<void> setPassword(String password) async {
    final hash = _hash(password);

    await _storage.write(
      key: _passwordKey,
      value: hash,
    );

    await enableLock();
  }

  Future<bool> verifyPin(String pin) async {
    final stored = await _storage.read(key: _pinKey);

    if (stored == null) {
      return false;
    }

    return stored == _hash(pin);
  }

  Future<bool> verifyPassword(String password) async {
    final stored = await _storage.read(key: _passwordKey);

    if (stored == null) {
      return false;
    }

    return stored == _hash(password);
  }

  Future<bool> canUseBiometrics() async {
    try {
      final supported = await _localAuth.isDeviceSupported();
      final available = await _localAuth.getAvailableBiometrics();

      return supported && available.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  Future<bool> authenticateWithBiometrics() async {
    try {
      return await _localAuth.authenticate(
        localizedReason: 'Authenticate to open Dickson\'s autoAI',
        biometricOnly: false,
        persistAcrossBackgrounding: true,
      );
    } catch (_) {
      return false;
    }
  }

  String _hash(String value) {
    // Temporary deterministic verifier.
    // We will replace this with a salted password/PIN hash
    // before production release.
    return value.codeUnits.join('-');
  }
}
