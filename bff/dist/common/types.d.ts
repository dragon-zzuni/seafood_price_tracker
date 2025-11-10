export interface Item {
    id: number;
    name_ko: string;
    name_en: string;
    category: string;
}
export interface MarketPrice {
    market: string;
    price: number;
    unit: string;
    date: string;
    tag: 'HIGH' | 'NORMAL' | 'LOW';
    base_price?: number;
    ratio?: number;
}
export interface PriceTrendPoint {
    date: string;
    market: string;
    price: number;
}
export interface ItemDashboard {
    item: {
        id: number;
        name_ko: string;
        name_en: string;
        season: {
            from: number;
            to: number;
        };
        default_origin: string;
    };
    current_prices: MarketPrice[];
    price_trend: {
        period_days: number;
        data: PriceTrendPoint[];
    };
    data_sources: string[];
    is_in_season: boolean;
}
export interface RecognitionResult {
    candidates: Array<{
        item_id: number;
        item_name: string;
        confidence: number;
    }>;
}
