import 'package:flutter/material.dart';
import '../../domain/models/models.dart';

/// 품목 검색 바 위젯
/// 
/// 자동완성 기능이 있는 검색 입력 필드를 제공합니다.
/// Requirements: 2.1, 2.2, 2.3
class ItemSearchBar extends StatefulWidget {
  final Function(String) onSearchChanged;
  final Function(Item) onItemSelected;
  final List<Item> suggestions;
  final bool isLoading;
  final String? selectedCategory;
  final Function(String?) onCategoryChanged;
  
  const ItemSearchBar({
    super.key,
    required this.onSearchChanged,
    required this.onItemSelected,
    required this.suggestions,
    this.isLoading = false,
    this.selectedCategory,
    required this.onCategoryChanged,
  });

  @override
  State<ItemSearchBar> createState() => _ItemSearchBarState();
}

class _ItemSearchBarState extends State<ItemSearchBar> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  bool _showSuggestions = false;
  
  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      setState(() {
        _showSuggestions = _focusNode.hasFocus && widget.suggestions.isNotEmpty;
      });
    });
  }
  
  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 검색 입력 필드
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: TextField(
            controller: _controller,
            focusNode: _focusNode,
            decoration: InputDecoration(
              hintText: '품목명을 입력하세요 (예: 광어, 우럭)',
              prefixIcon: const Icon(Icons.search, color: Colors.blue),
              suffixIcon: widget.isLoading
                  ? const Padding(
                      padding: EdgeInsets.all(12.0),
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    )
                  : _controller.text.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _controller.clear();
                            widget.onSearchChanged('');
                            setState(() {
                              _showSuggestions = false;
                            });
                          },
                        )
                      : null,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              filled: true,
              fillColor: Colors.white,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 14,
              ),
            ),
            onChanged: (value) {
              widget.onSearchChanged(value);
              setState(() {
                _showSuggestions = value.isNotEmpty && widget.suggestions.isNotEmpty;
              });
            },
          ),
        ),
        
        const SizedBox(height: 12),
        
        // 카테고리 필터
        _buildCategoryFilter(),
        
        // 자동완성 리스트
        if (_showSuggestions && widget.suggestions.isNotEmpty)
          _buildSuggestionsList(),
      ],
    );
  }
  
  /// 카테고리 필터 UI
  Widget _buildCategoryFilter() {
    final categories = [
      {'value': null, 'label': '전체', 'icon': Icons.grid_view},
      {'value': 'fish', 'label': '생선', 'icon': Icons.set_meal},
      {'value': 'shellfish', 'label': '조개류', 'icon': Icons.water_drop},
      {'value': 'crustacean', 'label': '갑각류', 'icon': Icons.pest_control},
      {'value': 'cephalopod', 'label': '연체류', 'icon': Icons.bubble_chart},
      {'value': 'other', 'label': '기타', 'icon': Icons.more_horiz},
    ];
    
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: categories.map((category) {
          final isSelected = widget.selectedCategory == category['value'];
          return Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: FilterChip(
              label: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    category['icon'] as IconData,
                    size: 16,
                    color: isSelected ? Colors.white : Colors.blue,
                  ),
                  const SizedBox(width: 4),
                  Text(category['label'] as String),
                ],
              ),
              selected: isSelected,
              onSelected: (selected) {
                widget.onCategoryChanged(
                  selected ? category['value'] as String? : null,
                );
              },
              selectedColor: Colors.blue,
              backgroundColor: Colors.white,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : Colors.black87,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
              side: BorderSide(
                color: isSelected ? Colors.blue : Colors.grey.shade300,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
  
  /// 자동완성 리스트 UI
  Widget _buildSuggestionsList() {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      constraints: const BoxConstraints(maxHeight: 300),
      child: ListView.separated(
        shrinkWrap: true,
        padding: const EdgeInsets.symmetric(vertical: 8),
        itemCount: widget.suggestions.length,
        separatorBuilder: (context, index) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final item = widget.suggestions[index];
          return ListTile(
            leading: CircleAvatar(
              backgroundColor: _getCategoryColor(item.category),
              child: Icon(
                _getCategoryIcon(item.category),
                color: Colors.white,
                size: 20,
              ),
            ),
            title: Text(
              item.nameKo,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 16,
              ),
            ),
            subtitle: item.nameEn != null
                ? Text(
                    item.nameEn!,
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 13,
                    ),
                  )
                : null,
            trailing: Chip(
              label: Text(
                _getCategoryLabel(item.category),
                style: const TextStyle(fontSize: 11),
              ),
              backgroundColor: _getCategoryColor(item.category).withOpacity(0.2),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 0),
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            onTap: () {
              _controller.text = item.nameKo;
              widget.onItemSelected(item);
              setState(() {
                _showSuggestions = false;
              });
              _focusNode.unfocus();
            },
          );
        },
      ),
    );
  }
  
  /// 카테고리별 색상 반환
  Color _getCategoryColor(String category) {
    switch (category) {
      case 'fish':
        return Colors.blue;
      case 'shellfish':
        return Colors.teal;
      case 'crustacean':
        return Colors.orange;
      case 'cephalopod':
        return Colors.deepPurple;
      case 'other':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }
  
  /// 카테고리별 아이콘 반환
  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'fish':
        return Icons.set_meal;
      case 'shellfish':
        return Icons.water_drop;
      case 'crustacean':
        return Icons.pest_control;
      case 'cephalopod':
        return Icons.bubble_chart;
      case 'other':
        return Icons.more_horiz;
      default:
        return Icons.help_outline;
    }
  }
  
  /// 카테고리별 라벨 반환
  String _getCategoryLabel(String category) {
    switch (category) {
      case 'fish':
        return '생선';
      case 'shellfish':
        return '조개류';
      case 'crustacean':
        return '갑각류';
      case 'cephalopod':
        return '연체류';
      case 'other':
        return '기타';
      default:
        return '미분류';
    }
  }
}
