import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000';
  static const int userId = 1;

  static Future<Map<String, dynamic>> getUser() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/users/$userId'),
    );

    Map<String, dynamic> data = {};

    if (response.body.isNotEmpty) {
      data = jsonDecode(response.body) as Map<String, dynamic>;
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(
        data['detail']?.toString() ??
            'Failed to load profile (${response.statusCode}).',
      );
    }

    return data;
  }


  static Future<List<dynamic>> getEmails({
    int limit = 50,
  }) async {
    final response = await http.get(
      Uri.parse(
        '$baseUrl/api/users/$userId/emails?limit=$limit',
      ),
    );

    if (response.statusCode != 200) {
      throw Exception(
        'Failed to load emails: ${response.statusCode}',
      );
    }

    final decoded = jsonDecode(response.body);

    if (decoded is! List) {
      throw Exception('Invalid email response.');
    }

    return decoded;
  }

  static Future<Map<String, dynamic>> updateUser({
    String? fullName,
    String? email,
    String? phone,
    String? location,
    String? preferredRoles,
    String? workPreference,
    String? salaryPreference,
  }) async {
    final Map<String, dynamic> body = {};

    if (fullName != null) {
      body['full_name'] = fullName;
    }

    if (email != null) {
      body['email'] = email;
    }

    if (phone != null) {
      body['phone'] = phone;
    }

    if (location != null) {
      body['location'] = location;
    }

    if (preferredRoles != null) {
      body['preferred_roles'] = preferredRoles;
    }

    if (workPreference != null) {
      body['work_preference'] = workPreference;
    }

    if (salaryPreference != null) {
      body['salary_preference'] = salaryPreference;
    }

    final response = await http.patch(
      Uri.parse('$baseUrl/api/users/$userId'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode(body),
    );

    Map<String, dynamic> data = {};

    if (response.body.isNotEmpty) {
      data = jsonDecode(response.body) as Map<String, dynamic>;
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(
        data['detail']?.toString() ??
            'Failed to save user (${response.statusCode}).',
      );
    }

    return data;
  }

  static Future<Map<String, dynamic>> uploadCv(
    PlatformFile file,
  ) async {
    if (file.path == null) {
      throw Exception('Unable to access the selected file.');
    }

    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/users/$userId/cv'),
    );

    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        file.path!,
        filename: file.name,
      ),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    Map<String, dynamic> data = {};

    if (response.body.isNotEmpty) {
      try {
        data = jsonDecode(response.body) as Map<String, dynamic>;
      } catch (_) {
        throw Exception(
          'Server returned an invalid response (${response.statusCode}).',
        );
      }
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(
        data['detail']?.toString() ??
            'CV upload failed (${response.statusCode}).',
      );
    }

    return data;
  }
}
