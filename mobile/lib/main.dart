import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'presentation/screens/home_screen.dart';
import 'application/providers/settings_provider.dart';

/// 앱 시작 시 환경 변수 및 SharedPreferences 초기화
/// Requirements: 12.4, 12.5
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 환경 변수 로드 (파일이 없어도 앱 실행 가능)
  try {
  await dotenv.load(fileName: "../.env");
  } catch (e) {
    print('Warning: .env file not found. Using default API URL.');
  }
  
  // SharedPreferences 초기화
  final sharedPreferences = await SharedPreferences.getInstance();
  
  runApp(
    ProviderScope(
      overrides: [
        // SharedPreferences를 Provider에 주입
        sharedPreferencesProvider.overrideWith((ref) => sharedPreferences),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '수산물 가격 추적',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
