import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { PricesService } from './prices.service';

@ApiTags('prices')
@Controller('api/prices')
export class PricesController {
  constructor(private readonly pricesService: PricesService) {}

  @Get('markets')
  @ApiOperation({ summary: '시장 목록 조회' })
  async getMarkets(): Promise<any[]> {
    return this.pricesService.getMarkets();
  }
}
