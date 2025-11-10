import { ItemsService } from './items.service';
import { Item, ItemDashboard } from '../common/types';
export declare class ItemsController {
    private readonly itemsService;
    constructor(itemsService: ItemsService);
    searchItems(query: string): Promise<{
        items: Item[];
    }>;
    getItem(id: number): Promise<Item>;
    getDashboard(id: number, date?: string): Promise<ItemDashboard>;
}
