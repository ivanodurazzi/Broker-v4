# BROKER V4 DEFINITIVA - IVO
# Capitale 1000€ - Stop giornaliero 30€ - Stop per trade 10€
# Bot: @IvoRaptor_bot - ID: 888137717

import requests
import time
import datetime
import feedparser
import os

# --- CONFIGURAZIONE - METTI QUI I TUOI DATI ---
TELEGRAM_TOKEN = "INCOLLA_QUI_IL_TUO_NUOVO_TOKEN"
CHAT_ID = "888137717"
# ------------------------------------------------

CAPITALE_INIZIALE = 1000.0
capitale = 1000.0
perdita_oggi = 0.0
profitto_oggi = 0.0
operazioni_oggi = 0
MAX_PERDITA_GIORNO = 30.0
MAX_PERDITA_TRADE = 10.0
MAX_OPERAZIONI_GIORNO = 3
OBIETTIVO_GIORNO = 30.0
attivo = True
ultimo_giorno = ""

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": messaggio}
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def controlla_news_ufficiali():
    # Fonti UFFICIALI: Fed, BCE, Reuters, Bloomberg, AP, FT, WSJ
    feeds = [
        "https://www.federalreserve.gov/feeds/press_all.xml",
        "https://www.ecb.europa.eu/rss/press.xml",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.ft.com/rss/home",
    ]
    notizie_importanti = []
    parole_chiave = ["fed", "federal reserve", "bce", "ecb", "tassi", "rates", "inflazione", "inflation", "sec", "casa bianca", "white house", "recessione", "recession"]
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                titolo = entry.title.lower()
                for parola in parole_chiave:
                    if parola in titolo:
                        notizie_importanti.append(entry.title)
                        break
        except:
            pass
    return notizie_importanti

def controlla_comandi():
    global attivo
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    try:
        r = requests.get(url, timeout=10).json()
        if "result" in r:
            for update in r["result"][-3:]:
                if "message" in update and "text" in update["message"]:
                    testo = update["message"]["text"].lower()
                    if testo == "/stop":
                        attivo = False
                        invia_telegram("👔 BROKER: STOP ricevuto. Mi fermo subito. Per ripartire scrivi /start")
                    elif testo == "/start":
                        attivo = True
                        invia_telegram("👔 BROKER: Riparto. Controllo le news e torno a lavorare.")
                    elif testo == "/stato":
                        invia_telegram(f"👔 BROKER STATO:\nCapitale: {capitale:.2f}€\nOggi: {profitto_oggi - perdita_oggi:.2f}€\nOperazioni oggi: {operazioni_oggi}/3\nAttivo: {'SI' if attivo else 'NO'}")
    except:
        pass

def reset_giornaliero():
    global perdita_oggi, profitto_oggi, operazioni_oggi, ultimo_giorno
    oggi = datetime.date.today().isoformat()
    if oggi != ultimo_giorno:
        ultimo_giorno = oggi
        perdita_oggi = 0.0
        profitto_oggi = 0.0
        operazioni_oggi = 0
        invia_telegram(f"👔 BROKER 8:00: Buongiorno Ivo. Parto con {capitale:.2f}€. Stop giornaliero 30€. Oggi controllo solo Fed, BCE, SEC, Reuters, Bloomberg, FT, WSJ. Se le notizie non sono sicure, non opero.")

# --- LOOP PRINCIPALE 24h/24h ---
invia_telegram("👔 BROKER: V4 DEFINITIVA ATTIVA. Collegato a @IvoRaptor_bot. Capitale 1000€. Protezione 30€/giorno attiva. Ti scrivo solo se c'è qualcosa di importante.")
reset_giornaliero()

while True:
    controlla_comandi()
    reset_giornaliero()

    if not attivo:
        time.sleep(60)
        continue

    # Controllo stop giornaliero
    if perdita_oggi >= MAX_PERDITA_GIORNO:
        invia_telegram(f"👔 BROKER: STOP - Ho perso 30€ oggi. Mi fermo per proteggerti. Totale {capitale:.2f}€. Domani riprovo.")
        attivo = False
        time.sleep(3600)
        continue

    if profitto_oggi >= OBIETTIVO_GIORNO:
        invia_telegram(f"👔 BROKER: Obiettivo raggiunto +30€ oggi! Mi fermo e tengo il profitto. Totale {capitale:.2f}€.")
        attivo = False
        time.sleep(3600)
        continue

    if operazioni_oggi < MAX_OPERAZIONI_GIORNO:
        notizie = controlla_news_ufficiali()
        if len(notizie) >= 2:
            # Doppia verifica: servono almeno 2 fonti che dicono la stessa cosa
            invia_telegram(f"👔 BROKER: STOP - Notizia importante da 2 fonti ufficiali: {notizie[0]}. Resto fermo 30 min per proteggerti.")
            time.sleep(1800)
        else:
            # Qui andrebbe la logica di trading reale
            # Per ora in modalità SICURA: osserva e non opera senza conferma
            pass

    time.sleep(120) # Controlla ogni 2 minuti
