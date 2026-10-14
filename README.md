
# Alpha Trading Bot

A Python cryptocurrency price-monitoring bot that collects prices
from CoinGecko and sends informational alerts to Discord.

## Requirements

- Python 3.10 or newer
- Internet connection
- A Discord webhook if you want Discord alerts

## Installation on Windows

Open Command Prompt inside this project folder.

Create a virtual environment:

    py -m venv .venv

Activate it:

    .venv\Scripts\activate

Install dependencies:

    python -m pip install -r requirements.txt

Copy the configuration template:

    copy .env.example .env

Open the configuration:

    notepad .env

Add your private Discord webhook URL and save the file.

Run the bot:

    python alpha_bot.py

## Configuration

Edit `.env` to change the cryptocurrency, currency, polling interval,
drop threshold, and alert cooldown.

For example, CRYPTO_ID=ethereum monitors Ethereum.

The bot needs 10 previous price samples by default before it can
compare a new price with its rolling baseline. At a 60-second
interval, this takes approximately 10 minutes.

## Important notes

- This bot monitors prices; it does not execute trades.
- A price-drop alert is not a guaranteed buy or sell signal.
- CoinGecko may impose rate limits or experience downtime.
- Keep `.env` private. Never publish your Discord webhook URL.
- SQLite is suitable for this starter project, not every production
  deployment.
- Before launching a public SaaS, add automated tests, authentication,
  monitoring, managed secrets, deployment configuration, and appropriate
  database and API-rate-limit handling.

# Alpha Trading Bot

A Python cryptocurrency price-monitoring bot that collects prices
from CoinGecko and sends informational alerts to Discord.

## Requirements

- Python 3.10 or newer
- Internet connection
- A Discord webhook if you want Discord alerts

## Installation on Windows

Open Command Prompt inside this project folder.

Create a virtual environment:

    py -m venv .venv

Activate it:

    .venv\Scripts\activate

Install dependencies:

    python -m pip install -r requirements.txt

Copy the configuration template:

    copy .env.example .env

Open the configuration:

    notepad .env

Add your private Discord webhook URL and save the file.

Run the bot:

    python alpha_bot.py

## Configuration

Edit `.env` to change the cryptocurrency, currency, polling interval,
drop threshold, and alert cooldown.

For example, CRYPTO_ID=ethereum monitors Ethereum.

The bot needs 10 previous price samples by default before it can
compare a new price with its rolling baseline. At a 60-second
interval, this takes approximately 10 minutes.

## Important notes

- This bot monitors prices; it does not execute trades.
- A price-drop alert is not a guaranteed buy or sell signal.
- CoinGecko may impose rate limits or experience downtime.
- Keep `.env` private. Never publish your Discord webhook URL.
- SQLite is suitable for this starter project, not every production
  deployment.
- Before launching a public SaaS, add automated tests, authentication,
  monitoring, managed secrets, deployment configuration, and appropriate
  database and API-rate-limit handling.
