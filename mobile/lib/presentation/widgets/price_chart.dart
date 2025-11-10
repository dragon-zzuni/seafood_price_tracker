import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../domain/models/item_dashboard.dart';

/// 가격 추이 차트 위젯
/// 
/// fl_chart를 사용하여 7일/30일/90일 기간 선택 탭과 시장별 라인 차트를 표시합니다.
/// 데이터 포인트 터치 시 툴팁을 표시합니다.
/// Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
class PriceChart extends StatefulWidget {
  final PriceTrend priceTrend;
  
  const PriceChart({
    Key? key,
    required this.priceTrend,
  }) : super(key: key);
  
  @override
  State<PriceChart> createState() => _PriceChartState();
}

class _PriceChartState extends State<PriceChart> {
  int _selectedPeriod = 30; // 기본값: 30일
  
  // 시장별 색상 매핑
  static const Map<String, Color> _marketColors = {
    '가락시장': Colors.blue,
    '노량진수산시장': Colors.orange,
    '노량진': Colors.orange, // 별칭
  };
  
  @override
  Widget build(BuildContext context) {
    // 데이터가 충분한지 확인
    if (!widget.priceTrend.hasSufficientTrendData) {
      return _buildInsufficientDataWidget();
    }
    
    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 제목
            Text(
              '가격 추이',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            // 기간 선택 탭
            _buildPeriodSelector(),
            
            const SizedBox(height: 24),
            
            // 차트
            SizedBox(
              height: 250,
              child: _buildChart(),
            ),
            
            const SizedBox(height: 16),
            
            // 범례
            _buildLegend(),
          ],
        ),
      ),
    );
  }
  
  /// 기간 선택 탭 위젯
  Widget _buildPeriodSelector() {
    return Row(
      children: [
        _buildPeriodTab(7, '7일'),
        const SizedBox(width: 8),
        _buildPeriodTab(30, '30일'),
        const SizedBox(width: 8),
        _buildPeriodTab(90, '90일'),
      ],
    );
  }
  
  /// 개별 기간 탭 버튼
  Widget _buildPeriodTab(int days, String label) {
    final isSelected = _selectedPeriod == days;
    
    return Expanded(
      child: InkWell(
        onTap: () {
          setState(() {
            _selectedPeriod = days;
          });
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? Colors.blue : Colors.grey[200],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: isSelected ? Colors.white : Colors.grey[700],
              ),
            ),
          ),
        ),
      ),
    );
  }
  
  /// 차트 위젯
  Widget _buildChart() {
    final filteredData = _getFilteredData();
    
    if (filteredData.isEmpty || filteredData.values.every((list) => list.length < 3)) {
      return _buildInsufficientDataWidget();
    }
    
    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: true,
          horizontalInterval: _calculateInterval(widget.priceTrend.minPrice, widget.priceTrend.maxPrice),
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: Colors.grey[300]!,
              strokeWidth: 1,
            );
          },
          getDrawingVerticalLine: (value) {
            return FlLine(
              color: Colors.grey[300]!,
              strokeWidth: 1,
            );
          },
        ),
        titlesData: FlTitlesData(
          show: true,
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              interval: _calculateDateInterval(),
              getTitlesWidget: (value, meta) {
                return _buildDateLabel(value.toInt());
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 50,
              getTitlesWidget: (value, meta) {
                return Text(
                  _formatPrice(value),
                  style: const TextStyle(
                    fontSize: 10,
                    color: Colors.grey,
                  ),
                );
              },
            ),
          ),
        ),
        borderData: FlBorderData(
          show: true,
          border: Border.all(color: Colors.grey[300]!),
        ),
        minX: 0,
        maxX: (_selectedPeriod - 1).toDouble(),
        minY: widget.priceTrend.minPrice * 0.9,
        maxY: widget.priceTrend.maxPrice * 1.1,
        lineBarsData: _buildLineBars(filteredData),
        lineTouchData: LineTouchData(
          enabled: true,
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                final market = filteredData.keys.elementAt(spot.barIndex);
                final point = filteredData[market]![spot.x.toInt()];
                return LineTooltipItem(
                  '$market\n${DateFormat('M/d').format(point.dateTime)}\n${_formatPrice(point.price)}',
                  const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                );
              }).toList();
            },
          ),
        ),
      ),
    );
  }
  
  /// 범례 위젯
  Widget _buildLegend() {
    final markets = widget.priceTrend.groupedByMarket.keys.toList();
    
    return Wrap(
      spacing: 16,
      runSpacing: 8,
      children: markets.map((market) {
        final color = _getMarketColor(market);
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 16,
              height: 3,
              color: color,
            ),
            const SizedBox(width: 6),
            Text(
              market,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        );
      }).toList(),
    );
  }
  
  /// 데이터 부족 위젯
  Widget _buildInsufficientDataWidget() {
    return Container(
      height: 250,
      alignment: Alignment.center,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.info_outline,
            size: 48,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '데이터 부족',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '차트를 표시하기 위한 데이터가 부족합니다',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }
  
  /// 선택된 기간에 맞게 데이터 필터링
  Map<String, List<dynamic>> _getFilteredData() {
    final now = DateTime.now();
    final cutoffDate = now.subtract(Duration(days: _selectedPeriod));
    
    final grouped = widget.priceTrend.groupedByMarket;
    final filtered = <String, List<dynamic>>{};
    
    for (final entry in grouped.entries) {
      final marketData = entry.value
          .where((point) => point.dateTime.isAfter(cutoffDate))
          .toList()
        ..sort((a, b) => a.dateTime.compareTo(b.dateTime));
      
      if (marketData.isNotEmpty) {
        filtered[entry.key] = marketData;
      }
    }
    
    return filtered;
  }
  
  /// 라인 바 데이터 생성
  List<LineChartBarData> _buildLineBars(Map<String, List<dynamic>> data) {
    return data.entries.map((entry) {
      final market = entry.key;
      final points = entry.value;
      final color = _getMarketColor(market);
      
      return LineChartBarData(
        spots: points.asMap().entries.map((e) {
          return FlSpot(e.key.toDouble(), e.value.price);
        }).toList(),
        isCurved: true,
        color: color,
        barWidth: 3,
        isStrokeCapRound: true,
        dotData: FlDotData(
          show: true,
          getDotPainter: (spot, percent, barData, index) {
            return FlDotCirclePainter(
              radius: 4,
              color: color,
              strokeWidth: 2,
              strokeColor: Colors.white,
            );
          },
        ),
        belowBarData: BarAreaData(
          show: true,
          color: color.withValues(alpha: 0.1),
        ),
      );
    }).toList();
  }
  
  /// 시장별 색상 반환
  Color _getMarketColor(String market) {
    return _marketColors[market] ?? Colors.green;
  }
  
  /// 날짜 라벨 생성
  Widget _buildDateLabel(int index) {
    final filteredData = _getFilteredData();
    if (filteredData.isEmpty) return const SizedBox.shrink();
    
    final firstMarket = filteredData.values.first;
    if (index >= firstMarket.length) return const SizedBox.shrink();
    
    final point = firstMarket[index];
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Text(
        DateFormat('M/d').format(point.dateTime),
        style: const TextStyle(
          fontSize: 10,
          color: Colors.grey,
        ),
      ),
    );
  }
  
  /// 가격 포맷팅 (천 단위 구분)
  String _formatPrice(double price) {
    if (price >= 10000) {
      return '${(price / 1000).toStringAsFixed(0)}k';
    }
    return price.toStringAsFixed(0);
  }
  
  /// Y축 간격 계산
  double _calculateInterval(double min, double max) {
    final range = max - min;
    if (range <= 0) return 1000;
    
    final interval = range / 5;
    if (interval < 1000) return 1000;
    if (interval < 5000) return 5000;
    if (interval < 10000) return 10000;
    return (interval / 10000).ceil() * 10000;
  }
  
  /// X축(날짜) 간격 계산
  double _calculateDateInterval() {
    if (_selectedPeriod <= 7) return 1;
    if (_selectedPeriod <= 30) return 5;
    return 15;
  }
}

/// PriceTrend 확장 메서드
extension PriceTrendExtension on PriceTrend {
  bool get hasSufficientTrendData => data.length >= 3;
}
