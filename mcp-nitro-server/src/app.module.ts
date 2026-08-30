import { Module } from '@nitrostack/core';
import { SentinelTools } from './tools/sentinel.tools';

@Module({
  tools: [SentinelTools],
})
export class AppModule {}