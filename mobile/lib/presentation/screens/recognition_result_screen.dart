import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/recognition_result.dart';
import '../widgets/empty_state_widget.dart';
import 'item_dashboard_screen.dart';

/// 이미지 인식 결과 화면
/// 
/// 인식된 품목 후보 리스트를 신뢰도 순으로 표시하고,
/// 사용자가 품목을 선택하면 대시보드로 이동합니다.
/// Requirements: 1.7, 2.4
class RecognitionResultScreen extends ConsumerWidget {
  final RecognitionResult result;
  final File? image;

  const RecognitionResultScreen({
    super.key,
    required this.result,
    this.image,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('인식 결과'),
        elevation: 0,
      ),
      body: Column(
        children: [
          // 선택한 이미지 미리보기
          if (image != null)
            Container(
              height: 200,
              width: double.infinity,
              color: Colors.grey[200],
              child: Image.file(
                image!,
                fit: BoxFit.contain,
              ),
            ),

          // 안내 메시지
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '인식된 품목',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  '아래 목록에서 원하는 품목을 선택해주세요',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                ),
              ],
            ),
          ),

          // 후보 품목 리스트
          Expanded(
            child: result.candidates.isEmpty
                ? _buildEmptyState(context)
                : _buildCandidateList(context),
          ),
        ],
      ),
    );
  }

  /// 후보 품목 리스트 위젯
  Widget _buildCandidateList(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      itemCount: result.candidates.length,
      separatorBuilder: (context, index) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final candidate = result.candidates[index];
        return _buildCandidateItem(context, candidate, index);
      },
    );
  }

  /// 개별 후보 품목 아이템
  Widget _buildCandidateItem(
    BuildContext context,
    RecognitionCandidate candidate,
    int index,
  ) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 16.0,
        vertical: 12.0,
      ),
      leading: CircleAvatar(
        backgroundColor: _getConfidenceColor(candidate.confidence),
        child: Text(
          '${index + 1}',
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      title: Text(
        candidate.itemName,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),
          Row(
            children: [
              Text(
                '신뢰도: ',
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey[700],
                ),
              ),
              Text(
                '${(candidate.confidence * 100).toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: _getConfidenceColor(candidate.confidence),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: LinearProgressIndicator(
                  value: candidate.confidence,
                  backgroundColor: Colors.grey[200],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getConfidenceColor(candidate.confidence),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: () {
        // 품목 선택 시 대시보드로 이동
        _navigateToDashboard(context, candidate.itemId);
      },
    );
  }

  /// 빈 상태 위젯 - 인식 실패 시 직접 검색 유도
  Widget _buildEmptyState(BuildContext context) {
    return EmptyStateWidget.recognitionFailed(
      onSearchManually: () {
        // 홈 화면으로 돌아가서 검색 유도
        Navigator.of(context).pop();
      },
    );
  }

  /// 신뢰도에 따른 색상 반환
  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.7) {
      return Colors.green;
    } else if (confidence >= 0.5) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }

  /// 대시보드로 이동
  void _navigateToDashboard(BuildContext context, int itemId) {
    // 인식 결과 화면을 닫고 대시보드로 이동
    Navigator.of(context).pop();
    
    // 대시보드 화면으로 이동
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ItemDashboardScreen(
          itemId: itemId,
          itemName: result.candidates
              .firstWhere((c) => c.itemId == itemId)
              .itemName,
        ),
      ),
    );
  }
}
