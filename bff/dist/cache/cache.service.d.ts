import { RedisClientType } from 'redis';
export declare class CacheService {
    private readonly redisClient;
    constructor(redisClient: RedisClientType);
    get<T>(key: string): Promise<T | null>;
    set(key: string, value: any, ttl: number): Promise<void>;
    del(key: string): Promise<void>;
    delPattern(pattern: string): Promise<void>;
    getOrSet<T>(key: string, fetcher: () => Promise<T>, ttl: number): Promise<T>;
}
