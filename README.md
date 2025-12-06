# Polymarket Insider Trading Tracker

Analysis and tracking system for Polymarket traders to identify insider trading patterns and enable automated position replication.

## 📋 Overview

This project integrates with Polymarket APIs to collect, catalog, and analyze trader and market data, identifying insider trading patterns and enabling automated copy trading in near real-time.

## 🎯 Objectives

### Phase 1 - Base Infrastructure ✅
- **Initial project setup**
- **MySQL database configuration**
- **Polymarket API integration**
- **Data collection system**
  - Trader information
  - Market data
  - Current and historical positions
  - Complete bet history
- **Structured storage**

### Phase 2 - Insider Analysis 🔄
- **Pattern detection algorithms**
- **Trader scoring system**
- **Early movement identification**
- **Analysis dashboard**

### Phase 3 - Copy Trading 🔄
- **Polymarket wallet integration**
- **Automated replication system**
- **Risk management**
- **Real-time notifications**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Polymarket API                          │
│  (Markets, Traders, Positions, Historical Data)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Collection Layer                      │
│  • Market Fetcher                                           │
│  • Trader Tracker                                           │
│  • Position Monitor                                         │
│  • Historical Data Collector                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    MySQL Database                           │
│  • traders          (profiles and statistics)               │
│  • markets          (markets and status)                    │
│  • positions        (current positions)                     │
│  • position_history (position history)                      │
│  • bets             (all bets)                              │
│  • trader_scores    (insider analysis scores)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Analysis Engine (Phase 2)                  │
│  • Pattern Detection                                        │
│  • Insider Scoring                                          │
│  • Early Movement Detection                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Copy Trading System (Phase 3)                │
│  • Position Replication                                     │
│  • Risk Management                                          │
│  • Wallet Integration                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ Database Schema

### Traders
- Profile information
- Performance statistics
- Creation/update timestamps

### Markets
- Market data
- Status (active, resolved, canceled)
- Volume and liquidity
- Timestamps

### Positions
- Current trader positions
- Invested amounts
- Shares held
- Related market

### Position History
- Complete position change history
- Temporal snapshots
- Entry/exit tracking

### Bets
- All individual bets
- Values, odds, timestamps
- Results

### Trader Scores (Phase 2)
- Insider trading score
- Performance metrics
- Identified patterns

## 🚀 Technologies

- **Runtime**: Python 3.11+
- **Database**: MySQL 8.0+
- **API Client**: httpx / requests
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Async**: asyncio / aiohttp
- **Scheduling**: APScheduler / Celery
- **Testing**: pytest
- **Environment**: python-dotenv

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/marcosgabbardo/insiderMarket.git
cd insiderMarket

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip3 install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your MySQL credentials

# Create database in MySQL
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS polymarket_insider;"

# Run migrations
alembic upgrade head

# Initialize the application
python3 -m polymarket_insider init
```

## ⚙️ Configuration

### Prerequisites

- Python 3.11+
- MySQL 8.0+ running on localhost:3306
- pip3

### Environment Setup

Create a `.env` file based on `.env.example`:

```env
# Database (Local MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=polymarket_insider
DB_USER=root
DB_PASSWORD=your_mysql_password

# Polymarket API
POLYMARKET_API_URL=https://gamma-api.polymarket.com
POLYMARKET_API_KEY=your_api_key_if_needed

# Collection Settings
COLLECTION_INTERVAL_MINUTES=5
MAX_TRADERS_TO_TRACK=1000
```

## 🔄 Usage

### Initialize database
```bash
python3 -m polymarket_insider init
```

### Check system status
```bash
python3 -m polymarket_insider status
```

### Collect market data
```bash
python3 -m polymarket_insider collect markets --limit 100 --active-only
```

### Track specific traders
```bash
python3 -m polymarket_insider collect traders <address1> <address2> <address3>
```

### Run insider analysis (Phase 2)
```bash
python3 -m polymarket_insider analyze insiders
```

## 📊 Polymarket API Endpoints

### Main endpoints used:
- `GET /markets` - Market list
- `GET /markets/:id` - Specific market details
- `GET /markets/:id/positions` - Positions in a market
- `GET /positions/:address` - Trader positions
- `GET /trades` - Trade history

Complete documentation: https://docs.polymarket.com

## 🔍 Phase 2 - Insider Detection (Planned)

### Analysis metrics:
- **Early Entry Score**: Traders who enter before significant movements
- **Timing Accuracy**: Timing precision relative to events
- **Volume Pattern**: Abnormal volume patterns
- **Win Rate**: Success rate in specific markets
- **Correlation Analysis**: Correlation between suspicious traders

### Algorithms:
1. Temporal cluster detection
2. Entry order analysis
3. Abnormal volume patterns
4. Cross-market correlation

## 🎯 Phase 3 - Copy Trading (Planned)

### Features:
- Real-time monitoring of top-scored traders
- Automatic position replication
- Configurable risk management
- Telegram/Discord notifications
- Automatic stop-loss
- Portfolio balancing

## 📈 Roadmap

- [x] Architecture definition
- [x] Initial project setup
- [x] MySQL schema implementation
- [x] Polymarket API client
- [x] Data collection system
- [x] CLI interface
- [ ] Unit tests
- [ ] Phase 2: Detection algorithms
- [ ] Phase 2: Analysis dashboard
- [ ] Phase 3: Wallet integration
- [ ] Phase 3: Copy trading engine

## 🤝 Contributing

This is a private project. To contribute, please contact the administrator.

## ⚠️ Disclaimer

This software is provided for educational and research purposes only. Using copy trading strategies involves significant financial risks. Use at your own risk.

**IMPORTANT**: The identification of "insider trading" is based on statistical analysis and patterns, and does not constitute legal proof of illicit activity.

## 📄 License

Proprietary - All rights reserved
