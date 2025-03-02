# Vortex Browser

Ein moderner, schneller und minimalistischer Webbrowser mit dunklem Design, entwickelt mit Python und Qt.

![Vortex Browser](https://platzhalter-für-screenshot.png)

## Features

- **Modernes dunkles Design**: Angenehm für die Augen bei langen Browsing-Sessions
- **Tab-Management**: Mehrere Tabs öffnen, schließen und organisieren
- **Schnelle Navigation**: Intuitive Bedienung mit einer aufgeräumten Benutzeroberfläche
- **Intelligente Adressleiste**: Zeigt nur die Domain an für bessere Übersichtlichkeit
- **Eingebaute Suchfunktion**: Unterstützt mehrere Suchmaschinen:
  - Google
  - Bing
  - DuckDuckGo
  - Ecosia
  - Qwant
- **Anpassbare Einstellungen**: Konfiguriere deine bevorzugte Suchmaschine
- **Schnelle Ladezeiten**: Optimiert für moderne Webseiten

## Installation

### Voraussetzungen

- Python 3.6 oder höher
- PyQt5
- PyQtWebEngine
- QtAwesome

### Abhängigkeiten installieren

```bash
pip install PyQt5 PyQtWebEngine qtawesome
```

### Den Browser starten

```bash
python main.py
```

## Verwendung

### Navigation

- **Zurück/Vorwärts**: Navigiere durch deinen Browserverlauf
- **Neu laden**: Aktualisiere die aktuelle Webseite
- **Home**: Kehre zur Startseite zurück (Google)
- **Adressleiste**: Gib URLs oder Suchbegriffe ein
  - Bei Eingabe einer URL (enthält einen Punkt ohne Leerzeichen) wird direkt zur Webseite navigiert
  - Bei Eingabe eines Suchbegriffs wird die konfigurierte Suchmaschine verwendet
- **Neuer Tab**: Öffne einen neuen Tab mit der Startseite
- **Einstellungen**: Konfiguriere den Browser

### Einstellungen

1. Klicke auf das Einstellungs-Icon
2. Wähle deine bevorzugte Suchmaschine
3. Klicke auf "Speichern"

## Technische Details

### Architektur

Der Vortex Browser basiert auf PyQt5 und verwendet die WebEngine-Komponente, die auf Chromium basiert, für das Rendern von Webseiten. Die wichtigsten Komponenten sind:

- **Browser-Klasse**: Hauptfenster und UI-Management
- **CustomWebEnginePage**: Spezielle Implementierung für die Handhabung von benutzerdefinierten URLs (vortex://)
- **Tab-Management**: Mehrere Instanzen von QWebEngineView in einem QTabWidget
- **Einstellungs-System**: Speichert Benutzereinstellungen in einer JSON-Datei

### Benutzerdefiniertes URL-Schema

Der Browser unterstützt ein eigenes URL-Schema `vortex://`:

- `vortex://settings`: Öffnet die Einstellungsseite
- `vortex://save-settings`: Backend-URL zum Speichern von Einstellungen

### Daten-Persistenz

Benutzereinstellungen werden im Home-Verzeichnis des Benutzers in der Datei `.vortex_settings.json` gespeichert.

## Weiterentwicklung

Mögliche zukünftige Erweiterungen:

- Lesezeichen-Management
- Erweiterbare Plugin-Architektur
- Synchronisierung zwischen Geräten
- Erweitertes Tab-Management (Gruppieren, Pinnen)
- Weitere Anpassungsmöglichkeiten für das Erscheinungsbild

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## Mitwirken

Beiträge sind willkommen! Bitte forke das Repository und erstelle einen Pull Request mit deinen Änderungen.

---

*Entwickelt mit ❤️ für ein besseres Web-Erlebnis* 