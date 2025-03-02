import sys
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                           QToolBar, QLineEdit, QPushButton, QVBoxLayout, 
                           QWidget, QHBoxLayout, QMenu, QStatusBar, QAction, QStyle)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import os
import json

# Suchmaschinen-Presets
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q={}",
    "Bing": "https://www.bing.com/search?q={}",
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
    "Ecosia": "https://www.ecosia.org/search?q={}",
    "Qwant": "https://www.qwant.com/?q={}"
}

# Settings-HTML Template
SETTINGS_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Vortex Einstellungen</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #2c2c2c;
            color: #ffffff;
        }}
        h1 {{
            color: #42a5f5;
            border-bottom: 1px solid #444;
            padding-bottom: 10px;
        }}
        .section {{
            background-color: #333;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        h2 {{
            margin-top: 0;
            color: #fff;
        }}
        select {{
            background-color: #444;
            color: white;
            padding: 8px;
            width: 100%;
            border: none;
            border-radius: 4px;
            margin: 10px 0;
        }}
        button {{
            background-color: #42a5f5;
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #2196f3;
        }}
        .current {{
            margin-top: 10px;
            font-style: italic;
            color: #aaa;
        }}
    </style>
</head>
<body>
    <h1>Vortex Browser Einstellungen</h1>
    
    <div class="section">
        <h2>Suchmaschine</h2>
        <p>Wähle deine Standard-Suchmaschine:</p>
        <select id="search-engine">
            {options}
        </select>
        <p class="current">Aktuelle Suchmaschine: <span id="current-engine">{current}</span></p>
        <button onclick="saveSettings()">Speichern</button>
    </div>

    <script>
        function saveSettings() {{
            const engine = document.getElementById('search-engine').value;
            window.location.href = 'vortex://save-settings?engine=' + encodeURIComponent(engine);
        }}
    </script>
</body>
</html>
"""

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if url.scheme() == "vortex":
            if url.host() == "settings":
                self.browser.loadSettingsPage()
                return False
            elif url.host() == "save-settings":
                try:
                    query = url.query()
                    if "engine=" in query:
                        engine = query.split("engine=")[1].split("&")[0]
                        engine = engine.replace("+", " ")  # Korrigiere URL-Codierung
                        self.browser.saveSettings({"search_engine": engine})
                    self.browser.loadSettingsPage()
                except Exception as e:
                    print(f"Fehler beim Verarbeiten der Einstellungen: {e}")
                    self.browser.status.showMessage(f"Fehler: {e}", 3000)
                return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Lade Einstellungen oder setze Standardwerte
        self.settings_file = os.path.join(os.path.expanduser("~"), ".vortex_settings.json")
        self.loadSettings()
        
        # Setze Dark Mode
        self.setDarkMode()
        
        # Setze Fenstertitel und Größe
        self.setWindowTitle("Vortex Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Erstelle ein zentrales Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout für das zentrale Widget
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Erstelle die Tab-Leiste
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        
        # Erstelle die Symbolleiste
        self.toolbar = QToolBar("Navigation")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)  # Nur Icons anzeigen
        self.addToolBar(self.toolbar)
        
        # Zurück-Button
        self.back_btn = QAction(self.style().standardIcon(QStyle.SP_ArrowBack), "", self)
        self.back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.toolbar.addAction(self.back_btn)
        
        # Vorwärts-Button
        self.forward_btn = QAction(self.style().standardIcon(QStyle.SP_ArrowForward), "", self)
        self.forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.toolbar.addAction(self.forward_btn)
        
        # Neu laden Button
        self.reload_btn = QAction(self.style().standardIcon(QStyle.SP_BrowserReload), "", self)
        self.reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.toolbar.addAction(self.reload_btn)
        
        # Home-Button
        self.home_btn = QAction(self.style().standardIcon(QStyle.SP_DirHomeIcon), "", self)
        self.home_btn.triggered.connect(self.navigateHome)
        self.toolbar.addAction(self.home_btn)
        
        # URL-Eingabefeld
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigateToUrl)
        self.toolbar.addWidget(self.url_bar)
        
        # Neuer Tab Button
        self.add_tab_btn = QAction(self.style().standardIcon(QStyle.SP_FileDialogNewFolder), "", self)
        self.add_tab_btn.triggered.connect(lambda: self.addTab())
        self.toolbar.addAction(self.add_tab_btn)
        
        # Settings Button
        self.settings_btn = QAction(self.style().standardIcon(QStyle.SP_FileDialogDetailedView), "", self)
        self.settings_btn.triggered.connect(self.loadSettingsPage)
        self.toolbar.addAction(self.settings_btn)
        
        # Füge die Tabs zum Layout hinzu
        self.layout.addWidget(self.tabs)
        
        # Statusleiste
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Erstelle einen ersten Tab
        self.addTab()
    
    def setDarkMode(self):
        # Erstelle eine dunkle Palette
        dark_palette = QPalette()
        
        # Setze Farben
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Wende die Palette an
        self.setPalette(dark_palette)
        
        # Setze Stylesheet für weitere Anpassungen
        self.setStyleSheet("""
            QTabWidget::pane { 
                border: 0; 
                background: #353535;
            }
            QTabBar::tab {
                background: #252525; 
                color: #FFFFFF;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #404040;
            }
            QToolBar {
                background: #252525;
                spacing: 3px;
                border: none;
                padding: 2px;
            }
            QLineEdit {
                background: #404040;
                color: white;
                border-radius: 4px;
                padding: 4px;
                selection-background-color: #2a82da;
            }
            QPushButton {
                background: #404040;
                color: white;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background: #505050;
            }
        """)
    
    def addTab(self, qurl=None):
        # Erstelle eine neue WebView
        browser = QWebEngineView()
        
        # Erstelle eine benutzerdefinierte Seite, die spezielle URLs behandeln kann
        page = CustomWebEnginePage(self)
        browser.setPage(page)
        
        # Verknüpfe das URL-Ändern mit unserer URL-Aktualisierung
        browser.urlChanged.connect(lambda qurl, browser=browser: self.updateUrlBar(qurl, browser))
        
        # Verknüpfe den Seitentitel mit unserem Tab-Titel
        browser.page().titleChanged.connect(self.updateTabTitle)
        
        # Verknüpfe das Laden mit der Statusleiste
        browser.loadStarted.connect(lambda: self.status.showMessage("Laden gestartet..."))
        browser.loadProgress.connect(lambda p: self.status.showMessage(f"Laden: {p}%"))
        browser.loadFinished.connect(lambda: self.status.showMessage("Laden abgeschlossen"))
        
        # Füge den Tab hinzu
        i = self.tabs.addTab(browser, "Neuer Tab")
        self.tabs.setCurrentIndex(i)
        
        # Wenn eine URL übergeben wurde, navigiere dorthin, ansonsten zur Startseite
        if qurl:
            browser.setUrl(qurl)
        else:
            browser.setUrl(QUrl("https://www.google.com"))
    
    def closeTab(self, i):
        # Schließe den Tab, wenn mehr als ein Tab geöffnet ist
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            # Wenn es der letzte Tab ist, öffne einen neuen
            self.tabs.widget(0).setUrl(QUrl("https://www.google.com"))
    
    def updateUrlBar(self, q, browser=None):
        # Aktualisiere die URL-Leiste
        if browser != self.tabs.currentWidget():
            return
        
        # Setze den Text in der URL-Leiste - nur die Domain anzeigen
        url_text = q.toString()
        if q.scheme() in ["http", "https"]:
            domain = q.host()
            self.url_bar.setText(domain)
        else:
            self.url_bar.setText(url_text)
    
    def updateTabTitle(self, title):
        # Aktualisiere den Tab-Titel mit dem HTML-Titel
        if title:
            self.tabs.setTabText(self.tabs.currentIndex(), title)
        else:
            self.tabs.setTabText(self.tabs.currentIndex(), "Unbenannt")
    
    def navigateToUrl(self):
        # Hole die URL aus der URL-Leiste
        url_text = self.url_bar.text().strip()
        
        # Überprüfe, ob es eine spezielle vortex:// URL ist
        if url_text.startswith("vortex://"):
            q = QUrl(url_text)
            self.tabs.currentWidget().setUrl(q)
            return
        
        # Überprüfe, ob es eine gültige URL ist
        if "." in url_text and not " " in url_text:
            # Füge http:// hinzu, falls keine Scheme vorhanden ist
            if not any(url_text.startswith(prefix) for prefix in ["http://", "https://", "file://"]):
                url_text = "http://" + url_text
            
            q = QUrl(url_text)
            self.tabs.currentWidget().setUrl(q)
        else:
            # Verwende die ausgewählte Suchmaschine für die Suche
            engine_name = self.settings.get("search_engine", "Google")
            search_url = SEARCH_ENGINES.get(engine_name, SEARCH_ENGINES["Google"])
            
            # Ersetze {} mit dem Suchbegriff
            search_url = search_url.format(url_text)
            
            # Navigiere zur Suchmaschine mit dem Suchbegriff
            self.tabs.currentWidget().setUrl(QUrl(search_url))
    
    def navigateHome(self):
        # Navigiere zur Startseite
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def loadSettings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = {"search_engine": "Google"}
        else:
            self.settings = {"search_engine": "Google"}

    def loadSettingsPage(self):
        # Erstelle die Optionen für die Suchmaschinen
        options = ""
        current_engine = self.settings.get("search_engine", "Google")
        
        for engine in SEARCH_ENGINES.keys():
            selected = "selected" if engine == current_engine else ""
            options += f'<option value="{engine}" {selected}>{engine}</option>'
        
        # Fülle das HTML-Template
        html = SETTINGS_HTML.format(options=options, current=current_engine)
        
        # Lade die Einstellungs-Seite
        current_tab = self.tabs.currentWidget()
        current_tab.setHtml(html, QUrl("vortex://settings"))
        
        # Setze die URL-Bar
        self.url_bar.setText("vortex://settings")
        
        # Aktualisiere den Tab-Titel
        self.tabs.setTabText(self.tabs.currentIndex(), "Einstellungen")
    
    def saveSettings(self, new_settings):
        # Aktualisiere die Einstellungen
        self.settings.update(new_settings)
        
        # Speichere die Einstellungen in der Datei
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)
        
        # Zeige eine Bestätigung
        self.status.showMessage("Einstellungen gespeichert", 3000)

if __name__ == "__main__":
    # Erstelle die Anwendung
    app = QApplication(sys.argv)
    
    # Erstelle das Browserfenster
    window = Browser()
    window.show()
    
    # Starte die Anwendung
    sys.exit(app.exec_()) 