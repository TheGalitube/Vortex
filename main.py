import sys
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                           QToolBar, QLineEdit, QPushButton, QVBoxLayout, 
                           QWidget, QHBoxLayout, QMenu, QStatusBar, QAction, QStyle)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
import os
import json
import qtawesome as qta
import base64

# Suchmaschinen-Presets
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q={}",
    "Bing": "https://www.bing.com/search?q={}",
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
    "Ecosia": "https://www.ecosia.org/search?q={}",
    "Qwant": "https://www.qwant.com/?q={}"
}

# Standard angepinnte Seiten
DEFAULT_PINNED_SITES = [
    {"title": "Google", "url": "https://www.google.com", "icon": "fa5s.search"},
    {"title": "YouTube", "url": "https://www.youtube.com", "icon": "fa5b.youtube"},
    {"title": "Wikipedia", "url": "https://www.wikipedia.org", "icon": "fa5b.wikipedia-w"},
    {"title": "GitHub", "url": "https://www.github.com", "icon": "fa5b.github"}
]

# Moderner Chrome User-Agent
MODERN_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# New Tab HTML Template
NEW_TAB_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Neue Registerkarte</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #2c2c2c;
            color: #ffffff;
            text-align: center;
        }}
        .container {{
            width: 80%;
            margin: 0 auto;
            padding-top: 100px;
        }}
        .search-box {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto 40px;
            position: relative;
        }}
        .search-input {{
            width: 100%;
            padding: 15px 20px;
            border-radius: 30px;
            border: none;
            background-color: #404040;
            color: white;
            font-size: 16px;
            outline: none;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }}
        .search-engine {{
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #aaa;
            font-size: 14px;
            background: none;
            border: none;
        }}
        .pinned-sites {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 40px;
            gap: 20px;
        }}
        .site-tile {{
            width: 120px;
            height: 120px;
            background-color: #333;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.2s;
            text-decoration: none;
            color: white;
            position: relative;
        }}
        .site-tile:hover {{
            background-color: #404040;
            transform: translateY(-5px);
        }}
        .site-icon {{
            font-size: 32px;
            margin-bottom: 10px;
            color: #42a5f5;
        }}
        .site-title {{
            font-size: 14px;
        }}
        .add-site {{
            border: 2px dashed #555;
            background-color: transparent;
        }}
        .add-site:hover {{
            border-color: #42a5f5;
            background-color: #353535;
        }}
        .add-icon {{
            font-size: 32px;
            color: #555;
        }}
        .add-site:hover .add-icon {{
            color: #42a5f5;
        }}
        .logo {{
            margin-bottom: 40px;
            font-size: 32px;
            font-weight: bold;
            color: #42a5f5;
        }}
        .unpin {{
            position: absolute;
            top: 5px;
            right: 5px;
            background: rgba(0, 0, 0, 0.5);
            color: #fff;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        .site-tile:hover .unpin {{
            opacity: 1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Vortex</div>
        
        <div class="search-box">
            <input type="text" class="search-input" placeholder="Suche oder URL eingeben..." autofocus id="search-input">
            <span class="search-engine">{current_engine}</span>
        </div>
        
        <div class="pinned-sites">
            {pinned_sites}
            
            <div class="site-tile add-site" onclick="showAddSiteDialog()">
                <div class="add-icon">+</div>
                <div class="site-title">Seite hinzufügen</div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('search-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                const query = this.value.trim();
                if (query) {{
                    // Wenn es eine URL ist, direkt dorthin navigieren
                    if (query.includes('.') && !query.includes(' ')) {{
                        let url = query;
                        if (!url.startsWith('http://') && !url.startsWith('https://')) {{
                            url = 'http://' + url;
                        }}
                        window.location.href = url;
                    }} else {{
                        // Sonst als Suchanfrage behandeln
                        window.location.href = 'vortex://search?q=' + encodeURIComponent(query);
                    }}
                }}
            }}
        }});

        function showAddSiteDialog() {{
            const title = prompt('Titel der Webseite:');
            if (title) {{
                const url = prompt('URL der Webseite (mit https://):');
                if (url && url.trim().startsWith('http')) {{
                    window.location.href = 'vortex://pin-site?title=' + encodeURIComponent(title) + '&url=' + encodeURIComponent(url);
                }} else {{
                    alert('Bitte gib eine gültige URL ein, die mit http:// oder https:// beginnt.');
                }}
            }}
        }}

        function unpinSite(url) {{
            if (confirm('Möchtest du diese Seite wirklich entfernen?')) {{
                window.location.href = 'vortex://unpin-site?url=' + encodeURIComponent(url);
            }}
        }}
    </script>
</body>
</html>
"""

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

# Benutzerdefinierter Request-Interceptor für den User-Agent
class CustomRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        info.setHttpHeader(b"User-Agent", MODERN_USER_AGENT.encode())
        
        # Erlaube alle Schriftarten-Ressourcen
        if info.resourceType() == QWebEngineUrlRequestInfo.ResourceTypeFontResource:
            info.setHttpHeader(b"Accept", b"*/*")

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
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
            elif url.host() == "new-tab":
                self.browser.loadNewTabPage()
                return False
            elif url.host() == "search":
                try:
                    query = url.query()
                    if "q=" in query:
                        search_term = query.split("q=")[1].split("&")[0]
                        search_term = search_term.replace("+", " ")  # Korrigiere URL-Codierung
                        self.browser.performSearch(search_term)
                except Exception as e:
                    print(f"Fehler bei der Suche: {e}")
                    self.browser.status.showMessage(f"Fehler: {e}", 3000)
                return False
            elif url.host() == "pin-site":
                try:
                    query = url.query()
                    title = ""
                    url_value = ""
                    
                    if "title=" in query:
                        title = query.split("title=")[1].split("&")[0]
                        title = title.replace("+", " ")
                    
                    if "url=" in query:
                        url_value = query.split("url=")[1].split("&")[0]
                        
                    self.browser.pinSite(title, url_value)
                    self.browser.loadNewTabPage()
                except Exception as e:
                    print(f"Fehler beim Anpinnen der Seite: {e}")
                    self.browser.status.showMessage(f"Fehler: {e}", 3000)
                return False
            elif url.host() == "unpin-site":
                try:
                    query = url.query()
                    if "url=" in query:
                        url_value = query.split("url=")[1].split("&")[0]
                        self.browser.unpinSite(url_value)
                    self.browser.loadNewTabPage()
                except Exception as e:
                    print(f"Fehler beim Entfernen der Seite: {e}")
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
        
        # Erstelle ein optimiertes WebEngineProfile
        self.setupWebEngineProfile()
        
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
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)  # Nur Icons anzeigen
        self.addToolBar(self.toolbar)
        
        # Zurück-Button
        self.back_btn = QAction(qta.icon('fa5s.arrow-left', color='white'), "", self)
        self.back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.toolbar.addAction(self.back_btn)
        
        # Vorwärts-Button
        self.forward_btn = QAction(qta.icon('fa5s.arrow-right', color='white'), "", self)
        self.forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.toolbar.addAction(self.forward_btn)
        
        # Neu laden Button
        self.reload_btn = QAction(qta.icon('fa5s.sync', color='white'), "", self)
        self.reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.toolbar.addAction(self.reload_btn)
        
        # Home-Button
        self.home_btn = QAction(qta.icon('fa5s.home', color='white'), "", self)
        self.home_btn.triggered.connect(self.loadNewTabPage)
        self.toolbar.addAction(self.home_btn)
        
        # Neuer Tab Button
        self.add_tab_btn = QAction(qta.icon('fa5s.plus', color='white'), "", self)
        self.add_tab_btn.triggered.connect(lambda: self.addTab())
        self.toolbar.addAction(self.add_tab_btn)
        
        # URL-Eingabefeld
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigateToUrl)
        self.toolbar.addWidget(self.url_bar)
        
        # Settings Button
        self.settings_btn = QAction(qta.icon('fa5s.cog', color='white'), "", self)
        self.settings_btn.triggered.connect(self.loadSettingsPage)
        self.toolbar.addAction(self.settings_btn)
        
        # Füge die Tabs zum Layout hinzu
        self.layout.addWidget(self.tabs)
        
        # Statusleiste
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Erstelle einen ersten Tab
        self.addTab()
    
    def setupWebEngineProfile(self):
        # Erstelle ein globales Profil mit optimierten Einstellungen
        self.profile = QWebEngineProfile("vortex_profile")
        
        # Setze Cache-Größe auf 100 MB
        self.profile.setCachePath(os.path.join(os.path.expanduser("~"), ".vortex_cache"))
        self.profile.setPersistentStoragePath(os.path.join(os.path.expanduser("~"), ".vortex_storage"))
        self.profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        self.profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100 MB
        
        # Setze benutzerdefinierten User-Agent
        self.interceptor = CustomRequestInterceptor()
        self.profile.setUrlRequestInterceptor(self.interceptor)
        
        # Globale WebEngine-Einstellungen
        settings = QWebEngineSettings.globalSettings()
        
        # Aktiviere moderne Web-Funktionen
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadIconsForPage, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        
        # Verbesserte Unterstützung für Schriftarten
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)  # Wichtig für Font-Ressourcen
        
        # Explizite Aktivierung von Web-Fonts
        try:
            # Ab Qt 5.10 verfügbar
            settings.setAttribute(QWebEngineSettings.WebFontsEnabled, True)
        except:
            print("WebFontsEnabled nicht verfügbar in dieser Qt-Version, Web-Fonts sollten aber trotzdem funktionieren")
        
        # Setze Schriftart-Rendering-Optionen
        # Standard-Schriftarten definieren
        settings.setFontFamily(QWebEngineSettings.StandardFont, "Arial")
        settings.setFontFamily(QWebEngineSettings.FixedFont, "Courier New")
        settings.setFontFamily(QWebEngineSettings.SerifFont, "Times New Roman")
        settings.setFontFamily(QWebEngineSettings.SansSerifFont, "Arial")
        
        # Standardgröße für Schriften
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)
        settings.setFontSize(QWebEngineSettings.DefaultFixedFontSize, 14)
        settings.setFontSize(QWebEngineSettings.MinimumFontSize, 10)
        
        # HTML5-Funktionen aktivieren
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        
        # Moderne Premium-Funktionen (wenn verfügbar in dieser Qt-Version)
        try:
            settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
            settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        except:
            pass
        
        # Hardware-Beschleunigung für bessere Performance
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu --enable-accelerated-2d-canvas --enable-accelerated-vpx-decode --ignore-gpu-blacklist"
    
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
        page = CustomWebEnginePage(self.profile, self)
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
            self.loadNewTabPage(browser)
    
    def closeTab(self, i):
        # Schließe den Tab, wenn mehr als ein Tab geöffnet ist
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            # Wenn es der letzte Tab ist, öffne einen neuen
            self.loadNewTabPage(self.tabs.widget(0))
    
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
            self.performSearch(url_text)
    
    def performSearch(self, search_term):
        engine_name = self.settings.get("search_engine", "Google")
        search_url = SEARCH_ENGINES.get(engine_name, SEARCH_ENGINES["Google"])
        
        # Ersetze {} mit dem Suchbegriff
        search_url = search_url.format(search_term)
        
        # Navigiere zur Suchmaschine mit dem Suchbegriff
        self.tabs.currentWidget().setUrl(QUrl(search_url))
    
    def loadNewTabPage(self, browser=None):
        # Verwende den aktuellen Tab, falls keiner angegeben wurde
        if browser is None:
            browser = self.tabs.currentWidget()
        
        # Erstelle die Liste der angepinnten Seiten
        pinned_sites_html = ""
        pinned_sites = self.settings.get("pinned_sites", DEFAULT_PINNED_SITES)
        
        for site in pinned_sites:
            title = site.get("title", "")
            url = site.get("url", "")
            icon = site.get("icon", "fa5s.globe")
            
            pinned_sites_html += f"""
            <a href="{url}" class="site-tile">
                <div class="site-icon"><i class="{icon}"></i></div>
                <div class="site-title">{title}</div>
                <button class="unpin" onclick="event.preventDefault(); unpinSite('{url}');">×</button>
            </a>
            """
        
        # Fülle das HTML-Template
        current_engine = self.settings.get("search_engine", "Google")
        html = NEW_TAB_HTML.format(current_engine=current_engine, pinned_sites=pinned_sites_html)
        
        # Lade die New-Tab-Seite
        browser.setHtml(html, QUrl("vortex://new-tab"))
        
        # Setze die URL-Bar
        self.url_bar.setText("vortex://new-tab")
        
        # Aktualisiere den Tab-Titel
        self.tabs.setTabText(self.tabs.currentIndex(), "Neue Registerkarte")

    def pinSite(self, title, url):
        if not title or not url:
            return
        
        # Extrahiere Favicon für dieses Icon
        icon = self.getFaviconForDomain(url)
        
        # Erstelle einen neuen Eintrag
        new_site = {
            "title": title,
            "url": url,
            "icon": icon
        }
        
        # Füge die neue Seite zu den angepinnten Seiten hinzu
        pinned_sites = self.settings.get("pinned_sites", DEFAULT_PINNED_SITES)
        
        # Prüfe, ob die URL bereits existiert
        for i, site in enumerate(pinned_sites):
            if site.get("url") == url:
                pinned_sites[i] = new_site
                break
        else:
            # Wenn die URL noch nicht existiert, füge sie hinzu
            pinned_sites.append(new_site)
        
        # Aktualisiere die Einstellungen
        self.settings["pinned_sites"] = pinned_sites
        self.saveSettings()
    
    def unpinSite(self, url):
        if not url:
            return
        
        # Entferne die Seite aus den angepinnten Seiten
        pinned_sites = self.settings.get("pinned_sites", DEFAULT_PINNED_SITES)
        
        # Filtere die zu entfernende Seite heraus
        pinned_sites = [site for site in pinned_sites if site.get("url") != url]
        
        # Aktualisiere die Einstellungen
        self.settings["pinned_sites"] = pinned_sites
        self.saveSettings()
    
    def getFaviconForDomain(self, url):
        # URL der Domain extrahieren
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            # Bestimme ein passendes Icon für bekannte Domains
            if "google" in domain:
                return "fa5b.google"
            elif "youtube" in domain:
                return "fa5b.youtube"
            elif "github" in domain:
                return "fa5b.github"
            elif "twitter" in domain or "x.com" in domain:
                return "fa5b.twitter"
            elif "facebook" in domain:
                return "fa5b.facebook"
            elif "instagram" in domain:
                return "fa5b.instagram"
            elif "reddit" in domain:
                return "fa5b.reddit"
            elif "wikipedia" in domain:
                return "fa5b.wikipedia-w"
            elif "linkedin" in domain:
                return "fa5b.linkedin"
            elif "amazon" in domain:
                return "fa5b.amazon"
            elif "microsoft" in domain:
                return "fa5b.microsoft"
            elif "apple" in domain:
                return "fa5b.apple"
            else:
                return "fa5s.globe"
        except:
            return "fa5s.globe"

    def loadSettings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = {
                    "search_engine": "Google",
                    "pinned_sites": DEFAULT_PINNED_SITES
                }
        else:
            self.settings = {
                "search_engine": "Google",
                "pinned_sites": DEFAULT_PINNED_SITES
            }

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
    
    def saveSettings(self, new_settings=None):
        # Aktualisiere die Einstellungen, falls neue übergeben wurden
        if new_settings:
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