import 'package:flutter/material.dart';

import 'screens/automation_screen.dart';
import 'screens/applications_screen.dart';
import 'screens/emails_screen.dart';
import 'screens/settings_screen.dart';

void main() {
  runApp(const AutoAIApp());
}

class AutoAIApp extends StatelessWidget {
  const AutoAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Dickson's autoAI",
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0F14),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6C63FF),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const AutoAIHome(),
    );
  }
}

class AutoAIHome extends StatefulWidget {
  const AutoAIHome({super.key});

  @override
  State<AutoAIHome> createState() => _AutoAIHomeState();
}

class _AutoAIHomeState extends State<AutoAIHome> {
  int index = 0;

  final pages = const [
    DashboardPage(),
    AutomationScreen(),
    ApplicationsScreen(),
    EmailsScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: pages[index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (value) {
          setState(() => index = value);
        },
        backgroundColor: const Color(0xFF10151C),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard),
            label: "Dashboard",
          ),
          NavigationDestination(
            icon: Icon(Icons.smart_toy_outlined),
            selectedIcon: Icon(Icons.smart_toy),
            label: "Automation",
          ),
          NavigationDestination(
            icon: Icon(Icons.work_outline),
            selectedIcon: Icon(Icons.work),
            label: "Applications",
          ),
          NavigationDestination(
            icon: Icon(Icons.email_outlined),
            selectedIcon: Icon(Icons.email),
            label: "Emails",
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: "Settings",
          ),
        ],
      ),
    );
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Dickson's autoAI",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              "Automation control center",
              style: TextStyle(
                fontSize: 12,
                color: Colors.white54,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.notifications_outlined),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _integratorCard(),

          const SizedBox(height: 24),

          const Text(
            "TODAY",
            style: TextStyle(
              color: Colors.white54,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),

          const SizedBox(height: 12),

          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.45,
            children: const [
              StatCard(Icons.search, "Jobs Found", "0"),
              StatCard(Icons.send_outlined, "Applications", "0"),
              StatCard(Icons.check_circle_outline, "Successful", "0"),
              StatCard(Icons.error_outline, "Failed", "0"),
              StatCard(Icons.email_outlined, "Emails", "0"),
              StatCard(Icons.event_available_outlined, "Interviews", "0"),
            ],
          ),

          const SizedBox(height: 28),

          const Text(
            "RECENT ACTIVITY",
            style: TextStyle(
              color: Colors.white54,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),

          const SizedBox(height: 12),

          Container(
            padding: const EdgeInsets.all(35),
            decoration: BoxDecoration(
              color: const Color(0xFF11161E),
              borderRadius: BorderRadius.circular(18),
            ),
            child: const Column(
              children: [
                Icon(
                  Icons.history,
                  size: 42,
                  color: Colors.white24,
                ),
                SizedBox(height: 12),
                Text(
                  "No activity yet",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 5),
                Text(
                  "Integrator activity will appear here.",
                  style: TextStyle(color: Colors.white54),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _integratorCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF171D29),
        borderRadius: BorderRadius.circular(20),
      ),
      child: const Row(
        children: [
          Icon(
            Icons.smart_toy,
            size: 42,
            color: Colors.greenAccent,
          ),
          SizedBox(width: 14),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Integrator",
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 5),
              Row(
                children: [
                  Icon(
                    Icons.circle,
                    size: 9,
                    color: Colors.greenAccent,
                  ),
                  SizedBox(width: 6),
                  Text(
                    "Online",
                    style: TextStyle(
                      color: Colors.greenAccent,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class StatCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;

  const StatCard(
    this.icon,
    this.title,
    this.value, {
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: const Color(0xFF11161E),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.white70),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}
