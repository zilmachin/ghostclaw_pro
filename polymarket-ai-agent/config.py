import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv('/etc/polymarket/secrets.env', override=True)
load_dotenv('.env', override=False)

# ============================================================================
# ENVIRONMENT
# ============================================================================
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ENV = os.getenv('ENV', 'development')  # development, staging, production

# ============================================================================
# API KEYS & SECRETS (from /etc/polymarket/secrets.env)
# ============================================================================
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'zilmachin/polymarket-ai-agent')

# Polymarket
POLYMARKET_PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
POLYMARKET_ADDRESS = os.getenv('POLYMARKET_ADDRESS')

# ============================================================================
# PATHS
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
DB_PATH = DATA_DIR / 'polymarket.db'
LOG_FILE = LOGS_DIR / 'orchestrator.log'

# Create directories
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# TRADING CONFIGURATION
# ============================================================================
# Signal filters
MIN_EDGE = float(os.getenv('MIN_EDGE', '0.08'))  # 8% minimum edge
MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '0.65'))  # LLM confidence
MAX_EXPOSURE_PER_CATEGORY = float(os.getenv('MAX_EXPOSURE_PER_CATEGORY', '0.40'))
START_DEPOSIT_USDC = float(os.getenv('START_DEPOSIT_USDC', '50'))
DRY_RUN_DAYS = int(os.getenv('DRY_RUN_DAYS', '7'))

# Kelly criterion
KELLY_FRACTION = float(os.getenv('KELLY_FRACTION', '0.25'))  # 1/4 Kelly

# Platform
PLATFORM_FEE = 0.0  # Polymarket has 0% trading fees

# ============================================================================
# LLM CONFIGURATION (OpenRouter)
# ============================================================================
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'deepseek-chat-v3.1:free')
OPENROUTER_TIMEOUT = 30  # seconds
OPENROUTER_MAX_RETRIES = 3

# Fallback models if main quota exceeded
OPENROUTER_FALLBACK_MODELS = [
    'mistral-7b',
    'llama-2-13b',
]

LLM_TEMPERATURE = 0.7
LLM_TOP_P = 0.9
LLM_MAX_TOKENS = 500

# ============================================================================
# POLYMARKET API
# ============================================================================
POLYMARKET_GAMMA_URL = 'https://gamma-api.polymarket.com'
POLYMARKET_CLOB_URL = 'https://clob.polymarket.com'
POLYMARKET_TIMEOUT = 10

# ============================================================================
# ORCHESTRATOR
# ============================================================================
ORCHESTRATOR_INTERVAL = int(os.getenv('ORCHESTRATOR_INTERVAL', '300'))  # 5 min
TRADING_AGENT_INTERVAL = int(os.getenv('TRADING_AGENT_INTERVAL', '300'))
NEWS_AGENT_INTERVAL = int(os.getenv('NEWS_AGENT_INTERVAL', '600'))  # 10 min
CODEBASE_AGENT_INTERVAL = int(os.getenv('CODEBASE_AGENT_INTERVAL', '3600'))  # 1h

# ============================================================================
# TELEGRAM BOT
# ============================================================================
TELEGRAM_POLLING_TIMEOUT = 30
TELEGRAM_ALLOWED_USERS = [int(uid.strip()) for uid in os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',') if uid.strip()]

# ============================================================================
# DATABASE
# ============================================================================
SQLALCHEMY_DATABASE_URL = f'sqlite:///{DB_PATH}'
SQLALCHEMY_ECHO = DEBUG

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# FEATURES
# ============================================================================
FEATURE_DRY_RUN = os.getenv('FEATURE_DRY_RUN', 'True').lower() == 'true'
FEATURE_REAL_TRADING = os.getenv('FEATURE_REAL_TRADING', 'False').lower() == 'true'
FEATURE_NEWS_POSTING = os.getenv('FEATURE_NEWS_POSTING', 'True').lower() == 'true'
FEATURE_CODEBASE_MONITORING = os.getenv('FEATURE_CODEBASE_MONITORING', 'True').lower() == 'true'

# ============================================================================
# VALIDATION
# ============================================================================
def validate_config():
    """Validate critical configuration"""
    errors = []
    
    if not OPENROUTER_API_KEY:
        errors.append('OPENROUTER_API_KEY not set')
    if not TELEGRAM_BOT_TOKEN:
        errors.append('TELEGRAM_BOT_TOKEN not set')
    if not TELEGRAM_CHAT_ID:
        errors.append('TELEGRAM_CHAT_ID not set')
    
    if FEATURE_REAL_TRADING:
        if not POLYMARKET_PRIVATE_KEY:
            errors.append('POLYMARKET_PRIVATE_KEY required for real trading')
        if not POLYMARKET_ADDRESS:
            errors.append('POLYMARKET_ADDRESS required for real trading')
    
    if errors:
        raise ValueError('Config validation failed:\n' + '\n'.join(f'  - {e}' for e in errors))
    
    print('✅ Configuration validated')

if __name__ == '__main__':
    validate_config()
