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
exports.PricesService = void 0;
const common_1 = require("@nestjs/common");
const http_client_service_1 = require("../common/http-client.service");
const cache_service_1 = require("../cache/cache.service");
let PricesService = class PricesService {
    constructor(httpClient, cacheService) {
        this.httpClient = httpClient;
        this.cacheService = cacheService;
        this.PRICE_CACHE_TTL = 1800;
    }
    async getMarkets() {
        const cacheKey = 'markets:list';
        return this.cacheService.getOrSet(cacheKey, async () => {
            return this.httpClient.getCoreService('/markets');
        }, 3600);
    }
};
exports.PricesService = PricesService;
exports.PricesService = PricesService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [http_client_service_1.HttpClientService,
        cache_service_1.CacheService])
], PricesService);
//# sourceMappingURL=prices.service.js.map