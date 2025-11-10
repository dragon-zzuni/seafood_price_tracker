import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { AxiosError } from 'axios';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요';
    let errorType = 'InternalServerError';
    let details: any = undefined;

    // HttpException 처리
    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();
      
      if (typeof exceptionResponse === 'string') {
        message = exceptionResponse;
      } else if (typeof exceptionResponse === 'object') {
        const responseObj = exceptionResponse as any;
        message = responseObj.message || message;
        errorType = responseObj.error || errorType;
        details = responseObj.details;
      }
    }
    // Axios 에러 처리 (Core/ML Service 호출 실패)
    else if (this.isAxiosError(exception)) {
      const axiosError = exception as AxiosError;
      const { status: axiosStatus, message: axiosMessage } = this.handleAxiosError(axiosError);
      status = axiosStatus;
      message = axiosMessage;
      errorType = 'ExternalServiceError';
    }
    // 기타 예외
    else if (exception instanceof Error) {
      this.logger.error(`Unexpected error: ${exception.message}`, exception.stack);
    }

    // 5xx 오류는 상세 정보 숨김 (보안) - Requirement 11.3
    if (status >= 500) {
      this.logger.error('Server error:', exception);
      // 사용자에게는 일반적인 메시지만 표시 (상세 정보 숨김)
      message = '일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요';
      details = undefined; // 상세 정보 제거
      errorType = 'ServerError'; // 일반적인 타입으로 변경
    } else {
      // 4xx 오류는 로그 레벨을 낮춤
      this.logger.warn(
        `Client error: ${status} - ${message}`,
        {
          path: request.url,
          method: request.method,
          errorType,
        }
      );
    }

    response.status(status).json({
      statusCode: status,
      message,
      errorType,
      ...(details && { details }),
      timestamp: new Date().toISOString(),
      path: request.url,
    });
  }

  private isAxiosError(error: any): error is AxiosError {
    return error.isAxiosError === true;
  }

  private handleAxiosError(error: AxiosError): { status: number; message: string } {
    // Core Service 또는 ML Service 응답이 있는 경우
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as any;

      // Core Service의 표준 에러 응답 처리
      if (data?.error) {
        return {
          status,
          message: this.translateErrorMessage(data.error.type, data.error.message),
        };
      }

      // 일반 에러 응답
      if (data?.message) {
        return {
          status,
          message: this.translateErrorMessage('', data.message),
        };
      }

      // 상태 코드별 기본 메시지
      return {
        status,
        message: this.getDefaultMessageForStatus(status),
      };
    }

    // 네트워크 오류 (서비스 연결 실패) - Requirement 11.1
    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      this.logger.error('External service connection failed', error.message);
      return {
        status: HttpStatus.SERVICE_UNAVAILABLE,
        message: '네트워크 연결을 확인해주세요',
      };
    }

    // 타임아웃
    if (error.code === 'ECONNABORTED') {
      return {
        status: HttpStatus.REQUEST_TIMEOUT,
        message: '요청 시간이 초과되었습니다. 다시 시도해주세요',
      };
    }

    // 기타 네트워크 오류
    return {
      status: HttpStatus.BAD_GATEWAY,
      message: '외부 서비스 오류가 발생했습니다',
    };
  }

  private translateErrorMessage(errorType: string, originalMessage: string): string {
    // Core Service 에러 타입별 사용자 친화적 메시지 변환
    const translations: Record<string, string> = {
      // Core Service 에러
      'ItemNotFoundException': '품목을 찾을 수 없습니다',
      'PriceDataNotFoundException': '가격 데이터가 없습니다',
      'MarketNotFoundException': '시장 정보를 찾을 수 없습니다',
      'AliasNotFoundException': '품목 정보를 찾을 수 없습니다',
      'InvalidDateRangeException': '잘못된 날짜 범위입니다',
      'ValidationException': '입력 데이터가 올바르지 않습니다',
      
      // ML Service 에러 (Requirement 11.2)
      'RecognitionFailedException': '품목을 인식할 수 없습니다. 직접 검색해주세요',
      'ImageTooLargeException': '이미지 크기가 너무 큽니다. 5MB 이하의 이미지를 사용해주세요',
      'InvalidImageFormatException': '지원하지 않는 이미지 형식입니다',
      'ModelInferenceException': '품목을 인식할 수 없습니다. 직접 검색해주세요',
      
      // 네트워크 에러 (Requirement 11.1)
      'NetworkError': '네트워크 연결을 확인해주세요',
      'ConnectionError': '네트워크 연결을 확인해주세요',
    };

    return translations[errorType] || originalMessage;
  }

  private getDefaultMessageForStatus(status: number): string {
    const messages: Record<number, string> = {
      400: '잘못된 요청입니다',
      401: '인증이 필요합니다',
      403: '접근 권한이 없습니다',
      404: '요청한 정보를 찾을 수 없습니다',
      408: '요청 시간이 초과되었습니다',
      422: '입력 데이터가 올바르지 않습니다',
      429: '너무 많은 요청이 발생했습니다. 잠시 후 다시 시도해주세요',
      500: '서버 오류가 발생했습니다',
      502: '외부 서비스 오류가 발생했습니다',
      503: '서비스를 일시적으로 사용할 수 없습니다',
      504: '외부 서비스 응답 시간이 초과되었습니다',
    };

    return messages[status] || '일시적인 오류가 발생했습니다';
  }
}
