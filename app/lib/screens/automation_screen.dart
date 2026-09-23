import 'package:flutter/material.dart';

class AutomationScreen extends StatefulWidget {
  const AutomationScreen({super.key});

  @override
  State<AutomationScreen> createState() => _AutomationScreenState();
}

class _AutomationScreenState extends State<AutomationScreen> {
  bool autoApply = false;
  bool autoReply = false;
  bool jobSearch = true;
  bool emailMonitoring = true;
  bool notifications = true;

  int dailyTarget = 50;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Automation",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _statusCard(),

          const SizedBox(height: 24),

          const Text(
            "AUTOMATION CONTROLS",
            style: TextStyle(
              color: Colors.white54,
              fontSize: 13,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),

          const SizedBox(height: 10),

          _switchTile(
            icon: Icons.search,
            title: "Job Search",
            subtitle: "Continuously search configured job sources",
            value: jobSearch,
            onChanged: (v) => setState(() => jobSearch = v),
          ),

          _switchTile(
            icon: Icons.send_outlined,
            title: "Auto-Apply",
            subtitle: "Automatically submit suitable applications",
            value: autoApply,
            onChanged: (v) => setState(() => autoApply = v),
          ),

          _switchTile(
            icon: Icons.email_outlined,
            title: "Email Monitoring",
            subtitle: "Monitor connected email for job activity",
            value: emailMonitoring,
            onChanged: (v) => setState(() => emailMonitoring = v),
          ),

          _switchTile(
            icon: Icons.reply_outlined,
            title: "Auto-Reply",
            subtitle: "Automatically respond to configured emails",
            value: autoReply,
            onChanged: (v) => setState(() => autoReply = v),
          ),

          _switchTile(
            icon: Icons.notifications_outlined,
            title: "Notifications",
            subtitle: "Receive automation activity notifications",
            value: notifications,
            onChanged: (v) => setState(() => notifications = v),
          ),

          const SizedBox(height: 24),

          const Text(
            "APPLICATION LIMIT",
            style: TextStyle(
              color: Colors.white54,
              fontSize: 13,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),

          const SizedBox(height: 10),

          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFF11161E),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text("Daily application target"),
                    Text(
                      "$dailyTarget",
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Slider(
                  value: dailyTarget.toDouble(),
                  min: 0,
                  max: 100,
                  divisions: 20,
                  label: "$dailyTarget",
                  onChanged: (value) {
                    setState(() {
                      dailyTarget = value.round();
                    });
                  },
                ),
                const Text(
                  "The integrator should only apply when a job genuinely matches your profile.",
                  style: TextStyle(
                    color: Colors.white54,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          const Text(
            "SAFETY",
            style: TextStyle(
              color: Colors.white54,
              fontSize: 13,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),

          const SizedBox(height: 10),

          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFF11161E),
              borderRadius: BorderRadius.circular(18),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.shield_outlined,
                      color: Colors.greenAccent,
                    ),
                    SizedBox(width: 10),
                    Text(
                      "Human approval",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 12),
                Text(
                  "Important actions such as accepting interviews, negotiating offers, or withdrawing applications can require your approval.",
                  style: TextStyle(
                    color: Colors.white60,
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _statusCard() {
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

  Widget _switchTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF11161E),
        borderRadius: BorderRadius.circular(18),
      ),
      child: SwitchListTile(
        secondary: Icon(icon),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          subtitle,
          style: const TextStyle(
            color: Colors.white54,
            fontSize: 12,
          ),
        ),
        value: value,
        onChanged: onChanged,
      ),
    );
  }
}
