import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

import '../services/api_service.dart';

class CvDocumentsScreen extends StatefulWidget {
  const CvDocumentsScreen({super.key});

  @override
  State<CvDocumentsScreen> createState() => _CvDocumentsScreenState();
}

class _CvDocumentsScreenState extends State<CvDocumentsScreen> {
  bool loading = true;
  bool uploading = false;

  String? cvPath;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  Future<void> _loadDocuments() async {
    setState(() {
      loading = true;
      errorMessage = null;
    });

    try {
      final user = await ApiService.getUser();

      if (!mounted) return;

      setState(() {
        cvPath = user['cv_path']?.toString();
        loading = false;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        loading = false;
        errorMessage = 'Could not load your CV.';
      });
    }
  }

  Future<void> _uploadCv() async {
    if (uploading) return;

    try {
      final files = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'docx', 'txt'],
      );

      if (files.isEmpty) {
        return;
      }

      final filePath = files.first.path;

      if (filePath == null || filePath.isEmpty) {
        return;
      }

      setState(() {
        uploading = true;
        errorMessage = null;
      });

      final response = await ApiService.uploadCv(files.first);

      if (!mounted) return;

      setState(() {
        cvPath = response['cv_path']?.toString() ?? filePath;
        uploading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('CV uploaded successfully.'),
        ),
      );
    } catch (_) {
      if (!mounted) return;

      setState(() {
        uploading = false;
        errorMessage = 'CV upload failed. Please try again.';
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Could not upload CV.'),
        ),
      );
    }
  }

  String _fileName(String? path) {
    if (path == null || path.isEmpty) {
      return 'No CV uploaded';
    }

    final normalized = path.replaceAll('\\', '/');
    return normalized.split('/').last;
  }

  String _fileType(String? path) {
    if (path == null || path.isEmpty) {
      return '';
    }

    final name = _fileName(path).toLowerCase();

    if (name.endsWith('.pdf')) return 'PDF';
    if (name.endsWith('.docx')) return 'DOCX';
    if (name.endsWith('.txt')) return 'TXT';

    return 'Document';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CV & Documents'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadDocuments,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          children: [
            const Text(
              'Your CV',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Your CV is used by AutoAI when matching you with relevant jobs and preparing applications.',
            ),
            const SizedBox(height: 20),

            if (loading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (cvPath == null || cvPath!.isEmpty)
              _buildEmptyCvCard()
            else
              _buildCvCard(),

            const SizedBox(height: 24),

            const Text(
              'CV status',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),

            _buildStatusCard(),

            const SizedBox(height: 24),

            const Text(
              'What AutoAI uses your CV for',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),

            _buildFeature(
              Icons.search,
              'Job matching',
              'Compare your CV with available jobs.',
            ),
            _buildFeature(
              Icons.work_outline,
              'Relevant roles',
              'Identify jobs that match your skills and preferences.',
            ),
            _buildFeature(
              Icons.send_outlined,
              'Applications',
              'Use your CV when preparing job applications.',
            ),
            _buildFeature(
              Icons.auto_awesome_outlined,
              'AutoAI',
              'Use your CV as part of the automated job workflow.',
            ),

            const SizedBox(height: 24),

            const Text(
              'Other documents',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),

            Card(
              child: ListTile(
                leading: const Icon(Icons.description_outlined),
                title: const Text('Additional documents'),
                subtitle: const Text(
                  'Additional document management will be added here.',
                ),
                trailing: const Icon(Icons.chevron_right),
              ),
            ),

            const SizedBox(height: 12),

            const Text(
              'Supported CV formats: PDF, DOCX and TXT.',
              style: TextStyle(color: Colors.grey),
            ),

            if (errorMessage != null) ...[
              const SizedBox(height: 20),
              Text(
                errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyCvCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Icon(
              Icons.picture_as_pdf_outlined,
              size: 56,
            ),
            const SizedBox(height: 12),
            const Text(
              'No CV uploaded',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Upload your CV so AutoAI can use it for job matching.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: uploading ? null : _uploadCv,
              icon: const Icon(Icons.upload_file),
              label: Text(
                uploading ? 'Uploading...' : 'Upload CV',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCvCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                const CircleAvatar(
                  child: Icon(Icons.description_outlined),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _fileName(cvPath),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _fileType(cvPath),
                        style: const TextStyle(
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Icon(
                  Icons.check_circle,
                  size: 20,
                ),
                SizedBox(width: 8),
                Text(
                  'Ready for AutoAI',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: uploading ? null : _uploadCv,
                icon: const Icon(Icons.sync),
                label: Text(
                  uploading ? 'Uploading...' : 'Replace CV',
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard() {
    final hasCv = cvPath != null && cvPath!.isNotEmpty;

    return Card(
      child: ListTile(
        leading: Icon(
          hasCv
              ? Icons.check_circle
              : Icons.warning_amber_rounded,
        ),
        title: Text(
          hasCv ? 'CV ready' : 'CV required',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          hasCv
              ? 'AutoAI can use your CV for job matching.'
              : 'Upload a CV before starting automated applications.',
        ),
      ),
    );
  }

  Widget _buildFeature(
    IconData icon,
    String title,
    String description,
  ) {
    return Card(
      child: ListTile(
        leading: Icon(icon),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Text(description),
      ),
    );
  }
}
