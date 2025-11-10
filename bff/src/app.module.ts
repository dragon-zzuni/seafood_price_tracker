import { Module } from '@nestjs/common';
import { ItemsModule } from './items/items.module';
import { PricesModule } from './prices/prices.module';
import { RecognitionModule } from './recognition/recognition.module';
import { CacheModule } from './cache/cache.module';

@Module({
  imports: [
    ItemsModule,
    PricesModule,
    RecognitionModule,
    CacheModule,
  ],
})
export class AppModule {}
