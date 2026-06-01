"""Telegram Bot Handler - Integrates orchestrator with Telegram"""

import logging
from typing import Optional
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

import config
from orchestrator import MultiAgentOrchestrator


class TelegramBotHandler:
    """Handles Telegram bot commands and status updates"""

    def __init__(self, orchestrator: MultiAgentOrchestrator):
        self.orchestrator = orchestrator
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        self.logger = logging.getLogger('telegram.bot')
        
        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all command handlers"""
        self.dp.message.register(self.handle_start, Command('start'))
        self.dp.message.register(self.handle_status, Command('status'))
        self.dp.message.register(self.handle_stats, Command('stats'))
        self.dp.message.register(self.handle_help, Command('help'))
        self.dp.message.register(self.handle_pause, Command('pause'))
        self.dp.message.register(self.handle_resume, Command('resume'))

    async def handle_start(self, message: Message):
        """Handle /start command"""
        self.logger.info(f'User {message.from_user.id}: /start')
        await message.reply(
            '🤖 **Polymarket AI Multi-Agent Bot** is running!\n\n'
            'Commands:\n'
            '/status - System status\n'
            '/stats - Trading statistics\n'
            '/help - Help\n'
            '/pause - Pause agents\n'
            '/resume - Resume agents',
            parse_mode='Markdown'
        )

    async def handle_status(self, message: Message):
        """Handle /status command"""
        self.logger.info(f'User {message.from_user.id}: /status')
        
        status = self.orchestrator.get_status()
        
        text = f"""
🔍 **Orchestrator Status**

Running: {'✅ Yes' if status['is_running'] else '❌ No'}
Cycles: {status['cycle_count']}
Time: {datetime.now().isoformat()}

**Agents:**
"""
        
        for agent_status in status['agents']:
            text += f"\n{agent_status['name']}:\n"
            text += f"  Status: {agent_status['status']}\n"
            text += f"  Runs: {agent_status['run_count']}\n"
            text += f"  Last: {agent_status['last_run'] or 'Never'}\n"
        
        await message.reply(text, parse_mode='Markdown')

    async def handle_stats(self, message: Message):
        """Handle /stats command - trading statistics"""
        self.logger.info(f'User {message.from_user.id}: /stats')
        
        # TODO: Query database for stats
        text = """
📊 **Trading Statistics**

Last 24h:
  Signals: 0
  Executed: 0
  P&L: $0.00
  Win Rate: 0%

Last 7d:
  Signals: 0
  Executed: 0
  P&L: $0.00
  ROI: 0%

Total:
  Signals: 0
  Executed: 0
  P&L: $0.00
"""
        
        await message.reply(text, parse_mode='Markdown')

    async def handle_help(self, message: Message):
        """Handle /help command"""
        self.logger.info(f'User {message.from_user.id}: /help')
        
        text = """
💡 **Help**

**Commands:**
/start - Start bot
/status - Show orchestrator status
/stats [period] - Show trading stats (24h, 7d, 30d)
/pause - Pause all agents
/resume - Resume all agents
/help - Show this help

**Features:**
🎯 TradingAgent - Identifies profitable Polymarket trades
📰 NewsAgent - Auto-posts market updates to Telegram
🔧 CodebaseAgent - Validates deployment readiness

**GitHub:**
https://github.com/zilmachin/ghostclaw_pro

**Support:**
Contact admin for issues
"""
        
        await message.reply(text, parse_mode='Markdown')

    async def handle_pause(self, message: Message):
        """Handle /pause command - pause all agents"""
        self.logger.info(f'User {message.from_user.id}: /pause')
        
        await self.orchestrator.stop()
        await message.reply('⏸️ All agents paused')

    async def handle_resume(self, message: Message):
        """Handle /resume command - resume agents"""
        self.logger.info(f'User {message.from_user.id}: /resume')
        
        for agent in self.orchestrator.agents:
            await agent.resume()
        
        await message.reply('▶️ All agents resumed')

    async def send_status_report(self):
        """Send periodic status report to Telegram"""
        while True:
            try:
                status = self.orchestrator.get_status()
                
                text = f"""
📊 **Orchestrator Status Report**

Cycles: {status['cycle_count']}
Time: {datetime.now().isoformat()}

**Agent Status:**
"""
                
                for agent_status in status['agents']:
                    text += f"\n{agent_status['name']}: {agent_status['status']} ({agent_status['run_count']} runs)"
                
                await self.bot.send_message(
                    chat_id=config.TELEGRAM_CHAT_ID,
                    text=text,
                    parse_mode='Markdown'
                )
                
                # Report every 1 hour
                await asyncio.sleep(3600)
            
            except Exception as e:
                self.logger.error(f'Error sending status report: {e}')
                await asyncio.sleep(60)

    async def send_signal_notification(self, signal):
        """Send trading signal notification"""
        text = f"""
🎯 **Trading Signal**

Market: {signal.market_id}
Side: {signal.side}
Probability: {signal.p_model:.2%}
Edge: {signal.real_edge:.2%}
Stake: ${signal.stake:.2f}
Confidence: {signal.confidence:.2%}

Time: {signal.timestamp.isoformat()}
"""
        
        try:
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=text,
                parse_mode='Markdown'
            )
        except Exception as e:
            self.logger.error(f'Error sending signal notification: {e}')

    async def send_news_post(self, title: str, content: str):
        """Send news post to Telegram group and channel"""
        text = f"""
📰 **{title}**

{content}

Time: {datetime.now().isoformat()}
"""
        
        try:
            # Send to group
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=text,
                parse_mode='Markdown'
            )
            
            # Send to channel
            await self.bot.send_message(
                chat_id=config.TELEGRAM_CHANNEL_ID,
                text=text,
                parse_mode='Markdown'
            )
        except Exception as e:
            self.logger.error(f'Error sending news post: {e}')

    async def start_polling(self):
        """Start Telegram bot polling"""
        self.logger.info('Starting Telegram bot polling')
        
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            self.logger.error(f'Polling error: {e}')
