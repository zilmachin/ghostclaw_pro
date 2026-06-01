# 🚀 DEPLOYMENT GUIDE - Polymarket AI Agent на VPS

## 📱 **ПОЛНАЯ ИНСТРУКЦИЯ для Samsung A25 + JuiceSSH**

### **ЭТАП 1: ПОДГОТОВКА (5 минут)**

#### Шаг 1.1: Получить API ключи

**1. OpenRouter API Key** (FREE deepseek-chat-v3.1):
- Перейти на https://openrouter.ai
- Sign up → Получить API key
- Скопировать ключ вида: `sk-or-v1-xxxxx`

**2. Telegram Bot Token:**
- В Telegram напиши: `@BotFather`
- `/start` → `/newbot`
- Назвать бота (например: `PolymarketAIBot`)
- Получить token вида: `123456789:ABCDefGHIjklMNOpQRstUVWxyzABC-DEfG`

**3. Telegram Chat ID:**
- Отправить боту `/start`
- В логах bot (или через любой бот-шпион) найти: `chat_id`
- Это твой user ID (обычно числа вида: `123456789`)

**4. Telegram Channel ID (опционально):**
- Если создал канал: `@MyPolymarketChannel`
- ID будет с минусом: `-100123456789`

#### Шаг 1.2: SSH Подключение (JuiceSSH на Samsung A25)

1. Открыть **JuiceSSH**
2. Создать новое соединение:
   - Host: `your_vps_ip` (например `1.2.3.4`)
   - Port: `22`
   - Username: `root`
   - Password: твой пароль VPS
3. Connect!

---

### **ЭТАП 2: УСТАНОВКА (10 минут)**

#### Шаг 2.1: Скопировать код

```bash
cd /root
git clone https://github.com/zilmachin/ghostclaw_pro.git
cd ghostclaw_pro/polymarket-ai-agent
```

#### Шаг 2.2: Создать виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Шаг 2.3: Установить зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Если будут ошибки с `aiogram` - установить отдельно:
```bash
pip install aiogram>=3.0.0
```

---

### **ЭТАП 3: КОНФИГУРАЦИЯ (5 минут)**

#### Шаг 3.1: Создать файл секретов

```bash
sudo mkdir -p /etc/polymarket
sudo nano /etc/polymarket/secrets.env
```

#### Шаг 3.2: Вставить конфиг

Нажать **Ctrl+Shift+V** в nano (paste), затем вставить:

```env
# LLM - OpenRouter (БЕСПЛАТНО)
OPENROUTER_API_KEY=sk-or-v1-your_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIjklMNOpQRstUVWxyzABC-DEfG
TELEGRAM_CHAT_ID=your_user_id
TELEGRAM_CHANNEL_ID=-100your_channel_id

# Polymarket (опционально для реальной торговли)
POLYMARKET_PRIVATE_KEY=0x
POLYMARKET_ADDRESS=0x

# Environment
ENV=production
DEBUG=False

# Features
FEATURE_DRY_RUN=True
FEATURE_REAL_TRADING=False
FEATURE_NEWS_POSTING=True

# Logging
LOG_LEVEL=INFO
```

**Сохранить:** Ctrl+O → Enter → Ctrl+X

#### Шаг 3.3: Установить права доступа

```bash
sudo chmod 600 /etc/polymarket/secrets.env
sudo chown root:root /etc/polymarket/secrets.env
```

---

### **ЭТАП 4: ТЕСТИРОВАНИЕ (5 минут)**

#### Шаг 4.1: Запустить локально (DEV MODE)

```bash
cd /root/ghostclaw_pro/polymarket-ai-agent
source venv/bin/activate
python main.py
```

**Должно вывести:**
```
================================================================================
🤖 Polymarket AI Multi-Agent Orchestrator + Telegram Bot
================================================================================
Environment: production
Debug: False
Dry-run: True
Real trading: False
✅ Configuration validated
✅ Telegram bot initialized
🚀 Orchestrator starting

───────────────────────────────────────────────────────────────────────────────
📊 Orchestration Cycle #1 @ 2026-06-01T10:30:45.123456
───────────────────────────────────────────────────────────────────────────────
...
```

**Если ошибка** → проверить:
1. Все ли API ключи в `/etc/polymarket/secrets.env`?
2. Интернет есть?
3. Python 3.10+?

#### Шаг 4.2: Тест Telegram бота

1. Отправить боту (в Telegram): `/start`
2. Должен ответить бот с приветствием
3. Затем: `/status` - должен показать статус агентов

**Если бот не отвечает:**
- Проверить `TELEGRAM_BOT_TOKEN` в secrets.env
- Проверить интернет
- Проверить логи: `Ctrl+C` → см. последние ошибки

#### Шаг 4.3: Остановить тест

```bash
Ctrl+C
```

---

### **ЭТАП 5: РАЗВЕРТЫВАНИЕ НА VPS (systemd)**

#### Шаг 5.1: Создать пользователя (безопасность)

```bash
sudo useradd -m -s /bin/bash polymarket
sudo chown -R polymarket:polymarket /root/ghostclaw_pro
```

#### Шаг 5.2: Скопировать systemd unit

```bash
sudo cp /root/ghostclaw_pro/polymarket-ai-agent/systemd/polymarket-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
```

#### Шаг 5.3: Запустить как сервис

```bash
sudo systemctl start polymarket-ai.service
sudo systemctl enable polymarket-ai.service  # Автозагрузка

# Проверить статус
sudo systemctl status polymarket-ai.service
```

#### Шаг 5.4: Смотреть логи в реальном времени

```bash
sudo journalctl -u polymarket-ai.service -f
```

---

### **ЭТАП 6: УПРАВЛЕНИЕ ЧЕРЕЗ TELEGRAM**

**Когда система работает, отправить боту:**

| Команда | Результат |
|---------|-----------|
| `/start` | Показать меню |
| `/status` | Статус всех 3 агентов |
| `/stats` | Торговая статистика за 24ч |
| `/stats 7d` | Статистика за 7 дней |
| `/pause` | Приостановить всех агентов |
| `/resume` | Возобновить работу |
| `/help` | Справка по командам |

**Система автоматически:**
- ✅ Отправляет отчет о статусе каждый час
- ✅ Уведомляет о торговых сигналах
- ✅ Постит новости из Polymarket

---

## 📊 **МОНИТОРИНГ И ОТЛАДКА**

### **Просмотр логов**

```bash
# Real-time логи
sudo journalctl -u polymarket-ai.service -f

# Последние 100 строк
sudo journalctl -u polymarket-ai.service -n 100

# Логи за последние 24 часа
sudo journalctl -u polymarket-ai.service --since "24 hours ago"

# Сохранить логи в файл
sudo journalctl -u polymarket-ai.service > /tmp/logs.txt
```

### **Проверить БД (SQLite)**

```bash
cd /root/ghostclaw_pro/polymarket-ai-agent
source venv/bin/activate
sqlite3 data/polymarket.db

# В sqlite3 prompt:
> SELECT COUNT(*) FROM trades;
> SELECT * FROM trades LIMIT 5;
> .quit
```

### **Перезагрузить сервис**

```bash
sudo systemctl restart polymarket-ai.service
```

### **Остановить сервис**

```bash
sudo systemctl stop polymarket-ai.service
```

---

## ⚙️ **НАСТРОЙКА ПАРАМЕТРОВ**

Отредактировать `config.py`:

```bash
cd /root/ghostclaw_pro/polymarket-ai-agent
nano config.py
```

Важные параметры:

```python
MIN_EDGE = 0.08              # Минимальный край (8%)
MIN_CONFIDENCE = 0.65        # Уверенность LLM (65%)
START_DEPOSIT_USDC = 50      # Начальный депозит (50 USDC)
DRY_RUN_DAYS = 7             # Дней перед реальной торговлей

ORCHESTRATOR_INTERVAL = 300  # Интервал (5 минут)
TRADING_AGENT_INTERVAL = 300
NEWS_AGENT_INTERVAL = 600    # Новости каждые 10 минут
```

После изменений:
```bash
sudo systemctl restart polymarket-ai.service
```

---

## 💰 **АКТИВАЦИЯ РЕАЛЬНОЙ ТОРГОВЛИ**

**⚠️ ВАЖНО: сначала минимум 7 дней в DRY-RUN режиме!**

### Шаг 1: Получить Polymarket приватный ключ

1. Создать Polygon кошелек (MetaMask или другой)
2. Получить приватный ключ (никому не давать!)
3. Добавить USDC на Polygon (Polymarket платит газ!)

### Шаг 2: Обновить конфиг

```bash
sudo nano /etc/polymarket/secrets.env
```

Заменить:
```env
POLYMARKET_PRIVATE_KEY=0xyour_private_key
POLYMARKET_ADDRESS=0xyour_wallet_address
FEATURE_DRY_RUN=False
FEATURE_REAL_TRADING=True
```

### Шаг 3: Перезагрузить

```bash
sudo systemctl restart polymarket-ai.service
```

---

## 🆘 **TROUBLESHOOTING**

### Проблема: "Config validation failed"

**Решение:** Проверить все ключи в `/etc/polymarket/secrets.env`
```bash
sudo cat /etc/polymarket/secrets.env
```

### Проблема: Telegram бот не отвечает

**Решение:** Проверить токен и интернет
```bash
sudo systemctl restart polymarket-ai.service
sudo journalctl -u polymarket-ai.service -f | grep -i telegram
```

### Проблема: "OutOfMemory"

**Решение:** VPS слишком слабый. Увеличить RAM или оптимизировать:
```bash
# Уменьшить интервал обновлений
ORCHESTRATOR_INTERVAL=600  # 10 минут вместо 5
```

### Проблема: OpenRouter quota exceeded

**Решение:** Система автоматически переключится на fallback модель. Ждать.

---

## ✅ **ФИНАЛЬНАЯ ЧЕКЛИСТ**

- [ ] API ключи получены
- [ ] Git репо скопирован
- [ ] Зависимости установлены
- [ ] `/etc/polymarket/secrets.env` создан
- [ ] Локальный тест пройден (python main.py)
- [ ] Telegram бот отвечает на команды
- [ ] systemd unit установлен
- [ ] Сервис работает (systemctl status)
- [ ] Логи читаются (journalctl -f)
- [ ] /stats показывает данные

---

## 📞 **ПОДДЕРЖКА**

- GitHub Issues: https://github.com/zilmachin/ghostclaw_pro/issues
- Telegram: Отправить боту `/help`
- Логи: `sudo journalctl -u polymarket-ai.service -n 50`

---

**🎉 ГОТОВО! Система работает 24/7 на твоем VPS!**
