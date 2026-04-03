# 📖 Technical Architecture & Engineering Documentation: ThecoreGrid.dev

**Systemversion:** 4.0 (März 2026) | **Status:** Production / Stable  
**Zielgruppe:** SRE, DevOps, System Architects, Tech Leads  
**Maintainer:** Founder / CTO  

---

## 1. EXECUTIVE SUMMARY & DATA FLOW (ARCHITEKTURÜBERBLICK)

ThecoreGrid.dev ist ein vollständig autonomer B2B-IT-Media-Hub mit einer Headless-Microservice-Architektur. Drittanbieter-Knoten (No-Code-Services, Telegram-Gateways) wurden vollständig aus der Kette eliminiert — die Kommunikation zwischen CMS und Python-Backend erfolgt direkt im Arbeitsspeicher des Servers (localhost).

**Content-Lebenszyklus (Data Pipeline v4.0):**

* **Aggregator:** Im Hintergrund (per Cron-Timer) parst der Bot Top-RSS-Blogs, bewertet sie über `gpt-4o-mini` auf architektonischen Wert und liefert einen Bericht.
* **AI Injection & Visuals:** Auf Befehl des Admins verfasst der Bot eine Deep-Analyse und übersetzt diese ins EN und DE. Er generiert SEO-Slugs. Er bestellt ein Enterprise-Cover bei DALL-E 3. Durch den Linux-Konsolenschutz hindurch (Direct DB Injection via `WP-CLI`) erstellt er 3 fertige Entwürfe (Drafts).
* **Hardware Taxonomy:** Der Linux-Kernel selbst ordnet den Posts hardwarenah die Sprachen zu (Polylang), vergibt Schlagwörter (Tags) und lädt das Bild in die Mediathek hoch, wobei es direkt mit allen drei Versionen verlinkt wird.
* **Async Webhook:** Der Admin klickt bei der RU-Version auf "Veröffentlichen". Ein selbst geschriebener PHP-Hook extrahiert den Teaser, holt die lokalisierten URLs sowie den Bildlink und feuert asynchron ein JSON-Payload an den internen Port `127.0.0.1:5000` ab.
* **Distribution:** Der Distributor-Bot fängt das JSON ab, ersetzt intelligent russische Links durch fremdsprachige mit UTM-Parametern und veröffentlicht diese im Format "Photo + Caption" in 3 Telegram-Kanälen.
* **Entertainment Pipeline:** Der Aggregator-Bot enthält einen separaten Kreislauf zum Sammeln von Reddit-Threads (`FUN_RSS_FEEDS`). Damit dieser "Nonsens" die analytischen Digests und das Oracle nicht kontaminiert (Data Poisoning), werden Unterhaltungslinks in der DB strikt isoliert (`score=0`, `used=1`). Die Verarbeitung erfolgt über die Befehle *отдых* (Senior-Sarkasmus in 80 Wörtern) und *мемосик* (DALL-E generiert eine "stumme" visuelle 3D-Metapher des IT-Schmerzes strikt ohne Text, die KI verfasst eine ironische Bildunterschrift).

---

## 2. INFRASTRUKTUR UND SERVER (HOSTING & DEVOPS)

* **Hosting & Network:** VPS bei Hetzner Cloud (Deutschland). DNS-Routing über Strato (A-Record IPv4). OS: Ubuntu 24.04 LTS.
* **Web Stack (LEMP):** Verwaltet über WordOps. Komponenten: Nginx, PHP 8.3-fpm, MariaDB.
* **Highload-Caching:**
  * *Frontend:* Nginx FastCGI Cache (Auslieferung von Static Content an nicht authentifizierte Nutzer im Millisekundenbereich).
  * *Backend:* Redis Object Cache (In-Memory-Datenbank-Cache zur massiven Beschleunigung des Admin-Bereichs und der Verarbeitung von KI-API-Anfragen).
* **Security:** Python `pip` ist in virtuelle Umgebungen (`venv`) isoliert. Der Schutz vor 409 Token Conflicts wurde durch eine strikte Trennung der Telegram-API-Schlüssel zwischen den Daemons realisiert.

---

## 3. MICROSERVICE-ARCHITEKTUR (PYTHON BACKEND)

Alle Bots sind fest in den Linux-Kernel als unabhängige, selbstheilende Dienste (Daemons) via `systemd` verankert.

### 🟢 Microservice 1: KI-Redakteur (`coregrid_ai.service`)
* **Pfad:** `/root/coregrid_ai/aggregator.py`
* **Funktion:** Nachrichtenaggregator, Generierung von Longreads, Generierung von Fun-Posts für Telegram (Befehl: *телега*), Layout von Digests.
* **Besonderheiten (V4.0):** Nutzt `subprocess` und `WP-CLI`. Dies umgeht die HTTP-Authentifizierung und injiziert Daten direkt in die WordPress-DB. Geschützt vor "Database Lock" beim Arbeiten mit der integrierten SQLite3. Verfügt über einen Smart Fallback Parser, der die Artikelstruktur wiederherstellt, selbst wenn das LLM das HTML-Markup zerstört hat.
* **Data Engineering & RAG (Oracle):** Ein Mechanismus zur semantischen Komprimierung ist implementiert. Jeder Artikel wird von `gpt-4o-mini` in ein komprimiertes Extrakt verarbeitet und in der DB (`knowledge_graph`) mit strenger Ontologie der Kategorien gespeichert. Auf den Befehl *тренд [Tage] [Kategorie]* zieht der Bot ein Array aus Wissen und verfasst eine Predictive Analytics-Vorhersage für die nächsten 6-12 Monate.
* **WP-CLI STDIN Hack:** Um das systembedingte Linux-Limit (`ARG_MAX`) für die Länge von Befehlszeilen zu umgehen, wird der HTML-Code der Artikel als Datenstrom via STDIN in den WordPress-Core eingespeist (`wp post create -`). Polylang-Sprachen werden über einen harten PHP-Code-Inject im Terminal zugewiesen (`wp eval "pll_set_post_language..."`), wodurch die Kapriolen der Plugin-API umgangen werden.

### 🌍 Microservice 2: Distributor (`coregrid_gateway.service`)
* **Pfad:** `/opt/coregrid_bots/bot_gateway/bot.py`
* **Funktion:** Im Inneren läuft ein Flask-Server auf dem geschlossenen Port 5000. Wartet auf den Webhook von WordPress.
* **Graceful Degradation (Fallbacks):** Wenn OpenAI einen API-Fehler zurückgibt, greift der Fallback-Algorithmus — der Bot veröffentlicht eine Fallback-Phrase ("👀 Schau mal, ein neuer Artikel ist erschienen") samt korrekter URL. Wenn die Textgröße das Telegram-Limit für Bildunterschriften (1024 Zeichen) überschreitet, stürzt der Bot nicht ab, sondern sendet den Text automatisch als separate Nachricht ohne Foto.

### 🛡 Microservice 3: AIOps Watchdog (`coregrid_watchdog.service`)
* **Pfad:** `/root/coregrid_ai/watchdog.py`
* **Funktion:** SRE-Tool (Site Reliability Engineering). Liest System-Logs (`journalctl`) der restlichen Bots. Das neuronale Netz filtert das Systemrauschen (Noise) und erstellt eine menschliche Diagnose.
* **Verwaltung:** Ermöglicht die hardwarenahe Leerung des Caches (`wo clean --all`) und das Abrufen von CPU/RAM/Disk-Metriken direkt aus Telegram.

---

## 4. WORDPRESS-UMGEBUNG (FRONTEND & CMS)

* **Optimierung:** Alle Autoposting-Plugins wurden gelöscht. Das Routing läuft über reines PHP (asynchroner Hook `wp_remote_post`, `blocking => false`).
* **SEO & Image Optimization:** Automatische Erstellung kurzer SEO-URLs (Slugs) basierend auf der englischen Übersetzung. Das DALL-E-Bild wird nur 1 Mal hochgeladen und hardwareseitig mit den 3 mehrsprachigen Beiträgen verknüpft (schont Speicherplatz in MariaDB).
* **Legal (GDPR / DSGVO):** Impressum und Datenschutzerklärung entsprechen vollumfänglich den deutschen B2B-Standards. Strikte logische Datensegregation: Die Google Analytics Client ID wird pseudonymisiert übergeben.
* **Edge Case Management (404 & Empty Search):** Das Error Handling wurde auf Ebene der `gettext`-Filter (WPCode) neu geschrieben. Statt leerer Seiten sehen die Ingenieure B2B-Platzhalter ("404: Node Not Found"), ein CSS-Grid der 6 neuesten Artikel und ein interaktives Easter Egg (SVG-Katze), das per Klick ein vollwertiges Minispiel "Python Debugger" entfaltet (geschrieben in Vanilla JS, Gewicht < 1KB, sendet GTM-Events `easter_egg_found` und `game_over` mit Spielergebnissen).

---

## 5. TELEGRAM-ÖKOSYSTEM UND ZUGRIFFSKONTROLLE

* **Prinzip des Least Privilege:** Der Zugriff auf manuelle Broadcasts und Steuerungsbefehle der Daemons ist auf der Ebene des Python-Cores strikt durch die Arrays `ADMIN_ID` und `TEAM_IDS` limitiert.
* **Kanäle:** `@ithub_ru_in_de`, `@ithub_en_in_de`, `@ithub_de_in_de`.

---

## 6. ROUTINE DES CHEFREDAKTEURS (SOP v4.0)

Der Wechsel zur Architektur 4.0 hat die Veröffentlichungszeit für einen komplexen, mehrsprachigen Longread auf 5-10 Minuten reduziert.

1. **07:00** — Der Watchdog-Bot sendet den Server Health Report. **07:20 / 17:20** — Der Aggregator-Bot liefert RSS-Insights samt Scoring.
2. Der Admin antwortet auf einen Link mit dem Befehl *сформируй* (Generieren). Der Bot generiert Texte, URL-Slugs, das Enterprise-Cover, Tags und injiziert all dies lautlos in die WordPress-Datenbank.
3. Der Admin öffnet die "Entwürfe". Die Sprachen (Polylang) sind vom System bereits getrennt worden. Tags und Bilder sind bereits gesetzt.
4. Der Admin prüft die RU-Version, verknüpft im rechten Panel die fertigen EN/DE-Entwürfe und veröffentlicht den Beitrag.
5. Der Server formatiert selbstständig den Teaser, übersetzt ihn, tauscht UTM-Links aus und pusht ihn inklusive Coverbild in die Telegram-Kanäle.
6. Kurze Nachrichten werden durch den Befehl *телега* (Telega) gebildet — vom Admin kopiert, in den Distributor-Bot eingefügt und direkt verteilt (ohne CMS-Umweg).
7. **SEO Enrichment (Rank Math):** Ganz unten in den generierten Entwürfen hinterlässt die KI einen textlichen «SEO-Block» (Focus Keyword, Description bis 160 Zeichen, Image Alt). Der Admin kopiert diese Daten in das Rank Math-Panel und löscht den Textblock aus dem Artikel vor der Veröffentlichung. Interne UTM-Links zum Original (`?utm_source=...&utm_medium=referral`) sind bereits durch das Skript am Ende des Textes hardcodiert.

---

## 7. CHEAT SHEET FÜR SYSADMINS (CLI-BEFEHLE)

```bash
# === VERWALTUNG DER MICROSERVICES ===
systemctl restart coregrid_ai.service          # Neustart KI-Sekretär
systemctl restart coregrid_gateway.service     # Neustart Übersetzer/Gateway
systemctl restart coregrid_watchdog.service    # Neustart Watchdog
systemctl daemon-reload                        # Linux-Konfiguration (.service) anwenden

# === LOGGING (TROUBLESHOOTING) ===
journalctl -u coregrid_ai.service -n 50 --no-pager   # Zeige letzte 50 Logs
ss -tulnp | grep 5000                                # Flask-Socket prüfen

# === BUGFIXING UND NOTFÄLLE ===
wo clean --all                                 # Web-Caches leeren (Nginx/Redis)
pkill -f aggregator.py                         # Zombie-Prozesse vernichten (fix: 409 Conflict)
rm -rf /root/coregrid_ai/__pycache__           # Python-Cache leeren (bei Wechsel der API Keys)
sqlite3 /root/coregrid_ai/articles_memory.db "SELECT count(*) FROM processed;" # DB prüfen
