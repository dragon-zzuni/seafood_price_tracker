import { HttpClientService } from '../common/http-client.service';
import { RecognitionResult } from '../common/types';
export declare class RecognitionService {
    private readonly httpClient;
    private readonly MAX_IMAGE_SIZE;
    constructor(httpClient: HttpClientService);
    recognizeImage(imageBuffer: Buffer): Promise<RecognitionResult>;
}
