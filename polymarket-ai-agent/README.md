# Polymarket AI Multi-Agent Orchestrator

🤖 **Autonomous Trading + News Agent System**

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│              VPS (2GB RAM, 32GB) - systemd Daemon                                       │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │         Multi-Agent Orchestrator (master)                                        │   │
│  │  - Coordinate 3 specialized agents                                               │   │
│  │  - State management & recovery                                                   │   │
│  │  - Logging & monitoring                                                          │   │
│  └──┬─────────────────────────────────────────┬──────────────────────┬──────────────┘   │
│     │                                         │                      │                  │
│  ┌──▼─────────────┐  ┌────────────────────┐  ┌─▼────────────────────▼┐                 │
│  │ TradingAgent   │  │  NewsAgent         │  │ CodebaseAgent        │                 │
│  │ evaluate       │  │ auto-post news     │  │ prep codebase        │                 │
│  │ execute trades │  │ generate content   │  │ analyze struct       │                 │
│  └──┬─────────────┘  └────────┬───────────┘  └─┬────────────────────┘                 │
│     │                        │               │                                        │
│  ┌──▼──────────────────────────▼───────────────▼─────────────────────────────────────┐ │
│  │              LLM Client (OpenRouter)                                              │ │
│  │  - deepseek-chat-v3.1:free (priority)                                            │ │
│  │  - Fallback models on quota                                                      │ │
│  └──▼──────────────────────────▲───────────────▲─────────────────────────────────────┘ │
│     │                          │               │                                       │
│  ┌──▼──────────┐  ┌────────────▼──────┐  ┌────▼──────────────────────────────┐        │
│  │ Polymarket  │  │ Telegram Bot API  │  │ GitHub / Local File System        │        │
│  │ Gamma API   │  │ (group + channel) │  │                                  │        │
│  └─────────────┘  └───────────────────┘  └──────────────────────────────────┘        │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐  │
│  │           SQLite Database + Logs                                               │  │
│  │  - trades (id, market_id, side, stake, pnl, ...)                              │  │
│  │  - news_posts (id, title, content, posted_at, ...)                            │  │
│  │  - codebase_snapshots (id, hash, structure, ...)                              │  │
│  └────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────┘
  systemd unit (polymarket-ai.service)
  EnvironmentFile: /etc/polymarket/secrets.env (API keys)
```

## 📁 Project Structure

```
polymarket-ai-agent/
├── README.md
├── requirements.txt
├── config.py                      # Configuration & environment
├── main.py                        # Entry point - starts orchestrator
│
├── orchestrator/
│   ├── __init__.py
│   ├── multi_agent.py            # ⭐ Main orchestrator (coordinate agents)
│   ├── base_agent.py             # Abstract Agent class
│   ├── agent_trading.py          # TradingAgent (evaluate + execute)
│   ├── agent_news.py             # NewsAgent (Telegram auto-posting)
│   └── agent_codebase.py         # CodebaseAgent (repo analysis)
│
├── skills/
│   ├── __init__.py
│   ├── value_betting.py          # ValueBettingSkill
│   ├── news_generation.py        # NewsGenerationSkill
│   └── code_analyzer.py          # CodebaseAnalysisSkill
│
├── llm/
│   ├── __init__.py
│   ├── openrouter_client.py      # OpenRouter API wrapper
│   ├── classifier.py             # LLM probability classification
│   └── prompt_templates.py       # Prompts for each agent
│
├── polymarket/
│   ├── __init__.py
│   ├── gamma_api.py              # Polymarket Gamma API client
│   ├── resolver.py               # Market resolution logic
│   └── execution_sim.py          # CLOB price simulation
│
├── risk/
│   ├── __init__.py
│   └── budget.py                 # Risk management & Kelly criterion
│
├── handlers/
│   ├── __init__.py
│   ├── telegram_handler.py       # Telegram bot commands
│   ├── stats_handler.py          # /stats command
│   └── webhook_handler.py        # Webhook for GitHub updates
│
├── db/
│   ├── __init__.py
│   ├── models.py                 # SQLite ORM models
│   ├── schema.py                 # Database schema
│   └── migrations.py             # Schema migrations
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                 # Centralized logging
│   ├── retry.py                  # Retry logic
│   └── validators.py             # Input validation
│
├── systemd/
│   └── polymarket-ai.service     # systemd unit file
│
└── tests/
    ├── __init__.py
    ├── test_orchestrator.py
    ├── test_agents.py
    ├── test_skills.py
    └── test_integration.py
```

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/zilmachin/polymarket-ai-agent.git
cd polymarket-ai-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Create secrets file
sudo mkdir -p /etc/polymarket
sudo nano /etc/polymarket/secrets.env
```

Add:
```
OPENROUTER_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_CHANNEL_ID=your_channel_id
GITHUB_TOKEN=your_github_token
POLYMARKET_PRIVATE_KEY=your_pk_here
POLYMARKET_ADDRESS=your_address
```

### 3. Run Locally (Dev Mode)

```bash
python main.py --dev
```

### 4. Deploy on VPS (systemd)

```bash
sudo cp systemd/polymarket-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable polymarket-ai.service
sudo systemctl start polymarket-ai.service
sudo journalctl -u polymarket-ai.service -f
```

## 🤖 Three Agents

### **1. TradingAgent**
- **Role**: Identify profitable trades on Polymarket
- **Flow**:
  1. Fetch markets from Gamma API
  2. Classify probability using LLM (OpenRouter)
  3. Calculate edge (real_edge = p_model - market_price - fees)
  4. Simulate execution (CLOB.calculateMarketPrice)
  5. Apply risk budget checks
  6. Execute trade if edge >= 0.08
  7. Log to SQLite

### **2. NewsAgent**
- **Role**: Auto-post relevant news to Telegram
- **Flow**:
  1. Monitor Polymarket question titles (market updates)
  2. Generate analytical post using LLM
  3. Format with hashtags, emoji, Omar Khayyam-style title
  4. Post to group + channel
  5. Track engagement

### **3. CodebaseAgent**
- **Role**: Prepare codebase for autonomous deployment
- **Flow**:
  1. Analyze GitHub repo structure
  2. Check for missing configs/secrets
  3. Validate dependencies (requirements.txt)
  4. Generate deployment checklist
  5. Create pre-flight validation script
  6. Report readiness % to Telegram

## 🔄 Orchestrator Workflow

```python
while True:
    # 1. Check system health
    health = orchestrator.check_health()
    
    # 2. TradingAgent: Scout for trades
    trading_signals = trading_agent.run()
    
    # 3. NewsAgent: Check for updates
    news_posts = news_agent.run()
    
    # 4. CodebaseAgent: Validate readiness
    codebase_status = codebase_agent.run()
    
    # 5. Persist results
    db.store(trading_signals, news_posts, codebase_status)
    
    # 6. Send status to Telegram
    telegram.send_status_report()
    
    # 7. Wait & retry
    sleep(config.ORCHESTRATOR_INTERVAL)  # default: 5 min
```

## 📊 Signal Data Structure

```python
@dataclass
class TradingSignal:
    market_id: str
    side: str              # BUY or SELL
    p_model: float         # LLM probability
    market_price: float
    estimated_fill_price: float  # From CLOB
    total_cost: float
    theoretical_edge: float
    real_edge: float
    stake: float           # Kelly-based
    confidence: float      # LLM confidence
    category: str
    timestamp: datetime
```

## 💰 Kelly Criterion (Binary Markets)

```
Optimal stake = 0.25 * f_star * bankroll

Where:
  f_star = (p*b - (1-p)) / b
  b = (1 - price) / price
  p = LLM-estimated probability
  0.25 = safety factor (quarter Kelly)
```

## ⚙️ Configuration

All in `config.py`:

```python
MIN_EDGE = 0.08              # 8% minimum edge
MIN_CONFIDENCE = 0.65        # LLM confidence threshold
MAX_EXPOSURE_PER_CATEGORY = 0.40  # 40% exposure cap
START_DEPOSIT_USDC = 50      # Initial bankroll
DRY_RUN_DAYS = 7             # Pre-launch dry run
ORCHESTRATOR_INTERVAL = 300  # Run every 5 minutes
OPENROUTER_MODEL = "deepseek-chat-v3.1:free"
```

## 🔐 Security

- **No private keys in code**: All secrets in `/etc/polymarket/secrets.env`
- **systemd EnvironmentFile**: Keys loaded at runtime
- **Read-only database**: SQLite with WAL mode
- **Rate limiting**: OpenRouter quota management
- **Audit log**: All trades/posts logged with timestamps

## 📈 Monitoring

```bash
# View logs (real-time)
sudo journalctl -u polymarket-ai.service -f

# Check database
sqlite3 data/polymarket.db "SELECT COUNT(*) FROM trades;"

# Telegram stats
/stats           # Last 24h
/stats 7d        # Last 7 days
/stats 30d       # Last 30 days
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/test_agents.py -v
python -m pytest tests/test_integration.py -v --live  # Real Gamma API
```

## ✨ Key Features

✅ **Multi-Agent Coordination**: Orchestrator manages 3 independent agents  
✅ **OpenRouter Integration**: Free model priority (deepseek-chat-v3.1:free)  
✅ **Polymarket Native**: Uses Gamma API + CLOB simulator  
✅ **Risk Management**: Kelly criterion + category exposure caps  
✅ **Telegram Notifications**: Commands + auto-posts + status reports  
✅ **Autonomous Trading**: Dry-run → real execution pipeline  
✅ **GitHub Integration**: Webhook for codebase updates  
✅ **SQLite Persistence**: Trades, posts, snapshots logged  
✅ **systemd Deployment**: Production-ready on VPS  
✅ **Zero-Cost**: Free models + no platform trading fees  

## 🔗 External APIs

- **OpenRouter**: https://openrouter.ai (free deepseek-chat-v3.1)
- **Polymarket Gamma**: https://gamma-api.polymarket.com
- **Telegram Bot API**: Official Python library (aiogram)
- **GitHub API**: For codebase analysis webhooks

## ⚠️ Disclaimers

- **NOT financial advice**. Use at your own risk.
- **Dry-run mandatory**: Min 7 days before real trading.
- **Small initial deposit**: Start with 50 USDC for risk management.
- **Monitor logs**: Check `/var/log/polymarket/` regularly.

## 📞 Support

- Telegram: `/help` or `/status`
- GitHub Issues: Report bugs
- Logs: `/var/log/polymarket/orchestrator.log`

---

**Made with ❤️ for autonomous trading on Polymarket**
