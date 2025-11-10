import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { RecognitionController } from './recognition.controller';
import { RecognitionService } from './recognition.service';
import { HttpClientService } from '../common/http-client.service';

@Module({
  imports: [HttpModule],
  controllers: [RecognitionController],
  providers: [RecognitionService, HttpClientService],
})
export class RecognitionModule {}
