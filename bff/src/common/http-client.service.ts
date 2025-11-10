import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class HttpClientService {
  private readonly coreServiceUrl: string;
  private readonly mlServiceUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.coreServiceUrl = process.env.CORE_SERVICE_URL || 'http://localhost:8000';
    this.mlServiceUrl = process.env.ML_SERVICE_URL || 'http://localhost:8001';
  }

  async getCoreService<T>(path: string): Promise<T> {
    const url = `${this.coreServiceUrl}${path}`;
    const response = await firstValueFrom(
      this.httpService.get<T>(url)
    );
    return response.data;
  }

  async postCoreService<T>(path: string, data: any): Promise<T> {
    const url = `${this.coreServiceUrl}${path}`;
    const response = await firstValueFrom(
      this.httpService.post<T>(url, data)
    );
    return response.data;
  }

  async postMlService<T>(path: string, data: any, headers?: any): Promise<T> {
    const url = `${this.mlServiceUrl}${path}`;
    const response = await firstValueFrom(
      this.httpService.post<T>(url, data, { headers })
    );
    return response.data;
  }
}
