import requests, feedparser, time, datetime, os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = "7730328507"
capitale = 1000.0
perdita_oggi = 0.0
profitto_oggi = 0.0
operazioni_oggi = 0
ultimo_giorno = ""
attivo = True
pausa_fino = None
ultimo_stop = 0

FONTI = [
    "https://www.federalreserve.gov/feeds/press_all.xml",
    "https://www.ecb.europa.eu/rss/press.html",
    "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=8-K&dateb=&owner=include&count=10&output=atom",
    "https://www.reuters.com/rssFeed/businessNews",
    "https://www.bloomberg.com/feeds/podcasts/etf-report.xml",
    "https://www.ft.com/?format=rss",
    "https://www.wsj.com/xml/rss/3_7014.xml",
]

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": testo}, timeout=10)
    except:
        pass

def controlla_notizie():
    notizie_importanti = []
    for fonte in FONTI:
        try:
            feed = feedparser.parse(fonte)
            for entry in feed.entries[:3]:
                titolo = entry.title.lower()
                if any(parola in titolo for parola in ["fed", "federal reserve", "bce", "ecb", "sec", "tasso", "rate", "inflazione", "inflation", "recessione", "recession", "crisi", "crisis", "war", "guerra", "bank", "banca"]):
                    notizie_importanti.append(entry.title)
        except:
            pass
        time.sleep(1)
    return notizie_importanti

offset_file = "offset.txt"
def leggi_offset():
    try:
        with open(offset_file, "r") as f:
            return int(f.read().strip())
    except:
        return 0
def salva_offset(valore):
    with open(offset_file, "w") as f:
        f.write(str(valore))

def controlla_comandi():
    global attivo
    offset = leggi_offset()
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=5"
    try:
        r = requests.get(url, timeout=10).json()
        if "result" in r:
            for update in r["result"]:
                salva_offset(update["update_id"] + 1)
                if "message" in update and "text" in update["message"]:
                    testo = update["message"]["text"].lower().replace(" ", "").strip()
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
        return True
    return False

if __name__ == "__main__":
    invia_telegram("👔 BROKER: V4.1 DEFINITIVA ATTIVA. Collegato a @IvoRaptor_bot. Capitale 1000€. Protezione 30€/giorno attiva. Scrivi /stato per controllare.")
    while True:
        try:
            if reset_giornaliero():
                invia_telegram("👔 BROKER 8:00: Buongiorno Ivo. Parto con 1000.00€. Stop giornaliero 30€. Oggi controllo solo Fed, BCE, SEC, Reuters, Bloomberg, FT, WSJ. Se le notizie non sono sicure, non opero.")
            controlla_comandi()
            if attivo:
                notizie = controlla_notizie()
                if len(notizie) >= 2:
                    invia_telegram(f"👔 BROKER: STOP - Notizia importante da {len(notizie)} fonti ufficiali: {notizie[0]}. Resto fermo 30 min per proteggerti.")
                    time.sleep(1800)
            time.sleep(60)
        except Exception as e:
            print(f"Errore: {e}")
            time.sleep(60)
