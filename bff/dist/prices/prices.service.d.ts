import { HttpClientService } from '../common/http-client.service';
import { CacheService } from '../cache/cache.service';
export declare class PricesService {
    private readonly httpClient;
    private readonly cacheService;
    private readonly PRICE_CACHE_TTL;
    constructor(httpClient: HttpClientService, cacheService: CacheService);
    getMarkets(): Promise<any[]>;
}
