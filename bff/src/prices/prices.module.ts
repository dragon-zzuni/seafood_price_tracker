import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { PricesController } from './prices.controller';
import { PricesService } from './prices.service';
import { HttpClientService } from '../common/http-client.service';
import { CacheModule } from '../cache/cache.module';

@Module({
  imports: [HttpModule, CacheModule],
  controllers: [PricesController],
  providers: [PricesService, HttpClientService],
})
export class PricesModule {}
