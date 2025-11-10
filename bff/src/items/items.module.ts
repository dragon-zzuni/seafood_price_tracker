import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { ItemsController } from './items.controller';
import { ItemsService } from './items.service';
import { HttpClientService } from '../common/http-client.service';
import { CacheModule } from '../cache/cache.module';

@Module({
  imports: [HttpModule, CacheModule],
  controllers: [ItemsController],
  providers: [ItemsService, HttpClientService],
})
export class ItemsModule {}
