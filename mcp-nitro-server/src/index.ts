import 'reflect-metadata';
import { McpApplicationFactory } from '@nitrostack/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await McpApplicationFactory.create(AppModule, {
    name: 'razorpay_sentinel_nitro',
    version: '1.0.0',
  });
  
  await app.startStdio();
  console.error('[START] NitroStack MCP Server running on stdio');
}

bootstrap();