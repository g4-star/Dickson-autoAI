import 'package:flutter/material.dart';

import '../services/api_service.dart';

class JobPreferencesScreen extends StatefulWidget {
  const JobPreferencesScreen({super.key});

  @override
  State<JobPreferencesScreen> createState() =>
      _JobPreferencesScreenState();
}

class _JobPreferencesScreenState
    extends State<JobPreferencesScreen> {
  final rolesController = TextEditingController();
  final salaryController = TextEditingController();

  String workPreference = 'Remote';

  bool loading = true;
  bool saving = false;

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  @override
  void dispose() {
    rolesController.dispose();
    salaryController.dispose();
    super.dispose();
  }

  Future<void> _loadPreferences() async {
    try {
      final user = await ApiService.getUser();

      if (!mounted) return;

      setState(() {
        rolesController.text =
            user['preferred_roles']?.toString() ?? '';

        salaryController.text =
            user['salary_preference']?.toString() ?? '';

        final savedWork =
            user['work_preference']?.toString();

        if (savedWork != null &&
            ['Remote', 'On-site', 'Hybrid']
                .contains(savedWork)) {
          workPreference = savedWork;
        }
      });
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not load job preferences: $e'),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          loading = false;
        });
      }
    }
  }

  Future<void> _savePreferences() async {
    setState(() {
      saving = true;
    });

    try {
      await ApiService.updateUser(
        preferredRoles: rolesController.text.trim(),
        workPreference: workPreference,
        salaryPreference: salaryController.text.trim(),
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Job preferences saved successfully'),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not save preferences: $e'),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          saving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Preferences'),
      ),
      body: loading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                const Text(
                  'What are you looking for?',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 8),

                const Text(
                  'These preferences help autoAI find and evaluate jobs that match you.',
                ),

                const SizedBox(height: 28),

                TextField(
                  controller: rolesController,
                  decoration: const InputDecoration(
                    labelText: 'Preferred roles',
                    hintText:
                        'e.g. SOC Analyst, Cybersecurity Analyst, Pentester',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.work_outline),
                  ),
                  maxLines: 3,
                ),

                const SizedBox(height: 20),

                const Text(
                  'Work preference',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 8),

                DropdownButtonFormField<String>(
                  initialValue: workPreference,
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.location_on_outlined),
                  ),
                  items: const [
                    DropdownMenuItem(
                      value: 'Remote',
                      child: Text('Remote'),
                    ),
                    DropdownMenuItem(
                      value: 'On-site',
                      child: Text('On-site'),
                    ),
                    DropdownMenuItem(
                      value: 'Hybrid',
                      child: Text('Hybrid'),
                    ),
                  ],
                  onChanged: (value) {
                    if (value == null) return;

                    setState(() {
                      workPreference = value;
                    });
                  },
                ),

                const SizedBox(height: 20),

                TextField(
                  controller: salaryController,
                  keyboardType: TextInputType.text,
                  decoration: const InputDecoration(
                    labelText: 'Salary preference',
                    hintText: 'e.g. KSh 50,000+ or Negotiable',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.payments_outlined),
                  ),
                ),

                const SizedBox(height: 28),

                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: saving ? null : _savePreferences,
                    icon: saving
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          )
                        : const Icon(Icons.save),
                    label: Text(
                      saving
                          ? 'Saving...'
                          : 'Save Preferences',
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}
