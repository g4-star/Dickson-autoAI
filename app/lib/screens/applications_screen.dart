import 'package:flutter/material.dart';

class ApplicationsScreen extends StatelessWidget {
  const ApplicationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Applications",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _filterBar(),
          const SizedBox(height: 20),
          _emptyState(),
        ],
      ),
    );
  }

  Widget _filterBar() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.filter_list),
            label: const Text("Filter"),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.sort),
            label: const Text("Sort"),
          ),
        ),
      ],
    );
  }

  Widget _emptyState() {
    return Container(
      padding: const EdgeInsets.symmetric(
        vertical: 70,
        horizontal: 20,
      ),
      decoration: BoxDecoration(
        color: const Color(0xFF11161E),
        borderRadius: BorderRadius.circular(20),
      ),
      child: const Column(
        children: [
          Icon(
            Icons.work_outline,
            size: 55,
            color: Colors.white24,
          ),
          SizedBox(height: 16),
          Text(
            "No applications yet",
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 8),
          Text(
            "Applications submitted by the integrator will appear here.",
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white54,
            ),
          ),
        ],
      ),
    );
  }
}
