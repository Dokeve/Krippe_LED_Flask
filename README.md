# LED Control Suite – Vollversion  

Dieses Projekt steuert ca. **997 WS2812-LEDs** über ein **Flask-Backend** mit **React-Frontend** und persistiert alle Daten in **MariaDB**.  
Es unterstützt:  

- **Zwei Modi**:  
  - **Modus 1**: Tag-Nacht-Verlauf (300 Sekunden, mit Übergängen, Hintergrundgeräusche, Pumpe an)  
  - **Modus 2**: Alle LEDs einheitlich (Hintergrund aus, Pumpe aus)  
- **GPIO**:  
  - **Pin 17**: Trigger für Textausgabe → Hintergrund wird geduckt  
  - **Pin 10**: Steuerung einer Wasserpumpe (nur in Modus 1 aktiv)  
- **Audio**: Hintergrund-Sounds für jede Phase + Textdateien (Ankündigungen), ducking beim Abspielen  
- **Kalender**: Drag & Drop zur Steuerung der Modi  
- **Gruppenverwaltung**: LEDs können per Mapping-Datei in Gruppen eingeteilt werden  
- **Live Preview**: zeigt LED-Gruppen mit Farben untereinander  

---

## 📂 Projektstruktur

```
led-suite-v3/
├── backend/                # Flask Backend + Importer + LED + Audio
│   ├── app.py              # Haupt-API + Socket.IO
│   ├── config.py           # Konfiguration
│   ├── models.py           # DB-Modelle (SQLAlchemy)
│   ├── importer.py         # Mapping-Importer (reset/merge)
│   ├── led_controller.py   # LED-Logik (Dummy + WS2812)
│   ├── audio.py            # Audio mit pygame (Phasen, Ducking)
│   ├── gpio_worker.py      # GPIO Trigger & Pumpe
│   ├── scheduler.py        # Kalender-Events & Ansagen
│   ├── requirements.txt    # Python-Abhängigkeiten
│   └── mappings/           # Mapping-Dateien
│       ├── mapping_off.txt
│       ├── mapping_dauer.txt
│       ├── mapping_day.txt
│       ├── mapping_d2n.txt
│       ├── mapping_night.txt
│       └── mapping_n2d.txt
│
├── frontend/               # React-Frontend (Vite)
│   ├── index.html          # Einstiegspunkt
│   ├── vite.config.js
│   ├── package.json
│   └── src/components/     # React-Komponenten
│       ├── App.jsx
│       ├── ModeControl.jsx
│       ├── LivePreviewRows.jsx
│       ├── MappingManager.jsx
│       └── DragCalendar.jsx
│
├── docker-compose.yml      # MariaDB + Adminer
├── .env.example            # Beispiel-Umgebungsvariablen
└── README.md               # Diese Datei
```

---

## ⚙️ Installation

### Voraussetzungen
- Python **3.10+**
- Node.js **18+** und npm
- Docker + Docker Compose (für MariaDB)

---

### 1. MariaDB starten

```bash
docker compose up -d
```

➡️ Datenbank läuft jetzt auf `localhost:3306`  
➡️ Adminer auf [http://localhost:8080](http://localhost:8080)  

---

### 2. Backend installieren & starten

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

python app.py
```

➡️ API läuft jetzt auf [http://localhost:5000](http://localhost:5000)

---

### 3. Frontend installieren & starten

```bash
cd frontend
npm install
npm run dev
```

➡️ Frontend läuft auf [http://localhost:5173](http://localhost:5173)  

---

## 🚀 Nutzung

### Modi
- **Modus 1 (Tag/Nacht)**: LEDs wechseln automatisch zwischen Tag (100s), Übergang (50s), Nacht (100s), Übergang (50s).  
- **Modus 2 (Einheitlich)**: Alle LEDs leuchten gleich (konfigurierbar).  
- **Stop**: LEDs aus, Pumpe aus.  

### Mapping
- Beim **ersten Start**: Importer lädt automatisch `mapping_dauer.txt` im **Reset-Modus**.  
- Im Frontend unter **Mapping verwalten**:  
  - Mapping-Datei wählen (`mapping_day.txt` etc.)  
  - Modus: `merge` oder `reset`  
  - Import starten  

### Kalender
- Drag & Drop im UI  
- Event hinzufügen: Zeitraum markieren → Name/Modus/Farbe eingeben  
- Events können verschoben, verlängert oder gelöscht werden  

### GPIO
- **Pin 17**: Knopfdruck → Textausgabe wird abgespielt, Hintergrund geduckt  
- **Pin 10**: Pumpe → läuft automatisch in Modus 1, aus in Modus 2  

---

## 🔧 Konfiguration

In `.env` (oder direkt in `backend/config.py`):  

```ini
LED_DRIVER=dummy     # "dummy" oder "rpi_ws281x"
LED_COUNT=997
LED_BRIGHTNESS=180
AUDIO_VOLUME=0.5
DUCKED_VOLUME=0.2
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=led_db
DB_USER=led_user
DB_PASS=led_pass
```

---

## 📡 API-Endpoints (Auszug)

- `GET /api/status` → Status (Modus, LED-Zahl)  
- `GET /api/preview` → LED-Vorschau (Gruppen, Farben)  
- `POST /api/mode` → Modus setzen (`{mode:1}` oder `{mode:2, color:"#FF0000"}`)  
- `POST /api/mode/stop` → LEDs & Pumpe stoppen  
- `GET/POST /api/groups` → Gruppen lesen/anlegen  
- `PUT/DELETE /api/groups/<id>` → Gruppe bearbeiten/löschen  
- `POST /api/import-mapping` → Mapping importieren (`reset` oder `merge`)  
- `GET/POST /api/calendar` → Kalender-Events verwalten  

---

## 🧪 Test ohne Hardware

- `LED_DRIVER=dummy` → LEDs werden nur als Preview in der UI angezeigt  
- GPIO- und Audiofunktionen fangen Fehler ab, wenn keine Hardware vorhanden ist  

---

## 🖼 Architektur (ASCII)

```ascii
+------------------+             +-------------------+
|  Frontend (React)| <---------> | Backend (Flask)   |
|  (Vite, Calendar,|   JSON/WS   | API + Socket.IO   |
|  Preview, Groups)|             |                   |
+------------------+             +-------------------+
                                       | | | 
                                       | | |
              +------------------------+ | +-----------------------+
              |                          |                         |
              v                          v                         v
     +-------------------+     +-------------------+     +-------------------+
     |     MariaDB       |     |  LED Controller   |     |   Audio System     |
     |  (Persistenz für  |     | (rpi_ws281x oder  |     | (pygame, Phasen-   |
     |   Calendar,Groups)|     |   Dummy-Simulation)|    |  Sounds, Ducking)  |
     +-------------------+     +-------------------+     +-------------------+
              ^
              |
              |
     +-------------------+
     |     Adminer       |
     | (DB-Webfrontend)  |
     +-------------------+

                        +-------------------+
                        |   GPIO Worker     |
                        | Pin 17 = Texte    |
                        | Pin 10 = Pumpe    |
                        +-------------------+
```

---

## 📜 Lizenz

Internes Projekt – keine öffentliche Lizenz.  
