"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@nestjs/core");
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const app_module_1 = require("./app.module");
const http_exception_filter_1 = require("./common/filters/http-exception.filter");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule);
    app.enableCors();
    app.useGlobalPipes(new common_1.ValidationPipe({
        whitelist: true,
        transform: true,
    }));
    app.useGlobalFilters(new http_exception_filter_1.HttpExceptionFilter());
    const config = new swagger_1.DocumentBuilder()
        .setTitle('Seafood Price Tracker API')
        .setDescription('BFF API for Seafood Price Tracker Mobile App')
        .setVersion('1.0')
        .addTag('items', '품목 관련 API')
        .addTag('prices', '가격 관련 API')
        .addTag('recognition', '이미지 인식 API')
        .build();
    const document = swagger_1.SwaggerModule.createDocument(app, config);
    swagger_1.SwaggerModule.setup('api/docs', app, document);
    await app.listen(3000);
    console.log('BFF is running on http://localhost:3000');
    console.log('Swagger documentation: http://localhost:3000/api/docs');
}
bootstrap();
//# sourceMappingURL=main.js.map