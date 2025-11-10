import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
  BadRequestException,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { ApiTags, ApiOperation, ApiConsumes, ApiBody, ApiResponse } from '@nestjs/swagger';
import { RecognitionService } from './recognition.service';
import { RecognitionResponseDto } from './dto/recognition-response.dto';

@ApiTags('recognition')
@Controller('api/recognition')
export class RecognitionController {
  constructor(private readonly recognitionService: RecognitionService) {}

  @Post()
  @ApiOperation({
    summary: '이미지 인식',
    description: '수산물 이미지를 업로드하여 품목을 자동으로 인식합니다. 최대 4개의 후보를 신뢰도 순으로 반환합니다.',
  })
  @ApiConsumes('multipart/form-data')
  @ApiBody({
    description: '인식할 이미지 파일 (최대 5MB, JPEG/PNG)',
    schema: {
      type: 'object',
      properties: {
        image: {
          type: 'string',
          format: 'binary',
          description: '이미지 파일',
        },
      },
      required: ['image'],
    },
  })
  @ApiResponse({
    status: 200,
    description: '인식 성공',
    type: RecognitionResponseDto,
  })
  @ApiResponse({
    status: 400,
    description: '잘못된 요청 (이미지 없음, 크기 초과, 인식 실패)',
    schema: {
      type: 'object',
      properties: {
        statusCode: { type: 'number', example: 400 },
        message: { type: 'string', example: '품목을 인식할 수 없습니다. 직접 검색해주세요' },
        timestamp: { type: 'string', example: '2025-11-10T12:00:00.000Z' },
      },
    },
  })
  @ApiResponse({
    status: 503,
    description: '서비스 이용 불가 (ML Service 오류)',
    schema: {
      type: 'object',
      properties: {
        statusCode: { type: 'number', example: 503 },
        message: { type: 'string', example: '이미지 인식 서비스에 일시적인 오류가 발생했습니다' },
        timestamp: { type: 'string', example: '2025-11-10T12:00:00.000Z' },
      },
    },
  })
  @UseInterceptors(FileInterceptor('image'))
  async recognizeImage(
    @UploadedFile() file: Express.Multer.File,
  ): Promise<RecognitionResponseDto> {
    if (!file) {
      throw new BadRequestException('이미지 파일이 필요합니다');
    }

    return this.recognitionService.recognizeImage(file.buffer);
  }
}

