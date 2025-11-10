import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../application/providers/item_provider.dart';
import '../../application/providers/recognition_provider.dart';
import '../../infrastructure/services/error_handler.dart';
import '../widgets/item_search_bar.dart';
import '../widgets/error_snackbar.dart';
import '../widgets/loading_indicator.dart';
import 'recognition_result_screen.dart';
import 'item_dashboard_screen.dart';
import 'settings_screen.dart';

/// 홈 화면
/// 
/// 검색창, 카메라 버튼, 인기 품목 카드 슬라이더를 포함합니다.
/// Requirements: 2.1, 2.3
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // 에러 상태 변경 감지를 위한 리스너 설정
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.listen<ItemSearchState>(
        itemSearchProvider,
        (previous, next) {
          if (next.error != null && next.error != previous?.error) {
            // 에러 발생 시 스낵바 표시 (3초 자동 숨김)
            ErrorSnackbar.show(
              context,
              AppError(
                type: ErrorType.unknown,
                message: next.error!,
                canRetry: false,
              ),
            );
          }
        },
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final searchState = ref.watch(itemSearchProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          '수산물 가격 추적',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
        elevation: 0,
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          // 설정 버튼
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const SettingsScreen(),
                ),
              );
            },
            tooltip: '설정',
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // 상단 검색 영역
            Container(
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(24),
                  bottomRight: Radius.circular(24),
                ),
              ),
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              child: Column(
                children: [
                  // 검색 바
                  ItemSearchBar(
                    onSearchChanged: (query) {
                      ref.read(itemSearchProvider.notifier).updateQuery(query);
                    },
                    onItemSelected: (item) {
                      ref.read(selectedItemProvider.notifier).state = item;
                      // 대시보드 화면으로 이동
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => ItemDashboardScreen(
                            itemId: item.id,
                            itemName: item.nameKo,
                          ),
                        ),
                      );
                    },
                    suggestions: searchState.items,
                    isLoading: searchState.isLoading,
                    selectedCategory: searchState.selectedCategory,
                    onCategoryChanged: (category) {
                      ref.read(itemSearchProvider.notifier).updateCategory(category);
                    },
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // 카메라 버튼
                  _buildCameraButton(context),
                ],
              ),
            ),
            
            // 에러 메시지는 스낵바로 표시 (3초 자동 숨김)
            // searchState.error가 변경되면 스낵바 표시
            
            // 메인 콘텐츠 영역
            Expanded(
              child: _buildMainContent(context),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 카메라 버튼
  Widget _buildCameraButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: () {
          _showCameraOptions(context);
        },
        icon: const Icon(Icons.camera_alt, size: 24),
        label: const Text(
          '사진으로 품목 인식하기',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: Colors.blue,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 2,
        ),
      ),
    );
  }
  
  /// 메인 콘텐츠 (인기 품목 카드 슬라이더 - 선택 사항)
  Widget _buildMainContent(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 안내 텍스트
          const Text(
            '품목을 검색하거나 사진을 촬영하여\n실시간 시장 가격을 확인하세요',
            style: TextStyle(
              fontSize: 16,
              color: Colors.black87,
              height: 1.5,
            ),
            textAlign: TextAlign.center,
          ),
          
          const SizedBox(height: 32),
          
          // 인기 품목 섹션 (선택 사항)
          _buildPopularItemsSection(),
        ],
      ),
    );
  }
  
  /// 인기 품목 섹션 (선택 사항)
  Widget _buildPopularItemsSection() {
    // 임시 인기 품목 데이터
    final popularItems = [
      {'name': '광어', 'icon': Icons.set_meal, 'color': Colors.blue},
      {'name': '고등어', 'icon': Icons.set_meal, 'color': Colors.teal},
      {'name': '전복', 'icon': Icons.water_drop, 'color': Colors.orange},
      {'name': '대게', 'icon': Icons.pest_control, 'color': Colors.red},
    ];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '인기 품목',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.5,
          ),
          itemCount: popularItems.length,
          itemBuilder: (context, index) {
            final item = popularItems[index];
            return _buildPopularItemCard(
              name: item['name'] as String,
              icon: item['icon'] as IconData,
              color: item['color'] as Color,
              onTap: () {
                // 해당 품목 검색
                ref.read(itemSearchProvider.notifier).updateQuery(item['name'] as String);
              },
            );
          },
        ),
      ],
    );
  }
  
  /// 인기 품목 카드
  Widget _buildPopularItemCard({
    required String name,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 40,
              color: color,
            ),
            const SizedBox(height: 8),
            Text(
              name,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 카메라 옵션 다이얼로그
  void _showCameraOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: const Icon(Icons.camera_alt, color: Colors.blue),
                  title: const Text('카메라로 촬영'),
                  onTap: () {
                    Navigator.pop(context);
                    _handleRecognition(ImageSource.camera);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.photo_library, color: Colors.blue),
                  title: const Text('갤러리에서 선택'),
                  onTap: () {
                    Navigator.pop(context);
                    _handleRecognition(ImageSource.gallery);
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  /// 이미지 인식 처리
  void _handleRecognition(ImageSource source) async {
    final recognitionNotifier = ref.read(recognitionProvider.notifier);
    
    // 이미지 인식 전용 로딩 인디케이터 표시
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Dialog(
        backgroundColor: Colors.transparent,
        child: RecognitionProgressIndicator(
          message: '이미지를 분석하고 있습니다...',
        ),
      ),
    );
    
    // 이미지 인식 실행
    if (source == ImageSource.camera) {
      await recognitionNotifier.recognizeFromCamera();
    } else {
      await recognitionNotifier.recognizeFromGallery();
    }
    
    // 로딩 다이얼로그 닫기
    if (mounted) {
      Navigator.of(context).pop();
    }
    
    // 결과 처리
    final recognitionState = ref.read(recognitionProvider);
    
    if (recognitionState.error != null) {
      // 에러 표시 (3초 자동 숨김)
      if (mounted) {
        ErrorSnackbar.show(
          context,
          AppError(
            type: ErrorType.recognition,
            message: recognitionState.error!,
            canRetry: false,
          ),
          onRetry: null,
        );
      }
    } else if (recognitionState.result != null) {
      // 인식 결과 화면으로 이동
      if (mounted) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => RecognitionResultScreen(
              result: recognitionState.result!,
              image: recognitionState.selectedImage,
            ),
          ),
        );
      }
    }
  }
}
