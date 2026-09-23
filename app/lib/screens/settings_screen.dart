import 'package:flutter/material.dart';

import 'change_email_screen.dart';
import 'job_preferences_screen.dart';
import 'profile_screen.dart';
import 'cv_documents_screen.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Settings",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView(
        children: [
          _section("ACCOUNT"),

          _tile(
            context,
            Icons.person_outline,
            "Profile",
            "Your CV, skills and job preferences",
            const ProfileScreen(),
          ),

          _tile(
            context,
            Icons.email_outlined,
            "Change email",
            "Change the email used by autoAI",
            const ChangeEmailScreen(),
          ),

          _section("APPLICATION"),

          _tile(
            context,
            Icons.description_outlined,
            "CV & documents",
            "Manage your CV and application documents",
            const CvDocumentsScreen(),
          ),

          _tile(
            context,
            Icons.work_outline,
            "Job preferences",
            "Roles, locations and work preferences",
            const JobPreferencesScreen(),
          ),

          _section("INTEGRATOR"),

          _tile(
            context,
            Icons.link,
            "Integrations",
            "Email and supported job sources",
            null,
          ),

          _tile(
            context,
            Icons.notifications_outlined,
            "Notifications",
            "Control automation notifications",
            null,
          ),

          _section("SECURITY"),

          _tile(
            context,
            Icons.security_outlined,
            "Security",
            "Authentication and account security",
            null,
          ),

          _tile(
            context,
            Icons.info_outline,
            "About",
            "Dickson's autoAI",
            null,
          ),
        ],
      ),
    );
  }

  Widget _section(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        title,
        style: const TextStyle(
          color: Colors.white54,
          fontSize: 12,
          fontWeight: FontWeight.bold,
          letterSpacing: 1.2,
        ),
      ),
    );
  }

  Widget _tile(
    BuildContext context,
    IconData icon,
    String title,
    String subtitle,
    Widget? page,
  ) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(
        subtitle,
        style: const TextStyle(
          color: Colors.white54,
        ),
      ),
      trailing: const Icon(
        Icons.chevron_right,
        color: Colors.white38,
      ),
      onTap: page == null
          ? () {}
          : () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => page,
                ),
              );
            },
    );
  }
}
