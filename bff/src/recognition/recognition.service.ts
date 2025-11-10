import { Injectable, BadRequestException, ServiceUnavailableException } from '@nestjs/common';
import { HttpClientService } from '../common/http-client.service';
import { RecognitionResult, Item } from '../common/types';
import * as FormData from 'form-data';

// ML Service 응답 타입
interface MLRecognitionResponse {
  results: Array<{
    item_name: string;
    confidence: number;
  }>;
}

@Injectable()
export class RecognitionService {
  private readonly MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5MB

  constructor(private readonly httpClient: HttpClientService) {}

  /**
   * 이미지 인식 및 결과 후처리
   * Requirements: 1.2, 1.3, 1.7, 11.2
   */
  async recognizeImage(imageBuffer: Buffer): Promise<RecognitionResult> {
    // 1. 이미지 크기 검증 (Requirement 1.2)
    if (imageBuffer.length > this.MAX_IMAGE_SIZE) {
      throw new BadRequestException('이미지 크기는 5MB를 초과할 수 없습니다');
    }

    try {
      // 2. ML Service로 이미지 전송 (Requirement 1.3)
      const mlResponse = await this.callMLService(imageBuffer);

      // 3. 인식 결과 검증
      if (!mlResponse.results || mlResponse.results.length === 0) {
        throw new BadRequestException('품목을 인식할 수 없습니다. 직접 검색해주세요');
      }

      // 4. 품목 ID 매핑 (Requirement 1.7, 11.2)
      const candidates = await this.mapToItemIds(mlResponse.results);

      // 5. 모바일 친화적 포맷으로 변환
      return {
        candidates: candidates.slice(0, 4), // Top-4 결과만 반환
      };
    } catch (error) {
      return this.handleRecognitionError(error);
    }
  }

  /**
   * ML Service 호출
   */
  private async callMLService(imageBuffer: Buffer): Promise<MLRecognitionResponse> {
    try {
      // FormData 생성
      const formData = new FormData();
      formData.append('image', imageBuffer, {
        filename: 'image.jpg',
        contentType: 'image/jpeg',
      });

      // ML Service로 프록시
      const response = await this.httpClient.postMlService<MLRecognitionResponse>(
        '/recognize',
        formData,
        formData.getHeaders()
      );

      return response;
    } catch (error) {
      console.error('ML Service call failed:', error);
      throw new ServiceUnavailableException('이미지 인식 서비스에 연결할 수 없습니다');
    }
  }

  /**
   * 품목명을 품목 ID로 매핑
   * Core Service를 조회하여 정확한 품목 정보 가져오기
   */
  private async mapToItemIds(
    mlResults: Array<{ item_name: string; confidence: number }>
  ): Promise<Array<{ item_id: number; item_name: string; confidence: number }>> {
    const candidates = [];

    for (const result of mlResults) {
      try {
        // Core Service에서 품목 검색
        const items = await this.httpClient.getCoreService<{ items: Item[] }>(
          `/items?query=${encodeURIComponent(result.item_name)}`
        );

        if (items.items && items.items.length > 0) {
          // 첫 번째 매칭 품목 사용
          const item = items.items[0];
          candidates.push({
            item_id: item.id,
            item_name: item.name_ko,
            confidence: result.confidence,
          });
        } else {
          // 품목을 찾지 못한 경우 로그만 기록하고 계속 진행
          console.warn(`Item not found in Core Service: ${result.item_name}`);
        }
      } catch (error) {
        // 개별 품목 조회 실패 시 로그만 기록하고 계속 진행
        console.error(`Failed to map item: ${result.item_name}`, error);
      }
    }

    return candidates;
  }

  /**
   * 에러 처리 및 사용자 친화적 메시지 변환
   * Requirement: 11.2
   */
  private handleRecognitionError(error: any): never {
    if (error instanceof BadRequestException) {
      throw error;
    }

    if (error instanceof ServiceUnavailableException) {
      throw error;
    }

    // 네트워크 오류
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      throw new ServiceUnavailableException('네트워크 연결을 확인해주세요');
    }

    // 기타 오류
    console.error('Unexpected recognition error:', error);
    throw new ServiceUnavailableException('일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요');
  }
}
