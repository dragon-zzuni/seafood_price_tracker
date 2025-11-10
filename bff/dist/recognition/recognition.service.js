"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RecognitionService = void 0;
const common_1 = require("@nestjs/common");
const http_client_service_1 = require("../common/http-client.service");
let RecognitionService = class RecognitionService {
    constructor(httpClient) {
        this.httpClient = httpClient;
        this.MAX_IMAGE_SIZE = 5 * 1024 * 1024;
    }
    async recognizeImage(imageBuffer) {
        if (imageBuffer.length > this.MAX_IMAGE_SIZE) {
            throw new common_1.BadRequestException('이미지 크기는 5MB를 초과할 수 없습니다');
        }
        try {
            const result = await this.httpClient.postMlService('/recognize', imageBuffer, {
                'Content-Type': 'image/jpeg',
            });
            return result;
        }
        catch (error) {
            console.error('Image recognition failed:', error);
            throw new common_1.BadRequestException('품목을 인식할 수 없습니다. 직접 검색해주세요');
        }
    }
};
exports.RecognitionService = RecognitionService;
exports.RecognitionService = RecognitionService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [http_client_service_1.HttpClientService])
], RecognitionService);
//# sourceMappingURL=recognition.service.js.map