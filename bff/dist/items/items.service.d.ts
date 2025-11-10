import { HttpClientService } from '../common/http-client.service';
import { CacheService } from '../cache/cache.service';
import { Item, ItemDashboard } from '../common/types';
export declare class ItemsService {
    private readonly httpClient;
    private readonly cacheService;
    private readonly SEARCH_CACHE_TTL;
    private readonly DASHBOARD_CACHE_TTL;
    constructor(httpClient: HttpClientService, cacheService: CacheService);
    searchItems(query: string): Promise<Item[]>;
    getItemById(id: number): Promise<Item>;
    getItemDashboard(id: number, date?: string): Promise<ItemDashboard>;
}
