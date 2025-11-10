import { Injectable } from '@nestjs/common';
import { HttpClientService } from '../common/http-client.service';
import { CacheService } from '../cache/cache.service';
import { Item, ItemDashboard } from '../common/types';

@Injectable()
export class ItemsService {
  private readonly SEARCH_CACHE_TTL = 1800; // 30분
  private readonly DASHBOARD_CACHE_TTL = 1800; // 30분

  constructor(
    private readonly httpClient: HttpClientService,
    private readonly cacheService: CacheService,
  ) {}

  /**
   * 품목 검색 (자동완성)
   */
  async searchItems(query: string): Promise<Item[]> {
    const cacheKey = `items:search:${query}`;
    
    return this.cacheService.getOrSet(
      cacheKey,
      async () => {
        const response = await this.httpClient.getCoreService<{ items: Item[] }>(
          `/items?query=${encodeURIComponent(query)}`
        );
        return response.items;
      },
      this.SEARCH_CACHE_TTL,
    );
  }

  /**
   * 품목 상세 조회
   */
  async getItemById(id: number): Promise<Item> {
    const cacheKey = `items:${id}`;
    
    return this.cacheService.getOrSet(
      cacheKey,
      async () => {
        return this.httpClient.getCoreService<Item>(`/items/${id}`);
      },
      this.SEARCH_CACHE_TTL,
    );
  }

  /**
   * 품목 대시보드 조회
   */
  async getItemDashboard(id: number, date?: string): Promise<ItemDashboard> {
    const dateStr = date || new Date().toISOString().split('T')[0];
    const cacheKey = `items:${id}:dashboard:${dateStr.replace(/-/g, '')}`;
    
    return this.cacheService.getOrSet(
      cacheKey,
      async () => {
        const queryParam = date ? `?date=${date}` : '';
        return this.httpClient.getCoreService<ItemDashboard>(
          `/items/${id}/dashboard${queryParam}`
        );
      },
      this.DASHBOARD_CACHE_TTL,
    );
  }
}
