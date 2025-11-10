import { RecognitionService } from './recognition.service';
import { RecognitionResult } from '../common/types';
export declare class RecognitionController {
    private readonly recognitionService;
    constructor(recognitionService: RecognitionService);
    recognizeImage(file: Express.Multer.File): Promise<RecognitionResult>;
}
