import { Injectable } from '@nestjs/common';
import { HttpClientService } from '../common/http-client.service';
import { CacheService } from '../cache/cache.service';

@Injectable()
export class PricesService {
  private readonly PRICE_CACHE_TTL = 1800; // 30분

  constructor(
    private readonly httpClient: HttpClientService,
    private readonly cacheService: CacheService,
  ) {}

  /**
   * 시장 목록 조회
   */
  async getMarkets(): Promise<any[]> {
    const cacheKey = 'markets:list';
    
    return this.cacheService.getOrSet(
      cacheKey,
      async () => {
        return this.httpClient.getCoreService<any[]>('/markets');
      },
      3600, // 1시간
    );
  }
}
