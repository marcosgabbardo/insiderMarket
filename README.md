# Polymarket Insider Trading Tracker

Sistema de análise e rastreamento de traders no Polymarket para identificação de padrões de insider trading e replicação automática de posições.

## 📋 Visão Geral

Este projeto integra-se com as APIs do Polymarket para coletar, catalogar e analisar dados de traders e mercados, identificando padrões de insider trading e permitindo copy trading automatizado em tempo quase real.

## 🎯 Objetivos

### Phase 1 - Base Infrastructure ✅
- **Setup inicial do projeto**
- **Configuração de banco de dados MySQL**
- **Integração com Polymarket API**
- **Sistema de coleta de dados**
  - Informações de traders
  - Dados de mercados
  - Posições atuais e históricas
  - Histórico completo de apostas
- **Armazenamento estruturado**

### Phase 2 - Insider Analysis 🔄
- **Algoritmos de detecção de padrões**
- **Sistema de pontuação de traders**
- **Identificação de movimentos antecipados**
- **Dashboard de análise**

### Phase 3 - Copy Trading 🔄
- **Integração com wallet Polymarket**
- **Sistema de replicação automatizada**
- **Gestão de risco**
- **Notificações em tempo real**

## 🏗️ Arquitetura

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
│  • traders          (perfis e estatísticas)                 │
│  • markets          (mercados e status)                     │
│  • positions        (posições atuais)                       │
│  • position_history (histórico de posições)                 │
│  • bets             (todas as apostas)                      │
│  • trader_scores    (pontuação insider analysis)            │
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

## 🗄️ Schema do Banco de Dados

### Traders
- Informações de perfil
- Estatísticas de performance
- Timestamp de criação/atualização

### Markets
- Dados do mercado
- Status (ativo, resolvido, cancelado)
- Volumes e liquidez
- Timestamps

### Positions
- Posições atuais dos traders
- Valores investidos
- Shares detidas
- Mercado relacionado

### Position History
- Histórico completo de mudanças de posição
- Snapshot temporal
- Tracking de entradas/saídas

### Bets
- Todas as apostas individuais
- Valores, odds, timestamps
- Resultados

### Trader Scores (Phase 2)
- Pontuação de insider trading
- Métricas de performance
- Padrões identificados

## 🚀 Tecnologias

- **Runtime**: Python 3.11+
- **Database**: MySQL 8.0+
- **API Client**: httpx / requests
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Async**: asyncio / aiohttp
- **Containerização**: Docker + Docker Compose
- **Agendamento**: APScheduler / Celery
- **Testing**: pytest
- **Environment**: python-dotenv

## 📦 Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd insiderMarket

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Inicie o banco de dados (Docker)
docker-compose up -d mysql

# Execute migrations
alembic upgrade head

# Inicie a aplicação
python main.py
```

## ⚙️ Configuração

Crie um arquivo `.env` baseado em `.env.example`:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=polymarket_insider
DB_USER=root
DB_PASSWORD=your_password

# Polymarket API
POLYMARKET_API_URL=https://gamma-api.polymarket.com
POLYMARKET_API_KEY=your_api_key_if_needed

# Collection Settings
COLLECTION_INTERVAL_MINUTES=5
MAX_TRADERS_TO_TRACK=1000
```

## 🔄 Uso

### Coletar dados de mercados
```bash
python -m src.collectors.markets
```

### Rastrear traders específicos
```bash
python -m src.collectors.traders --addresses <address1>,<address2>
```

### Atualizar posições históricas
```bash
python -m src.collectors.history
```

### Executar análise de insiders (Phase 2)
```bash
python -m src.analysis.insider_detection
```

## 📊 Endpoints da API Polymarket

### Principais endpoints utilizados:
- `GET /markets` - Lista de mercados
- `GET /markets/:id` - Detalhes de mercado específico
- `GET /markets/:id/positions` - Posições em um mercado
- `GET /positions/:address` - Posições de um trader
- `GET /trades` - Histórico de trades

Documentação completa: https://docs.polymarket.com

## 🔍 Phase 2 - Insider Detection (Planejado)

### Métricas de análise:
- **Early Entry Score**: Traders que entram antes de movimentos significativos
- **Timing Accuracy**: Precisão de timing em relação a eventos
- **Volume Pattern**: Padrões de volume anormais
- **Win Rate**: Taxa de acerto em mercados específicos
- **Correlation Analysis**: Correlação entre traders suspeitos

### Algoritmos:
1. Detecção de clusters temporais
2. Análise de ordem de entrada
3. Padrões de volume anormal
4. Cross-market correlation

## 🎯 Phase 3 - Copy Trading (Planejado)

### Features:
- Monitoramento em tempo real de traders top-scored
- Replicação automática de posições
- Gestão de risco configurable
- Notificações via Telegram/Discord
- Stop-loss automático
- Portfolio balancing

## 📈 Roadmap

- [x] Definição de arquitetura
- [x] Setup inicial do projeto
- [ ] Implementação do schema MySQL
- [ ] Cliente API Polymarket
- [ ] Sistema de coleta de dados
- [ ] Testes unitários básicos
- [ ] Docker setup completo
- [ ] Phase 2: Algoritmos de detecção
- [ ] Phase 2: Dashboard de análise
- [ ] Phase 3: Wallet integration
- [ ] Phase 3: Copy trading engine

## 🤝 Contribuição

Este é um projeto privado. Para contribuir, entre em contato com o administrador.

## ⚠️ Disclaimer

Este software é fornecido para fins educacionais e de pesquisa. O uso de estratégias de copy trading envolve riscos financeiros significativos. Use por sua própria conta e risco.

**IMPORTANTE**: A identificação de "insider trading" é baseada em análise estatística e padrões, não constituindo prova legal de atividade ilícita.

## 📄 Licença

Proprietary - Todos os direitos reservados
