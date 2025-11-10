import { Controller, Get, Param, Query, ParseIntPipe } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiQuery, ApiParam } from '@nestjs/swagger';
import { ItemsService } from './items.service';
import { Item, ItemDashboard } from '../common/types';

@ApiTags('items')
@Controller('api/items')
export class ItemsController {
  constructor(private readonly itemsService: ItemsService) {}

  @Get()
  @ApiOperation({ summary: '품목 검색 (자동완성)' })
  @ApiQuery({ name: 'query', description: '검색어', required: true })
  async searchItems(@Query('query') query: string): Promise<{ items: Item[] }> {
    const items = await this.itemsService.searchItems(query);
    return { items };
  }

  @Get(':id')
  @ApiOperation({ summary: '품목 상세 조회' })
  @ApiParam({ name: 'id', description: '품목 ID' })
  async getItem(@Param('id', ParseIntPipe) id: number): Promise<Item> {
    return this.itemsService.getItemById(id);
  }

  @Get(':id/dashboard')
  @ApiOperation({ summary: '품목 대시보드 조회' })
  @ApiParam({ name: 'id', description: '품목 ID' })
  @ApiQuery({ name: 'date', description: '조회 날짜 (YYYY-MM-DD)', required: false })
  async getDashboard(
    @Param('id', ParseIntPipe) id: number,
    @Query('date') date?: string,
  ): Promise<ItemDashboard> {
    return this.itemsService.getItemDashboard(id, date);
  }
}
