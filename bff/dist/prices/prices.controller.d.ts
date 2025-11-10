import { PricesService } from './prices.service';
export declare class PricesController {
    private readonly pricesService;
    constructor(pricesService: PricesService);
    getMarkets(): Promise<any[]>;
}
