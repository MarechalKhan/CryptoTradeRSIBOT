import os
import time
import json
import logging
import requests
from dotenv import load_dotenv
from telegram import Bot
import os

# --- FORÇA leitura manual do .env local (evita problemas com load_dotenv/OneDrive/encoding) ---
def read_dotenv(path):
    d = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                d[k] = v.strip()
    except FileNotFoundError:
        pass
    return d

_env_path = os.path.join(os.path.dirname(__file__), ".env")
_env = read_dotenv(_env_path)
# opcional: colocar no ambiente para que todo código que usa os.getenv() funcione
os.environ.update(_env)
# --- fim bloco ---

# tentar importar NetworkError (pode existir em algumas versões)
try:
    from telegram.error import NetworkError
except Exception:
    NetworkError = None

# --- Configuração inicial ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LAST_ALERTS_FILE = "last_alerts.json"
TOP_N = int(os.getenv("TOP_N", 1))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))
COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", 10))

# --- Logger ---
logging.basicConfig(
    filename="bot.log",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
    encoding="utf-8"
)
logger = logging.getLogger()

# --- Validações mínimas ---
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN não definido no .env")
    raise SystemExit("TELEGRAM_TOKEN não definido no .env")
if not CHAT_ID:
    logger.error("TELEGRAM_CHAT_ID não definido no .env")
    raise SystemExit("TELEGRAM_CHAT_ID não definido no .env")

# --- Bot Telegram ---
bot = Bot(token=TELEGRAM_TOKEN)

# --- Funções auxiliares ---

def _is_unauthorized_exception(exc):
    """Detecta se a exceção corresponde a 'Unauthorized' (compatível entre versões)."""
    msg = str(exc).lower()
    if 'unauthorized' in msg or '401' in msg:
        return True
    name = type(exc).__name__.lower()
    if 'unauthorized' in name:
        return True
    return False

def send(msg, max_retries=4):
    """
    Envia mensagem para o Telegram com retry/backoff.
    Trata Unauthorized (token inválido/sem permissão) separadamente.
    """
    attempt = 0
    wait = 1
    while attempt < max_retries:
        try:
            # debug / sanitização do chat id antes do envio
            logger.debug("Tentativa de envio — CHAT_ID repr=%s type=%s", repr(CHAT_ID), type(CHAT_ID))
            try:
                _target_chat = int(str(CHAT_ID).strip())
            except Exception:
                _target_chat = CHAT_ID

            bot.send_message(chat_id=_target_chat, text=msg)
            logger.info("Mensagem enviada: %s", msg.replace("\n", " | "))
            return True

        except Exception as e:
            # trata Unauthorized separadamente (função _is_unauthorized_exception deve existir)
            if _is_unauthorized_exception(e):
                logger.error("Unauthorized ao enviar mensagem: %s", e)
                try:
                    with open("telegram_unauthorized.flag", "w", encoding="utf-8") as f:
                        f.write(f"Unauthorized at {time.strftime('%Y-%m-%d %H:%M:%S')}\n{e}\n")
                except Exception:
                    pass
                return False

            attempt += 1
            logger.warning("NetworkError (tentativa %d/%d): %s. Retry em %ds", attempt, max_retries, e, wait)
            time.sleep(wait)
            wait = min(wait * 2, 30)

    logger.error("Falha ao enviar mensagem apos %d tentativas.", max_retries)
    return False

# --- Persistência do cooldown entre reinícios ---
def load_last_alerts():
    if os.path.exists(LAST_ALERTS_FILE):
        try:
            with open(LAST_ALERTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logger.exception("Erro ao carregar last alerts, iniciando vazio.")
    return {}

def save_last_alerts(data):
    try:
        with open(LAST_ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        logger.exception("Erro ao salvar last alerts.")

last_alert = load_last_alerts()

# --- Helper: requests com backoff simples ---
def fetch_with_backoff(url, max_retries=3, base_wait=1):
    wait = base_wait
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning("Request falhou (tentativa %d/%d): %s", attempt, max_retries, e)
            if attempt == max_retries:
                logger.error("Max retries atingido para %s", url)
                return None
            time.sleep(wait)
            wait *= 2
    return None

# --- Busca top symbols pela quoteVolume (Binance Futures) ---
def get_top_symbols(n=1):
    data = fetch_with_backoff("https://fapi.binance.com/fapi/v1/ticker/24hr")
    if not data:
        return []
    try:
        usdt = [d for d in data if d["symbol"].endswith("USDT")]
        sorted_by_vol = sorted(usdt, key=lambda x: float(x.get("quoteVolume", 0)), reverse=True)
        return sorted_by_vol[:n]
    except Exception:
        logger.exception("Erro ao processar dados Binance")
        return []

def check_conditions_and_alert(ticker):
    try:
        symbol = ticker["symbol"]
        change = float(ticker.get("priceChangePercent", 0))
        price = ticker.get("lastPrice")
        now = time.time()
        last = float(last_alert.get(symbol, 0))
        if abs(change) >= 5:  # exemplo demo: alerta se variação >= 5%
            if now - last >= COOLDOWN_MINUTES * 60:
                msg = f"ALERTA DEMO: {symbol}\nChange(24h): {change:.2f}%\nPreço: {price}"
                send(msg)
                last_alert[symbol] = now
                save_last_alerts(last_alert)
            else:
                logger.info("%s em cooldown.", symbol)
    except Exception:
        logger.exception("Erro ao checar condição para %s", ticker.get("symbol", "unknown"))

# --- Início ---
logger.info("Bot de Alertas iniciado (starter seguro). TOP_N=%d POLL_INTERVAL=%ds COOLDOWN=%dm",
            TOP_N, POLL_INTERVAL, COOLDOWN_MINUTES)
send(f"Bot de Alertas iniciado ✅\nModo: starter seguro\nTOP_N={TOP_N}")

logger.info("Entrando no loop principal. Ctrl+C para parar.")
try:
    while True:
        top = get_top_symbols(TOP_N)
        if not top:
            logger.warning("Nenhum ticker retornado neste ciclo.")
        else:
            for t in top:
                logger.info("Checando: %s Change%% %s", t["symbol"], t.get("priceChangePercent"))
                check_conditions_and_alert(t)
        time.sleep(POLL_INTERVAL)
except KeyboardInterrupt:
    logger.info("Interrompido pelo usuário. Finalizando.")
    send("Bot de Alertas finalizado (Ctrl+C).")
except Exception:
    logger.exception("Erro não tratado no loop principal.")
    send("Bot encontrou erro crítico e parou. Veja logs.")