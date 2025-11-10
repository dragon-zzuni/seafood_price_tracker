import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // CORS 설정
  app.enableCors();
  
  // Validation 파이프 설정
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    transform: true,
  }));
  
  // 전역 예외 필터 설정
  app.useGlobalFilters(new HttpExceptionFilter());
  
  // Swagger 문서 설정
  const config = new DocumentBuilder()
    .setTitle('Seafood Price Tracker API')
    .setDescription('BFF API for Seafood Price Tracker Mobile App')
    .setVersion('1.0')
    .addTag('items', '품목 관련 API')
    .addTag('prices', '가격 관련 API')
    .addTag('recognition', '이미지 인식 API')
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api/docs', app, document);
  
  await app.listen(3000);
  console.log('BFF is running on http://localhost:3000');
  console.log('Swagger documentation: http://localhost:3000/api/docs');
}
bootstrap();
