import 'package:flutter/material.dart';

class ChangeEmailScreen extends StatefulWidget {
  const ChangeEmailScreen({super.key});

  @override
  State<ChangeEmailScreen> createState() => _ChangeEmailScreenState();
}

class _ChangeEmailScreenState extends State<ChangeEmailScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  bool loading = false;

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  Future<void> changeEmail() async {
    if (emailController.text.trim().isEmpty ||
        passwordController.text.isEmpty) {
      return;
    }

    setState(() => loading = true);

    await Future.delayed(const Duration(milliseconds: 700));

    if (!mounted) return;

    setState(() => loading = false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          "Email change request submitted",
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Change Email",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFF171D29),
              borderRadius: BorderRadius.circular(18),
            ),
            child: const Row(
              children: [
                Icon(
                  Icons.security_outlined,
                  color: Colors.greenAccent,
                  size: 30,
                ),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    "Changing your account email may require verification.",
                    style: TextStyle(
                      color: Colors.white70,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          TextField(
            controller: emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: InputDecoration(
              labelText: "New email address",
              prefixIcon: const Icon(Icons.email_outlined),
              filled: true,
              fillColor: const Color(0xFF11161E),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: BorderSide.none,
              ),
            ),
          ),

          const SizedBox(height: 14),

          TextField(
            controller: passwordController,
            obscureText: true,
            decoration: InputDecoration(
              labelText: "Current password",
              prefixIcon: const Icon(Icons.lock_outline),
              filled: true,
              fillColor: const Color(0xFF11161E),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: BorderSide.none,
              ),
            ),
          ),

          const SizedBox(height: 24),

          FilledButton(
            onPressed: loading ? null : changeEmail,
            child: Padding(
              padding: const EdgeInsets.all(13),
              child: loading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                      ),
                    )
                  : const Text("Change Email"),
            ),
          ),
        ],
      ),
    );
  }
}
