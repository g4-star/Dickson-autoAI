import 'package:flutter/material.dart';

import '../services/api_service.dart';

class EmailsScreen extends StatefulWidget {
  const EmailsScreen({super.key});

  @override
  State<EmailsScreen> createState() => _EmailsScreenState();
}

class _EmailsScreenState extends State<EmailsScreen> {
  List<dynamic> emails = [];

  bool loading = true;
  String? errorMessage;

  String selectedFolder = 'Inbox';
  String selectedTab = 'Primary';
  String searchQuery = '';

  final TextEditingController searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadEmails();
  }

  @override
  void dispose() {
    searchController.dispose();
    super.dispose();
  }

  Future<void> _loadEmails() async {
    if (!mounted) return;

    setState(() {
      loading = true;
      errorMessage = null;
    });

    try {
      final result = await ApiService.getEmails(limit: 50);

      if (!mounted) return;

      setState(() {
        emails = result;
        loading = false;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        loading = false;
        errorMessage = 'Could not load emails. Check your connection.';
      });
    }
  }

  String _sender(dynamic email) {
    return email['sender']?.toString() ??
        email['from']?.toString() ??
        email['sender_email']?.toString() ??
        'Unknown sender';
  }

  String _subject(dynamic email) {
    final subject = email['subject']?.toString();

    if (subject == null || subject.trim().isEmpty) {
      return '(No subject)';
    }

    return subject;
  }

  String _body(dynamic email) {
    return email['body']?.toString() ??
        email['body_text']?.toString() ??
        email['snippet']?.toString() ??
        '';
  }

  String _category(dynamic email) {
    final category = email['category']?.toString();

    if (category == null || category.isEmpty) {
      return 'email';
    }

    return category;
  }

  String _formatDate(dynamic email) {
    final raw =
        email['received_at']?.toString() ??
        email['created_at']?.toString();

    if (raw == null || raw.isEmpty) {
      return '';
    }

    try {
      final date = DateTime.parse(raw).toLocal();
      final now = DateTime.now();

      if (date.year == now.year &&
          date.month == now.month &&
          date.day == now.day) {
        final hour = date.hour % 12 == 0 ? 12 : date.hour % 12;
        final minute = date.minute.toString().padLeft(2, '0');
        final period = date.hour >= 12 ? 'PM' : 'AM';

        return '$hour:$minute $period';
      }

      final yesterday = now.subtract(const Duration(days: 1));

      if (date.year == yesterday.year &&
          date.month == yesterday.month &&
          date.day == yesterday.day) {
        return 'Yesterday';
      }

      return '${date.day}/${date.month}/${date.year}';
    } catch (_) {
      return raw;
    }
  }

  List<dynamic> get filteredEmails {
    var result = List<dynamic>.from(emails);

    final query = searchQuery.trim().toLowerCase();

    if (query.isNotEmpty) {
      result = result.where((email) {
        final sender = _sender(email).toLowerCase();
        final subject = _subject(email).toLowerCase();
        final body = _body(email).toLowerCase();

        return sender.contains(query) ||
            subject.contains(query) ||
            body.contains(query);
      }).toList();
    }

    if (selectedFolder == 'Jobs') {
      result = result.where((email) {
        final category = _category(email).toLowerCase();
        return category.contains('job') ||
            category.contains('recruiter');
      }).toList();
    }

    if (selectedFolder == 'School') {
      result = result.where((email) {
        final category = _category(email).toLowerCase();
        return category.contains('school') ||
            category.contains('class');
      }).toList();
    }

    if (selectedFolder == 'Spam') {
      result = result.where((email) {
        final category = _category(email).toLowerCase();
        return category.contains('spam') ||
            category.contains('irrelevant');
      }).toList();
    }

    if (selectedFolder == 'Starred') {
      result = result.where((email) {
        return email['starred'] == true;
      }).toList();
    }

    if (selectedTab == 'Promotions') {
      result = result.where((email) {
        final category = _category(email).toLowerCase();
        return category.contains('promotion') ||
            category.contains('newsletter');
      }).toList();
    }

    if (selectedTab == 'Social') {
      result = result.where((email) {
        final category = _category(email).toLowerCase();
        return category.contains('social');
      }).toList();
    }

    if (selectedTab == 'Updates') {
      result = result.where((email) {
        final category = _category(email).toLowerCase();
        return category.contains('notification') ||
            category.contains('update') ||
            category.contains('service');
      }).toList();
    }

    if (selectedTab == 'Forums') {
      result = result.where((email) {
        final category = _category(email).toLowerCase();
        return category.contains('forum');
      }).toList();
    }

    return result;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: _buildDrawer(),
      appBar: AppBar(
        titleSpacing: 0,
        title: const Text(
          'Emails',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            onPressed: loading ? null : _loadEmails,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchBar(),
          _buildTabs(),
          Expanded(
            child: _buildEmailBody(),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      child: TextField(
        controller: searchController,
        onChanged: (value) {
          setState(() {
            searchQuery = value;
          });
        },
        decoration: InputDecoration(
          hintText: 'Search mail',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: searchQuery.isNotEmpty
              ? IconButton(
                  onPressed: () {
                    searchController.clear();
                    setState(() {
                      searchQuery = '';
                    });
                  },
                  icon: const Icon(Icons.clear),
                )
              : null,
          filled: true,
          fillColor: const Color(0xFF171D26),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
        ),
      ),
    );
  }

  Widget _buildTabs() {
    const tabs = [
      'Primary',
      'Promotions',
      'Social',
      'Updates',
      'Forums',
    ];

    return SizedBox(
      height: 48,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        itemCount: tabs.length,
        itemBuilder: (context, index) {
          final tab = tabs[index];
          final selected = selectedTab == tab;

          return Padding(
            padding: const EdgeInsets.only(right: 6),
            child: ChoiceChip(
              label: Text(tab),
              selected: selected,
              onSelected: (_) {
                setState(() {
                  selectedTab = tab;
                });
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildEmailBody() {
    if (loading && emails.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (errorMessage != null && emails.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          const SizedBox(height: 100),
          const Icon(
            Icons.cloud_off_outlined,
            size: 60,
            color: Colors.white24,
          ),
          const SizedBox(height: 18),
          Text(
            errorMessage!,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white54,
            ),
          ),
          const SizedBox(height: 18),
          Center(
            child: ElevatedButton.icon(
              onPressed: _loadEmails,
              icon: const Icon(Icons.refresh),
              label: const Text('Try again'),
            ),
          ),
        ],
      );
    }

    final visibleEmails = filteredEmails;

    if (visibleEmails.isEmpty) {
      return RefreshIndicator(
        onRefresh: _loadEmails,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: [
            const SizedBox(height: 100),
            const Icon(
              Icons.inbox_outlined,
              size: 60,
              color: Colors.white24,
            ),
            const SizedBox(height: 18),
            Text(
              searchQuery.isNotEmpty
                  ? 'No matching emails'
                  : 'No emails in $selectedFolder',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Pull down to refresh your mailbox.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white54,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadEmails,
      child: ListView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.only(bottom: 20),
        itemCount: visibleEmails.length,
        itemBuilder: (context, index) {
          return _buildEmailTile(visibleEmails[index]);
        },
      ),
    );
  }

  Widget _buildEmailTile(dynamic email) {
    final sender = _sender(email);
    final subject = _subject(email);
    final body = _body(email);
    final date = _formatDate(email);
    final category = _category(email);

    final needsReply = email['needs_reply'] == true;
    final replied = email['replied'] == true;
    final starred = email['starred'] == true;

    return InkWell(
      onTap: () => _openEmail(email),
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 11,
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              radius: 22,
              child: Text(
                sender.isNotEmpty
                    ? sender[0].toUpperCase()
                    : '?',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            const SizedBox(width: 12),

            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          sender,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      if (date.isNotEmpty)
                        Text(
                          date,
                          style: const TextStyle(
                            color: Colors.white54,
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),

                  const SizedBox(height: 4),

                  Text(
                    subject,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                    ),
                  ),

                  if (body.isNotEmpty) ...[
                    const SizedBox(height: 3),
                    Text(
                      body.replaceAll(RegExp(r'\s+'), ' ').trim(),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Colors.white54,
                        fontSize: 13,
                      ),
                    ),
                  ],

                  const SizedBox(height: 6),

                  Wrap(
                    spacing: 5,
                    runSpacing: 4,
                    children: [
                      _badge(category),

                      if (needsReply)
                        _badge(
                          'Needs reply',
                          color: Colors.orangeAccent,
                        ),

                      if (replied)
                        _badge(
                          'Replied',
                          color: Colors.greenAccent,
                        ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(width: 4),

            Icon(
              starred
                  ? Icons.star
                  : Icons.star_border,
              size: 20,
              color: starred
                  ? Colors.amber
                  : Colors.white38,
            ),
          ],
        ),
      ),
    );
  }

  Widget _badge(
    String text, {
    Color? color,
  }) {
    final badgeColor = color ?? Colors.white54;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 7,
        vertical: 3,
      ),
      decoration: BoxDecoration(
        color: badgeColor.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(7),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: badgeColor,
          fontSize: 10,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Drawer _buildDrawer() {
    return Drawer(
      child: SafeArea(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const Padding(
              padding: EdgeInsets.fromLTRB(20, 20, 20, 18),
              child: Row(
                children: [
                  Icon(
                    Icons.mail_rounded,
                    size: 30,
                  ),
                  SizedBox(width: 12),
                  Text(
                    'Mail',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),

            _drawerItem(
              Icons.inbox_outlined,
              'Inbox',
              'Inbox',
            ),

            _drawerItem(
              Icons.star_border,
              'Starred',
              'Starred',
            ),

            _drawerItem(
              Icons.schedule_outlined,
              'Snoozed',
              'Snoozed',
            ),

            _drawerItem(
              Icons.send_outlined,
              'Sent',
              'Sent',
            ),

            _drawerItem(
              Icons.drafts_outlined,
              'Drafts',
              'Drafts',
            ),

            _drawerItem(
              Icons.all_inbox_outlined,
              'All Mail',
              'All Mail',
            ),

            const Divider(),

            const Padding(
              padding: EdgeInsets.fromLTRB(20, 12, 20, 6),
              child: Text(
                'AUTOAI',
                style: TextStyle(
                  color: Colors.white54,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            _drawerItem(
              Icons.work_outline,
              'Jobs / Recruiters',
              'Jobs',
            ),

            _drawerItem(
              Icons.school_outlined,
              'School / Class',
              'School',
            ),

            _drawerItem(
              Icons.person_outline,
              'Personal',
              'Personal',
            ),

            _drawerItem(
              Icons.notifications_none,
              'Notifications',
              'Notifications',
            ),

            const Divider(),

            _drawerItem(
              Icons.report_gmailerrorred_outlined,
              'Spam',
              'Spam',
            ),

            _drawerItem(
              Icons.delete_outline,
              'Trash',
              'Trash',
            ),
          ],
        ),
      ),
    );
  }

  Widget _drawerItem(
    IconData icon,
    String title,
    String folder,
  ) {
    final selected = selectedFolder == folder;

    return ListTile(
      leading: Icon(icon),
      title: Text(
        title,
        style: TextStyle(
          fontWeight:
              selected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
      selected: selected,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(30),
      ),
      onTap: () {
        setState(() {
          selectedFolder = folder;
        });

        Navigator.pop(context);
      },
    );
  }

  void _openEmail(dynamic email) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => EmailDetailScreen(
          sender: _sender(email),
          subject: _subject(email),
          body: _body(email),
          category: _category(email),
          date: _formatDate(email),
          needsReply: email['needs_reply'] == true,
          replied: email['replied'] == true,
        ),
      ),
    );
  }
}

class EmailDetailScreen extends StatelessWidget {
  final String sender;
  final String subject;
  final String body;
  final String category;
  final String date;
  final bool needsReply;
  final bool replied;

  const EmailDetailScreen({
    super.key,
    required this.sender,
    required this.subject,
    required this.body,
    required this.category,
    required this.date,
    required this.needsReply,
    required this.replied,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Email',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              subject,
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 18),

            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 24,
                  child: Text(
                    sender.isNotEmpty
                        ? sender[0].toUpperCase()
                        : '?',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),

                const SizedBox(width: 12),

                Expanded(
                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment.start,
                    children: [
                      Text(
                        sender,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (date.isNotEmpty)
                        Text(
                          date,
                          style: const TextStyle(
                            color: Colors.white54,
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 14),

            Wrap(
              spacing: 7,
              runSpacing: 7,
              children: [
                Chip(
                  label: Text(category),
                ),

                if (needsReply)
                  const Chip(
                    label: Text('Needs reply'),
                  ),

                if (replied)
                  const Chip(
                    label: Text('Replied'),
                  ),
              ],
            ),

            const Divider(height: 30),

            SelectableText(
              body.isEmpty ? '(No email body)' : body,
              style: const TextStyle(
                fontSize: 15,
                height: 1.55,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
