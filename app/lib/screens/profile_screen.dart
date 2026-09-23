import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final nameController = TextEditingController();
  final emailController = TextEditingController();
  final phoneController = TextEditingController();
  final locationController = TextEditingController();

  String? cvPath;
  String? cvFilename;

  bool loadingProfile = true;
  bool savingProfile = false;
  bool uploadingCv = false;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  @override
  void dispose() {
    nameController.dispose();
    emailController.dispose();
    phoneController.dispose();
    locationController.dispose();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    try {
      final user = await ApiService.getUser();

      debugPrint('=== AUTOAI PROFILE LOAD ===');
      debugPrint('USER RESPONSE: $user');
      debugPrint('CV PATH: ${user['cv_path']}');

      if (!mounted) return;

      setState(() {
        nameController.text = user['full_name']?.toString() ?? '';
        emailController.text = user['email']?.toString() ?? '';
        phoneController.text = user['phone']?.toString() ?? '';
        locationController.text = user['location']?.toString() ?? '';

        cvPath = user['cv_path']?.toString();

        if (cvPath != null && cvPath!.isNotEmpty) {
          final pathParts = cvPath!.split('/');
          cvFilename = pathParts.isNotEmpty ? pathParts.last : null;
        }
      });
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not load profile: $e'),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          loadingProfile = false;
        });
      }
    }
  }

  Future<void> _saveProfile() async {
    if (nameController.text.trim().isEmpty ||
        emailController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Name and email are required.'),
        ),
      );
      return;
    }

    setState(() {
      savingProfile = true;
    });

    try {
      final user = await ApiService.updateUser(
        fullName: nameController.text.trim(),
        email: emailController.text.trim(),
        phone: phoneController.text.trim(),
        location: locationController.text.trim(),
      );

      if (!mounted) return;

      setState(() {
        nameController.text = user['full_name']?.toString() ?? '';
        emailController.text = user['email']?.toString() ?? '';
        phoneController.text = user['phone']?.toString() ?? '';
        locationController.text = user['location']?.toString() ?? '';
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Profile saved successfully'),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not save profile: $e'),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          savingProfile = false;
        });
      }
    }
  }

  Future<void> _uploadCv() async {
    final files = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'docx', 'txt'],
    );

    if (files.isEmpty) {
      return;
    }

    final file = files.first;

    setState(() {
      uploadingCv = true;
    });

    try {
      final result = await ApiService.uploadCv(file);

      if (!mounted) return;

      setState(() {
        cvPath = result['cv_path']?.toString();
        cvFilename = result['filename']?.toString() ?? file.name;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('CV uploaded successfully'),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('CV upload failed: $e'),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          uploadingCv = false;
        });
      }
    }
  }

  Widget _field(
    String label,
    TextEditingController controller, {
    TextInputType? keyboardType,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: TextField(
        controller: controller,
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }

  Widget _cvSection() {
    final hasCv = cvPath != null && cvPath!.trim().isNotEmpty;

    String displayedFilename = 'No CV uploaded';

    if (hasCv) {
      displayedFilename = cvPath!.split('/').last;
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'CV / Resume',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  hasCv
                      ? Icons.description
                      : Icons.description_outlined,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    displayedFilename,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: hasCv ? Colors.white : Colors.grey,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: uploadingCv ? null : _uploadCv,
                icon: uploadingCv
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                        ),
                      )
                    : Icon(
                        hasCv
                            ? Icons.sync
                            : Icons.upload_file,
                      ),
                label: Text(
                  uploadingCv
                      ? 'Uploading...'
                      : hasCv
                          ? 'Replace CV'
                          : 'Upload CV',
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
      ),
      body: loadingProfile
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                const Text(
                  'Candidate Profile',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Keep your information and CV ready for autoAI job matching.',
                ),
                const SizedBox(height: 24),

                _field('Full name', nameController),

                _field(
                  'Email',
                  emailController,
                  keyboardType: TextInputType.emailAddress,
                ),

                _field(
                  'Phone',
                  phoneController,
                  keyboardType: TextInputType.phone,
                ),

                _field('Location', locationController),

                const SizedBox(height: 4),

                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: savingProfile ? null : _saveProfile,
                    icon: savingProfile
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          )
                        : const Icon(Icons.save),
                    label: Text(
                      savingProfile ? 'Saving...' : 'Save Profile',
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                _cvSection(),
              ],
            ),
    );
  }
}
