# 🕹️ Swing Trading Bot Prototype

This is an early-stage prototype for a swing trading bot I'm testing out. Built using Python, the bot uses Alpaca's Market Data API, Redis Streams, and WebSocket streams to:

- Fetch historical bar data
- Store current portfolio positions and EMAs in Redis
- Stream real-time bar data into Redis Streams
- Calculate 21-day and 50-day EMAs (for now, strategy is subject to change)
- Monitor for golden/death cross patterns (for now, strategy is subject to change)
- Make real-time trading decisions based on trends
- Distribute processing across threads using stream consumers

## 🔧 Current Stack

This bot leverages Alpaca’s Market Data API, real-time WebSocket streams, and Redis Streams for inter-process communication. The system uses multithreaded consumers to process bar updates for each stock symbol in parallel, and implements distributed coordination via Redis locks to safely update state and execute trades, to ultimately enable real-time trend detection and execution with minimal latency.

- **Language**: Python 3.11+
- **Market Data**: [Alpaca Market Data API](https://alpaca.markets/)
- **Streaming**: WebSocket + Redis Streams
- **Persistence**: Redis (local or hosted)
- **Libraries**:
  - `pandas` for historical EMA warmup
  - `asyncio`, `websockets` for async stream handling
  - `redis-py` for pub-sub and hash maps
  - `requests` for REST order placement

## 📈 Strategy

This is just a super basic strategy I'm experimenting with (because of the market's volatility right now). 
The idea is to get the basic infrastructure of the project setup so then I can tune my strategy to however I want in the future.

Right now, this prototype implements a **trend-based swing trading strategy**.

A high level overview of this is:

- Monitor EMAs (21 and 50 day)
- If a **golden cross** (EMA21 > EMA50) occurs, **buy**
- If a **death cross** (EMA21 < EMA50) occurs, **sell**

Price updates are streamed into Redis and processed in parallel using per-symbol consumer threads with distributed locks.

## 🧱 Architecture

- `main.py`: Initializes positions and launches all stream producers and consumer threads
- `initializer.py`: Fetches current holdings and writes to Redis (used as the state store)
- `streamBars.py`: Authenticates and streams real-time bar data into Redis Streams
- `processBars.py`: Consumer that listens for new bar data, processes it, updates EMAs, and triggers trades if crossovers are detected
- `redis`: Used for:
  - Locks (to avoid race conditions)
  - EMA and quantity storage (`position:<symbol>`)
  - Streaming bar data (`bar_stream:<symbol>`)

## ✅ Features Completed

- ✅ Historical data bootstrapping via Alpaca REST API
- ✅ Redis-based position persistence
- ✅ Real-time bar streaming via WebSocket
- ✅ Parallel consumer threads using Redis Streams
- ✅ EMA calculation and crossover detection
- ✅ Thread-safe updates with distributed Redis locks

## 🛠️ Roadmap

- ⏳ Add logging + audit trails
- ⏳ Add backtesting framework
- ⏳ Add unit/integration tests
- ⏳ Retry logic for WebSocket drops
- ⏳ Auto-scale based on number of holdings
- ⏳ Explore Docker + deployment automation
- ⏳ Transition to intraday or low-latency strategy
- ⏳ Option to run on AWS Lambda/EventBridge for scheduling

## ⚠️ Disclaimer

This is **not investment advice**. This bot is under active development and is currently in testing. Don't use this lol.
