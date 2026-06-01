"""Main entry point - Starts Orchestrator + Telegram Bot"""

import asyncio
import logging
import sys
from pathlib import Path

import config
from orchestrator import MultiAgentOrchestrator
from handlers.telegram_handler import TelegramBotHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    """Start orchestrator with Telegram bot integration"""
    logger = logging.getLogger('main')
    
    logger.info('=' * 80)
    logger.info('🤖 Polymarket AI Multi-Agent Orchestrator + Telegram Bot')
    logger.info('=' * 80)
    logger.info(f'Environment: {config.ENV}')
    logger.info(f'Debug: {config.DEBUG}')
    logger.info(f'Dry-run: {config.FEATURE_DRY_RUN}')
    logger.info(f'Real trading: {config.FEATURE_REAL_TRADING}')
    
    try:
        config.validate_config()
        logger.info('✅ Configuration validated')
    except ValueError as e:
        logger.error(f'Config validation failed: {e}')
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    # Create Telegram bot handler
    telegram_handler = TelegramBotHandler(orchestrator)
    logger.info('✅ Telegram bot initialized')
    
    # Run orchestrator and bot in parallel
    try:
        await asyncio.gather(
            orchestrator.start(),
            telegram_handler.start_polling(),
            telegram_handler.send_status_report(),
        )
    except KeyboardInterrupt:
        logger.info('Shutdown signal received')
        await orchestrator.stop()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n👋 Goodbye!')
        sys.exit(0)
    except Exception as e:
        print(f'Fatal error: {e}')
        sys.exit(1)
