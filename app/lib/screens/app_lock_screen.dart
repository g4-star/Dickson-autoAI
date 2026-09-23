import 'package:flutter/material.dart';

import '../services/auth_service.dart';

class AppLockScreen extends StatefulWidget {
  const AppLockScreen({
    super.key,
    required this.onAuthenticated,
  });

  final VoidCallback onAuthenticated;

  @override
  State<AppLockScreen> createState() => _AppLockScreenState();
}

class _AppLockScreenState extends State<AppLockScreen> {
  final AuthService _authService = AuthService();
  final TextEditingController _controller = TextEditingController();

  bool _loading = false;
  bool _obscureText = true;
  String _method = 'PIN';
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    final value = _controller.text.trim();

    if (value.isEmpty) {
      setState(() => _error = 'Enter your $_method.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    bool authenticated = false;

    if (_method == 'PIN') {
      authenticated = await _authService.verifyPin(value);
    } else {
      authenticated = await _authService.verifyPassword(value);
    }

    if (!mounted) return;

    setState(() {
      _loading = false;
    });

    if (authenticated) {
      widget.onAuthenticated();
    } else {
      setState(() {
        _error = 'Incorrect $_method.';
        _controller.clear();
      });
    }
  }

  Future<void> _biometric() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    final authenticated =
        await _authService.authenticateWithBiometrics();

    if (!mounted) return;

    setState(() {
      _loading = false;
    });

    if (authenticated) {
      widget.onAuthenticated();
    } else {
      setState(() {
        _error = 'Biometric authentication failed.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0F14),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(28),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                children: [
                  Container(
                    width: 82,
                    height: 82,
                    decoration: BoxDecoration(
                      color: const Color(0xFF171D29),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: const Icon(
                      Icons.lock_outline,
                      size: 42,
                      color: Color(0xFF6C63FF),
                    ),
                  ),

                  const SizedBox(height: 24),

                  const Text(
                    "Dickson's autoAI",
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: 8),

                  const Text(
                    'App locked',
                    style: TextStyle(
                      color: Colors.white54,
                      fontSize: 15,
                    ),
                  ),

                  const SizedBox(height: 32),

                  SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(
                        value: 'PIN',
                        label: Text('PIN'),
                        icon: Icon(Icons.pin_outlined),
                      ),
                      ButtonSegment(
                        value: 'PASSWORD',
                        label: Text('Password'),
                        icon: Icon(Icons.password_outlined),
                      ),
                    ],
                    selected: {_method},
                    onSelectionChanged: (selection) {
                      setState(() {
                        _method = selection.first;
                        _controller.clear();
                        _error = null;
                      });
                    },
                  ),

                  const SizedBox(height: 22),

                  TextField(
                    controller: _controller,
                    obscureText: _obscureText,
                    keyboardType: _method == 'PIN'
                        ? TextInputType.number
                        : TextInputType.text,
                    decoration: InputDecoration(
                      labelText: _method,
                      prefixIcon: Icon(
                        _method == 'PIN'
                            ? Icons.pin_outlined
                            : Icons.password_outlined,
                      ),
                      suffixIcon: IconButton(
                        onPressed: () {
                          setState(() {
                            _obscureText = !_obscureText;
                          });
                        },
                        icon: Icon(
                          _obscureText
                              ? Icons.visibility_outlined
                              : Icons.visibility_off_outlined,
                        ),
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    onSubmitted: (_) => _verify(),
                  ),

                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _error!,
                      style: const TextStyle(
                        color: Colors.redAccent,
                      ),
                    ),
                  ],

                  const SizedBox(height: 22),

                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: FilledButton(
                      onPressed: _loading ? null : _verify,
                      child: _loading
                          ? const SizedBox(
                              width: 22,
                              height: 22,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                              ),
                            )
                          : Text('Unlock with $_method'),
                    ),
                  ),

                  const SizedBox(height: 14),

                  FutureBuilder<bool>(
                    future: _authService.canUseBiometrics(),
                    builder: (context, snapshot) {
                      if (snapshot.data != true) {
                        return const SizedBox.shrink();
                      }

                      return OutlinedButton.icon(
                        onPressed: _loading ? null : _biometric,
                        icon: const Icon(Icons.fingerprint),
                        label: const Text('Use fingerprint / biometric'),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
