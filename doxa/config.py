"""Granice sustava. Izvršni sloj ne šalje naloge na burzu."""

from __future__ import annotations

GUARD_SYMBOL = "BTCUSDT"

# Altovi. BTC je samo čuvar, ne instrument za ulaz.
TRADABLE: tuple[str, ...] = (
    "SOLUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "DOGEUSDT",
    "ADAUSDT",
)

ALL_SYMBOLS: tuple[str, ...] = (GUARD_SYMBOL, *TRADABLE)

# Koliko zatvorenih svijeća treba prije nego agent smije glasati.
MIN_BARS: dict[str, int] = {"1m": 40, "15m": 40, "1h": 40, "4h": 60}

INTERVALS: dict[str, tuple[str, ...]] = {
    GUARD_SYMBOL: ("1m", "15m"),
    **{symbol: ("1m", "15m", "1h", "4h") for symbol in TRADABLE},
}

INTERVAL_MS: dict[str, int] = {
    "1m": 60_000,
    "15m": 900_000,
    "1h": 3_600_000,
    "4h": 14_400_000,
}

KLINE_LIMIT = 200
BOOK_LEVELS = 50
TAKER_FEE = 0.001
START_CASH = 200.0
TARGET_CASH = 1000.0
HORIZON_S = 60 * 60
MISSION_ID = "blitz-1h"
MIN_STAKE_EUR = 10.0
ENTRY_COOLDOWN_S = 12.0
GLOBAL_ENTRY_GAP_S = 0.0
FREEZE_COOLDOWN_S = 180.0

# Spot koji nije geo-blokiran tamo gdje api.binance.com vraća 451.
BINANCE_REST = "https://data-api.binance.vision"
BINANCE_WS = "wss://data-stream.binance.vision/stream"
# Binance futures funding je često nedostupan. OKX perpetual je javni zamjenski izvor.
FUNDING_URL = "https://www.okx.com/api/v5/public/funding-rate"

WALLET_PATH = "data/crypto_wallet.json"
LOCK_PATH = "data/doxa.lock"
