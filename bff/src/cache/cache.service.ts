import { Injectable, Inject } from '@nestjs/common';
import { RedisClientType } from 'redis';

@Injectable()
export class CacheService {
  constructor(
    @Inject('REDIS_CLIENT')
    private readonly redisClient: RedisClientType,
  ) {}

  /**
   * 캐시에서 데이터 조회
   */
  async get<T>(key: string): Promise<T | null> {
    try {
      const data = await this.redisClient.get(key);
      if (!data) return null;
      return JSON.parse(data) as T;
    } catch (error) {
      console.error(`Cache get error for key ${key}:`, error);
      return null;
    }
  }

  /**
   * 캐시에 데이터 저장
   * @param key 캐시 키
   * @param value 저장할 데이터
   * @param ttl TTL (초 단위)
   */
  async set(key: string, value: any, ttl: number): Promise<void> {
    try {
      await this.redisClient.setEx(key, ttl, JSON.stringify(value));
    } catch (error) {
      console.error(`Cache set error for key ${key}:`, error);
    }
  }

  /**
   * 캐시 삭제
   */
  async del(key: string): Promise<void> {
    try {
      await this.redisClient.del(key);
    } catch (error) {
      console.error(`Cache delete error for key ${key}:`, error);
    }
  }

  /**
   * 패턴에 매칭되는 모든 키 삭제
   */
  async delPattern(pattern: string): Promise<void> {
    try {
      const keys = await this.redisClient.keys(pattern);
      if (keys.length > 0) {
        await this.redisClient.del(keys);
      }
    } catch (error) {
      console.error(`Cache delete pattern error for ${pattern}:`, error);
    }
  }

  /**
   * Cache-Aside 패턴 구현
   * 캐시에 데이터가 있으면 반환, 없으면 fetcher 함수 실행 후 캐시에 저장
   */
  async getOrSet<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl: number,
  ): Promise<T> {
    // 1. 캐시 확인
    const cached = await this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    // 2. 데이터 조회
    const data = await fetcher();

    // 3. 캐시 저장
    await this.set(key, data, ttl);

    return data;
  }
}
