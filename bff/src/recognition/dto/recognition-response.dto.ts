import { ApiProperty } from '@nestjs/swagger';

export class RecognitionCandidateDto {
  @ApiProperty({
    description: '품목 ID',
    example: 1,
  })
  item_id: number;

  @ApiProperty({
    description: '품목명 (한글)',
    example: '광어',
  })
  item_name: string;

  @ApiProperty({
    description: '인식 신뢰도 (0.0 ~ 1.0)',
    example: 0.85,
    minimum: 0,
    maximum: 1,
  })
  confidence: number;
}

export class RecognitionResponseDto {
  @ApiProperty({
    description: '인식된 품목 후보 목록 (최대 4개, 신뢰도 순)',
    type: [RecognitionCandidateDto],
  })
  candidates: RecognitionCandidateDto[];
}
