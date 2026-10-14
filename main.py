import asyncio
import logging
import os
import time
import aiohttp
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

# --- CONFIGURATION ---
SYMBOLS = [s.strip().upper() for s in os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")]
ALERT_THRESHOLD_PERCENT = float(os.getenv("ALERT_THRESHOLD_PERCENT", "1.5"))
VOLUME_SPIKE_MULTIPLIER = float(os.getenv("VOLUME_SPIKE_MULTIPLIER", "2.5"))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "300"))  # 5 minutes de cooldown

# --- CONFIGURATION DES LOGS ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("PulseSignalPro")

# Stockage en mémoire
price_history = {symbol: [] for symbol in SYMBOLS}
last_alert_time = {symbol: 0 for symbol in SYMBOLS}


async def send_discord_embed(session: aiohttp.ClientSession, symbol: str, price: float, change: float, alert_type: str, extra_info: str = ""):
    """Envoie un message formaté (Embed) sur le webhook Discord."""
    if not DISCORD_WEBHOOK_URL:
        log.warning("DISCORD_WEBHOOK_URL est manquant. Alerte non envoyée.")
        return

    is_bullish = change > 0 or alert_type == "BULLISH_PUMP"
    color = 0x2ECC71 if is_bullish else 0xE74C3C  # Vert ou Rouge

    embed = {
        "title": f"🚨 {symbol} — {alert_type.replace('_', ' ')}",
        "description": f"**Mouvement détecté sur {symbol} !**\n{extra_info}",
        "color": color,
        "fields": [
            {"name": "💵 Prix Actuel", "value": f"${price:,.2f}", "inline": True},
            {"name": "📊 Variation (15m)", "value": f"{change:+.2f}%", "inline": True},
            {"name": "⏱ Timestamp", "value": f"<t:{int(time.time())}:R>", "inline": True},
        ],
        "footer": {"text": "PulseSignal Pro Engine • Real-time Alpha"},
    }

    payload = {"username": "PulseSignal Alpha", "embeds": [embed]}

    try:
        async with session.post(DISCORD_WEBHOOK_URL, json=payload) as resp:
            if resp.status in (200, 204):
                log.info(f"[{symbol}] Alerte Discord envoyée avec succès.")
            else:
                log.warning(f"Discord a retourné un statut HTTP {resp.status}")
    except Exception as e:
        log.error(f"Erreur lors de l'envoi de l'alerte Discord : {e}")


async def analyze_market_data(session: aiohttp.ClientSession, symbol: str, price: float, volume: float):
    """Analyse l'historique des prix, calcule la variation et déclenche les alertes."""
    now = time.time()
    history = price_history[symbol]
    
    # Ajouter la nouvelle donnée (timestamp, prix, volume)
    history.append((now, price, volume))
    
    # Conserver uniquement les 15 dernières minutes (900 secondes)
    price_history[symbol] = [p for p in history if now - p[0] <= 900]
    
    # Attendre d'avoir assez de données pour comparer
    if len(price_history[symbol]) < 5:
        return

    oldest_price = price_history[symbol][0][1]
    avg_volume = sum(p[2] for p in price_history[symbol]) / len(price_history[symbol])
    
    price_change = ((price - oldest_price) / oldest_price) * 100
    
    log.info(f"[{symbol}] Prix: ${price:,.2f} | Var (15m): {price_change:+.2f}%")

    # Vérification du Cooldown (pour éviter de spammer le salon)
    if now - last_alert_time[symbol] < COOLDOWN_SECONDS:
        return

    # Détection de Pump ou Dump
    if abs(price_change) >= ALERT_THRESHOLD_PERCENT:
        alert_type = "BULLISH_PUMP" if price_change > 0 else "BEARISH_DUMP"
        extra = "Variation de prix significative détectée sur la période."
        
        # Détection d'un pic de volume en plus
        if avg_volume > 0 and volume > avg_volume * VOLUME_SPIKE_MULTIPLIER:
            extra += f"\n🔥 **PIC DE VOLUME !** (Volume {volume/avg_volume:.1f}x supérieur à la moyenne)"

        last_alert_time[symbol] = now
        await send_discord_embed(session, symbol, price, price_change, alert_type, extra)


async def main():
    log.info("🚀 Démarrage de PulseSignal Pro...")
    log.info(f"Actifs surveillés : {', '.join(SYMBOLS)}")
    log.info(f"Seuil d'alerte : {ALERT_THRESHOLD_PERCENT}%")

    url = "https://api.binance.com/api/v3/ticker/24hr"

    # Création d'une session HTTP unique (optimisation des performances)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ticker_dict = {item["symbol"]: item for item in data}

                        for symbol in SYMBOLS:
                            if symbol in ticker_dict:
                                price = float(ticker_dict[symbol]["lastPrice"])
                                volume = float(ticker_dict[symbol]["volume"])
                                await analyze_market_data(session, symbol, price, volume)
                    else:
                        log.warning(f"Binance API a retourné le code HTTP {resp.status}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Erreur lors de la récupération des prix : {e}")

            # Attendre 5 secondes avant la prochaine vérification
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("🛑 PulseSignal Pro arrêté par l'utilisateur.")
