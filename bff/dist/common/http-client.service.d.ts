import { HttpService } from '@nestjs/axios';
export declare class HttpClientService {
    private readonly httpService;
    private readonly coreServiceUrl;
    private readonly mlServiceUrl;
    constructor(httpService: HttpService);
    getCoreService<T>(path: string): Promise<T>;
    postCoreService<T>(path: string, data: any): Promise<T>;
    postMlService<T>(path: string, data: any, headers?: any): Promise<T>;
}
