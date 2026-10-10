import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const apiBase = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://127.0.0.1:8000');

void main() => runApp(const TwinApp());

class TwinApp extends StatelessWidget {
  const TwinApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Cardiovascular Twin',
        theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff087f8c)), useMaterial3: true),
        home: const DashboardPage(),
      );
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});
  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  Map<String, dynamic>? data;
  String? error;
  bool loading = true;
  bool contactAuthorized = false;

  Future<void> refresh() async {
    setState(() { loading = true; error = null; });
    try {
      final response = await http.get(Uri.parse('$apiBase/api/patients/demo/dashboard'));
      if (response.statusCode != 200) throw Exception('API returned ${response.statusCode}: ${response.body}');
      setState(() => data = jsonDecode(response.body) as Map<String, dynamic>);
      contactAuthorized = data?['family_contact_authorized'] == true;
    } catch (e) {
      setState(() => error = '$e');
    } finally {
      setState(() => loading = false);
    }
  }

  Future<void> simulate(String scenario) async {
    try {
      final response = await http.post(Uri.parse('$apiBase/api/patients/demo/simulate'),
          headers: {'Content-Type': 'application/json'}, body: jsonEncode({'scenario': scenario, 'hours': 3}));
      if (response.statusCode != 200) throw Exception(response.body);
      await refresh();
    } catch (e) {
      setState(() => error = '$e');
    }
  }

  Future<void> setFamilyPermission(bool authorized) async {
    final response = await http.put(Uri.parse('$apiBase/api/patients/demo/family-contact'),
        headers: {'Content-Type': 'application/json'}, body: jsonEncode({'authorized': authorized, 'name': 'Demo family contact'}));
    if (response.statusCode != 200) throw Exception(response.body);
    setState(() => contactAuthorized = authorized);
  }

  Future<void> runWhatIf() async {
    final controllers = <String, TextEditingController>{
      'heart_rate': TextEditingController(text: '96'),
      'hrv': TextEditingController(text: '25'),
      'systolic_bp': TextEditingController(text: '145'),
      'spo2': TextEditingController(text: '93'),
    };
    final changes = await showDialog<Map<String, double>?>(context: context, builder: (dialogContext) => AlertDialog(
      title: const Text('What-if measurements'),
      content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: controllers.entries.map((entry) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: TextField(controller: entry.value, keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(labelText: entry.key.replaceAll('_', ' '), border: const OutlineInputBorder())),
      )).toList())),
      actions: [
        TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
        FilledButton(onPressed: () {
          final values = <String, double>{};
          for (final entry in controllers.entries) {
            final value = double.tryParse(entry.value.text);
            if (value == null) return;
            values[entry.key] = value;
          }
          Navigator.pop(dialogContext, values);
        }, child: const Text('Assess')),
      ],
    ));
    for (final controller in controllers.values) { controller.dispose(); }
    if (changes == null) return;
    final response = await http.post(Uri.parse('$apiBase/api/patients/demo/what-if'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'changes': changes}));
    if (response.statusCode != 200) throw Exception(response.body);
    final result = jsonDecode(response.body) as Map<String, dynamic>;
    if (!mounted) return;
    showDialog<void>(context: context, builder: (_) => AlertDialog(
      title: Text('What-if: ${result['state']}'),
      content: Text('${result['explanation']}\n\nThis scenario did not change patient history.'),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
    ));
  }

  @override
  void initState() { super.initState(); refresh(); }

  @override
  Widget build(BuildContext context) {
    final latest = data?['latest'] as Map<String, dynamic>? ?? {};
    final baseline = data?['baseline']?['values'] as Map<String, dynamic>? ?? {};
    final assessment = data?['assessment'] as Map<String, dynamic>? ?? {};
    final history = data?['history'] as List<dynamic>? ?? [];
    return Scaffold(
      appBar: AppBar(title: const Text('Cardiovascular Twin'), actions: [IconButton(onPressed: refresh, icon: const Icon(Icons.refresh))]),
      body: loading && data == null ? const Center(child: CircularProgressIndicator()) : RefreshIndicator(
        onRefresh: refresh,
        child: ListView(padding: const EdgeInsets.all(16), children: [
          if (error != null) Card(color: Theme.of(context).colorScheme.errorContainer, child: Padding(padding: const EdgeInsets.all(12), child: Text(error!))),
          _statusCard(assessment),
          const SizedBox(height: 12),
          Text('Latest readings', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          _metricGrid(latest, baseline),
          const SizedBox(height: 16),
          Text('Recent trends', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          _trendCard(history),
          const SizedBox(height: 16),
          Text('Demo scenarios', style: Theme.of(context).textTheme.titleLarge),
          Wrap(spacing: 8, runSpacing: 8, children: [
            _scenarioButton('Normal', 'normal'), _scenarioButton('Sustained deviation', 'sustained_deviation'),
            _scenarioButton('Recovery', 'recovery'), _scenarioButton('Incomplete data', 'incomplete'),
            OutlinedButton.icon(onPressed: runWhatIf, icon: const Icon(Icons.science_outlined), label: const Text('What-if')),
          ]),
          const SizedBox(height: 12),
          Card(child: SwitchListTile(title: const Text('Authorize demo family contact'), subtitle: const Text('Alerts use local demo delivery unless FCM is configured.'), value: contactAuthorized,
              onChanged: (value) => setFamilyPermission(value).catchError((e) => setState(() => error = '$e')))),
          const Padding(padding: EdgeInsets.symmetric(vertical: 14), child: Text('Simulated data only. Deviations are for further attention and are not a diagnosis or medical-event prediction.', style: TextStyle(color: Colors.black54))),
        ]),
      ),
    );
  }

  Widget _statusCard(Map<String, dynamic> assessment) {
    final deviation = assessment['state'] == 'deviation';
    final color = deviation ? Colors.deepOrange : Colors.teal;
    final contributors = (assessment['contributing_measurements'] as List<dynamic>? ?? []).map((x) => x['signal'].toString().replaceAll('_', ' ')).join(', ');
    return Card(color: color.withOpacity(.09), child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [Icon(deviation ? Icons.info_outline : Icons.favorite_outline, color: color), const SizedBox(width: 8), Text('Twin status: ${assessment['state'] ?? 'loading'}', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: color))]),
      const SizedBox(height: 8), Text(assessment['explanation']?.toString() ?? 'Connecting to the simulated patient.'),
      if (contributors.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text('Signals to review: $contributors')),
      if ((assessment['missing_signals'] as List<dynamic>? ?? []).isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text('Missing: ${(assessment['missing_signals'] as List<dynamic>).join(', ')}')),
      const SizedBox(height: 8), Text('Demo model score ${assessment['confidence'] ?? '—'} · persistence ${assessment['persistence_hours'] ?? 0}/${assessment['alert_threshold_hours'] ?? 3} hours', style: Theme.of(context).textTheme.labelMedium),
    ])));
  }

  Widget _metricGrid(Map<String, dynamic> latest, Map<String, dynamic> baseline) {
    const labels = {'heart_rate': ('Heart rate', 'bpm'), 'hrv': ('HRV', 'ms'), 'systolic_bp': ('Systolic BP', 'mmHg'),
      'diastolic_bp': ('Diastolic BP', 'mmHg'), 'spo2': ('SpO₂', '%'), 'activity': ('Activity', 'steps')};
    return GridView.count(shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), crossAxisCount: 2, childAspectRatio: 1.8, crossAxisSpacing: 8, mainAxisSpacing: 8,
      children: labels.entries.map((entry) {
        final value = latest[entry.key]; final center = baseline[entry.key];
        return Card(child: Padding(padding: const EdgeInsets.all(12), child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [
          Text(entry.value.$1, style: Theme.of(context).textTheme.labelLarge),
          Text(value == null ? 'No reading' : '${(value as num).toStringAsFixed(0)} ${entry.value.$2}', style: Theme.of(context).textTheme.titleLarge),
          Text(center == null ? 'Baseline learning' : 'Baseline ${((center as num).toDouble()).toStringAsFixed(0)} ${entry.value.$2}', style: Theme.of(context).textTheme.bodySmall),
        ])));
      }).toList());
  }

  Widget _trendCard(List<dynamic> history) {
    if (history.isEmpty) return const Card(child: Padding(padding: EdgeInsets.all(16), child: Text('No trend data yet.')));
    final last = history.skip(history.length > 12 ? history.length - 12 : 0).toList();
    const signals = [('heart_rate', 'Heart rate'), ('hrv', 'HRV'), ('spo2', 'SpO₂')];
    return Card(child: Padding(padding: const EdgeInsets.all(12), child: Column(children: signals.map((signal) {
      final values = last.map((r) => (r[signal.$1] as num?)?.toDouble()).whereType<double>().toList();
      final max = values.isEmpty ? 1.0 : values.reduce((a, b) => a > b ? a : b);
      return Padding(padding: const EdgeInsets.symmetric(vertical: 7), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(signal.$2), const SizedBox(height: 4), Row(children: values.map((v) => Expanded(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 1), child: LinearProgressIndicator(value: (v / max).clamp(0, 1), minHeight: 8)))).toList())]));
    }).toList())));
  }

  Widget _scenarioButton(String label, String scenario) => OutlinedButton(onPressed: () => simulate(scenario), child: Text(label));
}
