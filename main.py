import sys
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                           QToolBar, QLineEdit, QPushButton, QVBoxLayout, 
                           QWidget, QHBoxLayout, QMenu, QStatusBar, QAction, QStyle, QTabBar, QLabel)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
import os
import json
import qtawesome as qta
import base64

# Windows-spezifische Importe für Darkmode-Titelleiste
if sys.platform == 'win32':
    from PyQt5.QtWinExtras import QtWin
    import ctypes

# Suchmaschinen-Konfiguration
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q={query}",
    "Bing": "https://www.bing.com/search?q={query}",
    "DuckDuckGo": "https://duckduckgo.com/?q={query}",
    "Yahoo": "https://search.yahoo.com/search?p={query}",
    "Ecosia": "https://www.ecosia.org/search?q={query}",
    "Startpage": "https://www.startpage.com/do/search?q={query}",
    "Qwant": "https://www.qwant.com/?q={query}"
}

# Standard-Favoriten
DEFAULT_PINNED_SITES = [
    {"title": "Google", "url": "https://www.google.com"},
    {"title": "YouTube", "url": "https://www.youtube.com"},
    {"title": "GitHub", "url": "https://github.com"},
    {"title": "Wikipedia", "url": "https://www.wikipedia.org"},
    {"title": "Reddit", "url": "https://www.reddit.com"}
]

# Moderner Chrome User-Agent
MODERN_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# HTML-Template für die Neue-Tab-Seite
NEW_TAB_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Neuer Tab</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #202124;
            color: #e8eaed;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .search-container {{
            margin: 100px 0 40px 0;
            width: 100%;
            max-width: 600px;
            text-align: center;
        }}
        
        .search-bar {{
            width: 100%;
            padding: 12px 20px;
            margin: 8px 0;
            box-sizing: border-box;
            border: 1px solid #5f6368;
            border-radius: 24px;
            background-color: #303134;
            color: #e8eaed;
            font-size: 16px;
            outline: none;
        }}
        
        .search-bar:focus {{
            border-color: #8ab4f8;
            background-color: #303134;
        }}
        
        .sites-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 16px;
            margin-top: 30px;
            width: 100%;
            max-width: 800px;
        }}
        
        .site-tile {{
            position: relative;
            width: 110px;
            height: 110px;
            background-color: #303134;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: #e8eaed;
            transition: background-color 0.2s;
        }}
        
        .site-tile:hover {{
            background-color: #3c4043;
        }}
        
        .site-link {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: #e8eaed;
            width: 100%;
            height: 100%;
            padding: 10px;
            box-sizing: border-box;
        }}
        
        .site-icon {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background-color: #5f6368;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 8px;
            font-size: 24px;
        }}
        
        .site-icon img {{
            width: 24px;
            height: 24px;
        }}
        
        .site-title {{
            font-size: 12px;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        }}
        
        .unpin-button {{
            position: absolute;
            top: 5px;
            right: 5px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: rgba(80, 80, 80, 0.7);
            color: #e8eaed;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            font-size: 16px;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        
        .site-tile:hover .unpin-button {{
            opacity: 1;
        }}
        
        .unpin-button:hover {{
            background-color: rgba(100, 100, 100, 0.9);
        }}
    </style>
    <!-- FontAwesome CDN für Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
</head>
<body>
    <div class="search-container">
        <form action="javascript:void(0);" onsubmit="submitSearch()">
            <input type="text" class="search-bar" id="searchInput" placeholder="{search_input_placeholder}" autofocus>
        </form>
    </div>
    
    <div class="sites-container">
        {pinned_sites}
    </div>
    
    <script>
        function submitSearch() {{
            const input = document.getElementById('searchInput').value.trim();
            if (input) {{
                // Prüfe, ob es eine URL ist
                if (input.includes('.') && !input.includes(' ')) {{
                    // Füge http:// hinzu, wenn kein Protokoll angegeben ist
                    if (!input.startsWith('http://') && !input.startsWith('https://')) {{
                        window.location.href = 'http://' + input;
                    }} else {{
                        window.location.href = input;
                    }}
                }} else {{
                    // Behandle es als Suchanfrage
                    window.location.href = input;
                }}
            }}
        }}
        
        // Setze Fokus auf das Suchfeld
        document.addEventListener('DOMContentLoaded', function() {{
            document.getElementById('searchInput').focus();
        }});
    </script>
</body>
</html>
"""

# HTML-Template für die Einstellungs-Seite
SETTINGS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Einstellungen</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #202124;
            color: #e8eaed;
            margin: 0;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .settings-container {{
            width: 100%;
            max-width: 600px;
        }}
        
        h1 {{
            margin-bottom: 30px;
            text-align: center;
            color: #e8eaed;
        }}
        
        .settings-section {{
            background-color: #303134;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .settings-title {{
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 15px;
            color: #e8eaed;
        }}
        
        select {{
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            background-color: #202124;
            color: #e8eaed;
            border: 1px solid #5f6368;
            border-radius: 4px;
            outline: none;
        }}
        
        select:focus {{
            border-color: #8ab4f8;
        }}
        
        button {{
            background-color: #8ab4f8;
            color: #202124;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        
        button:hover {{
            background-color: #aecbfa;
        }}
        
        .info-text {{
            font-size: 14px;
            color: #9aa0a6;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="settings-container">
        <h1>Vortex Browser Einstellungen</h1>
        
        <div class="settings-section">
            <div class="settings-title">Suchmaschine</div>
            <form action="vortex://save-settings" method="get">
                <select name="engine">
                    {options}
                </select>
                <button type="submit">Speichern</button>
            </form>
            <div class="info-text">
                Aktuell ausgewählt: <strong>{current}</strong>
            </div>
        </div>
        
        <div class="settings-section">
            <div class="settings-title">Über Vortex Browser</div>
            <div class="info-text">
                Version: 1.0.0<br>
                Ein moderner, leichtgewichtiger Browser basierend auf QtWebEngine.
            </div>
        </div>
    </div>
</body>
</html>
"""

# Benutzerdefinierter Request-Interceptor für den User-Agent
class CustomRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def interceptRequest(self, info):
        # Setze einen benutzerdefinierten User-Agent
        info.setHttpHeader(b"User-Agent", b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vortex/1.0.0")

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
        self.browsers = []
        
        # Fenster-Eigenschaften
        self.setWindowTitle("Vortex Browser")
        
        # Setze das Programm-Icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vortex-icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Layout für die Hauptfensterelemente
        self.layout = QVBoxLayout()
        
        # Windows-Darkmode für Titelleiste aktivieren
        if sys.platform == 'win32':
            self.enableWindowsDarkMode()
        
        # Zentrale Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Erstelle Tab-Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(False)  # Wir implementieren unsere eigenen Close-Buttons
        self.tabs.setMovable(True)
        self.tabs.setElideMode(Qt.ElideRight)  # Text wird mit Ellipsis gekürzt
        self.tabs.setUsesScrollButtons(True)  # Aktiviere Scroll-Buttons für viele Tabs
        
        # Tab Bar konfigurieren für linksbündige Anordnung
        tab_bar = self.tabs.tabBar()
        tab_bar.setExpanding(False)  # Tabs werden nicht ausdehnen, um den Platz zu füllen
        tab_bar.setDrawBase(True)
        tab_bar.setUsesScrollButtons(True)
        tab_bar.setDocumentMode(True)
        tab_bar.setElideMode(Qt.ElideRight)  # Text mit Ellipsis am Ende kürzen
        
        # Neu Tab Button
        self.new_tab_button = QPushButton()
        self.new_tab_button.setIcon(qta.icon('fa5s.plus', color='white'))
        self.new_tab_button.setObjectName("new_tab_button")
        self.new_tab_button.setToolTip("Neuer Tab")
        self.new_tab_button.clicked.connect(self.addTab)
        self.tabs.setCornerWidget(self.new_tab_button, Qt.TopRightCorner)
        
        # Erstelle Navigations-Toolbar mit QHBoxLayout für bessere Kontrolle
        self.nav_toolbar = QToolBar("Navigation")
        self.nav_toolbar.setObjectName("nav_toolbar")
        self.nav_toolbar.setMovable(False)
        self.nav_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.nav_toolbar.setIconSize(QSize(18, 18))
        
        # Container für die gesamte Navigationsleiste
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(5, 2, 5, 2)
        nav_layout.setSpacing(4)
        
        # Navigation-Buttons in einer Gruppe
        nav_buttons = QWidget()
        buttons_layout = QHBoxLayout(nav_buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(2)
        
        # Zurück-Button
        back_btn = QPushButton()
        back_btn.setIcon(qta.icon('fa5s.arrow-left', color='white'))
        back_btn.setToolTip("Zurück")
        back_btn.setObjectName("nav_button")
        back_btn.clicked.connect(self.navigateBack)
        buttons_layout.addWidget(back_btn)
        
        # Vorwärts-Button
        forward_btn = QPushButton()
        forward_btn.setIcon(qta.icon('fa5s.arrow-right', color='white'))
        forward_btn.setToolTip("Vorwärts")
        forward_btn.setObjectName("nav_button")
        forward_btn.clicked.connect(self.navigateForward)
        buttons_layout.addWidget(forward_btn)
        
        # Neu-laden-Button
        reload_btn = QPushButton()
        reload_btn.setIcon(qta.icon('fa5s.sync', color='white'))
        reload_btn.setToolTip("Neu laden")
        reload_btn.setObjectName("nav_button")
        reload_btn.clicked.connect(self.reloadPage)
        buttons_layout.addWidget(reload_btn)
        
        # Home-Button
        home_btn = QPushButton()
        home_btn.setIcon(qta.icon('fa5s.home', color='white'))
        home_btn.setToolTip("Startseite")
        home_btn.setObjectName("nav_button")
        home_btn.clicked.connect(self.loadNewTabPage)
        buttons_layout.addWidget(home_btn)
        
        # Füge die Navigationsbuttons zum Layout hinzu
        nav_layout.addWidget(nav_buttons)
        
        # URL-Leiste
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigateToUrl)
        self.url_bar.setPlaceholderText("Suche oder Adresse eingeben")
        nav_layout.addWidget(self.url_bar, 1)  # Stretch-Faktor 1 für dynamische Anpassung
        
        # Einstellungen-Button
        settings_btn = QPushButton()
        settings_btn.setIcon(qta.icon('fa5s.cog', color='white'))
        settings_btn.setToolTip("Einstellungen")
        settings_btn.setObjectName("nav_button")
        settings_btn.clicked.connect(self.loadSettingsPage)
        nav_layout.addWidget(settings_btn)
        
        # Füge den Container zur Toolbar hinzu
        self.nav_toolbar.addWidget(nav_container)
        
        # Füge die Navigationsleiste zum Layout hinzu
        self.layout.addWidget(self.nav_toolbar)
        
        # Entferne die Tabs aus der Navigationsleiste
        nav_layout.removeWidget(self.tabs)

        # Erstelle Tab-Toolbar
        self.tabs_toolbar = QToolBar("Tabs")
        self.tabs_toolbar.setObjectName("tabs_toolbar")
        self.tabs_toolbar.setMovable(False)
        self.tabs_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        
        # Füge Tabs zur Tab-Toolbar hinzu und setze Ausrichtung linksbündig
        self.tabs_hbox = QHBoxLayout()
        self.tabs_hbox.setContentsMargins(0, 0, 0, 0)
        self.tabs_hbox.addWidget(self.tabs)
        self.tabs_hbox.addStretch(1)  # Fügt Stretchfaktor hinzu, damit die Tabs linksbündig sind
        self.tabs_toolbar_widget = QWidget()
        self.tabs_toolbar_widget.setLayout(self.tabs_hbox)
        self.tabs_toolbar.addWidget(self.tabs_toolbar_widget)

        # Füge die Tab-Toolbar zum Layout hinzu (vor der Navigationsleiste)
        self.layout.removeWidget(self.nav_toolbar)
        self.layout.addWidget(self.tabs_toolbar)
        self.layout.addWidget(self.nav_toolbar)
        
        # Lade Einstellungen
        self.settings = self.loadSettings()
        
        # WebEngine-Profile mit benutzerdefinierten Einstellungen
        self.setupWebEngineProfile()
        
        # Dunkler Modus
        self.setDarkMode()
        
        # Füge ersten Tab hinzu
        self.addTab()
        
        # Verbinde Tab-Wechselsignal
        self.tabs.currentChanged.connect(self.onTabChange)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        
        # Setze Fenstergröße und Position
        self.resize(1000, 800)
        self.move(100, 100)
    
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
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(33, 33, 36))  # Dunkler für bessere Harmonie mit Titelleiste
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Modernes Stylesheet für den Browser
        self.setStyleSheet("""
            QMainWindow {
                background-color: #202124;
                color: #ffffff;
            }
            
            QStatusBar {
                background-color: #202124;
                color: #9aa0a6;
                border-top: 1px solid #3c4043;
            }
            
            #tabs_toolbar {
                background-color: #202124;
                padding: 0px;
                margin: 0px 0px 0px 0px;
                min-height: 32px;
                max-height: 32px;
                border: none;
            }
            
            #nav_toolbar {
                background-color: #292b2f;
                border-top: none;
                border-bottom: none;
                padding: 0px;
                min-height: 40px;
                margin-top: 0px;
            }
            
            QTabBar {
                alignment: left;
                margin-bottom: 0px;
                margin-left: 4px;
            }
            
            QTabBar::tab {
                background-color: #202124;
                color: #9aa0a6;
                border: none;
                padding: 5px 12px 9px 12px;
                min-width: 40px;
                max-width: 200px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-bottom: 0px;
                margin-top: 1px;
            }
            
            QTabBar::tab:selected {
                background-color: #35363a;
                color: #ffffff;
                border-bottom: 2px solid #8ab4f8;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #292b2f;
            }
            
            QTabBar::close-button {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMiAybDggOG0wLThsLTggOCIgc3Ryb2tlPSIjOWFhMGE2IiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PC9zdmc+);
                margin: 2px 4px 0px 4px;
                border-radius: 2px;
            }
            
            QTabBar::close-button:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            QTabBar::scroller {
                width: 20px;
            }
            
            QTabBar QToolButton {
                background-color: #202124;
                border: none;
            }
            
            QTabBar QToolButton::right-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMyAxTDcgNUwzIDkiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            
            QTabBar QToolButton::left-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNNyAxTDMgNUw3IDkiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
            }
            
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            
            QToolButton:hover {
                background-color: #3c4043;
            }
            
            /* Styling für die Navigationsbuttons */
            #nav_button {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
                margin: 1px;
                min-width: 26px;
                max-width: 26px;
                min-height: 26px;
                max-height: 26px;
            }
            
            #nav_button:hover {
                background-color: #3c4043;
            }
            
            #nav_button:pressed {
                background-color: #4c4f52;
            }
            
            #new_tab_button {
                background-color: transparent;
                border: none;
                padding: 4px 8px;
                margin: 5px;
                border-radius: 4px;
            }
            
            #new_tab_button:hover {
                background-color: #3c4043;
            }
            
            QLineEdit {
                background-color: #35363a;
                color: white;
                padding: 6px 8px;
                border-radius: 4px;
                border: 1px solid #5f6368;
                selection-background-color: #1a73e8;
            }
            
            QLineEdit:focus {
                border: 1px solid #8ab4f8;
            }
            
            #tab_close_button {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 0px;
                margin: 0px;
            }
            
            #tab_close_button:hover {
                background-color: #494a4e;
            }
            
            #tab_close_button:pressed {
                background-color: #5f6064;
            }
            
            #tab_label {
                color: #ffffff;
                margin: 0px;
                padding: 0px;
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
        
        # Füge den Browser zum Content-Container hinzu
        self.layout.addWidget(browser)
        
        # Füge den Tab hinzu
        i = self.tabs.addTab(QWidget(), "Neuer Tab")
        self.tabs.setCurrentIndex(i)
        
        # Verknüpfe Tab-Änderungen mit dem Inhalt
        self.tabs.currentChanged.connect(self.onTabChange)
        
        # Speichere den Browser in einer Liste
        self.browsers.append(browser)
        
        # Zeige den aktuellen Browser
        self.onTabChange(i)
        
        # Füge den Close-Button hinzu
        self.addCloseButtonToTab(i)
        
        # Wenn eine URL übergeben wurde, navigiere dorthin, ansonsten zur Startseite
        if qurl:
            browser.setUrl(qurl)
        else:
            self.loadNewTabPage(browser)
            
        return i, browser
    
    def onTabChange(self, index):
        # Verstecke alle Browser
        if hasattr(self, 'browsers'):
            for browser in self.browsers:
                browser.hide()
            
            # Zeige den aktuellen Browser
            if index >= 0 and index < len(self.browsers):
                self.browsers[index].show()
                
                # Aktualisiere die URL-Leiste
                current_url = self.browsers[index].url()
                self.updateUrlBar(current_url, self.browsers[index])
    
    def closeTab(self, i):
        # Schließe den Tab, wenn mehr als ein Tab geöffnet ist
        if self.tabs.count() > 1:
            # Entferne den Browser aus der Liste
            if hasattr(self, 'browsers') and i < len(self.browsers):
                browser = self.browsers[i]
                self.layout.removeWidget(browser)
                browser.deleteLater()
                self.browsers.pop(i)
            
            # Entferne den Tab
            self.tabs.removeTab(i)
            
            # Aktualisiere die Tab-Indizes in den Close-Buttons
            self.updateTabCloseButtons()
        else:
            # Lade eine neue Tab-Seite, wenn es der letzte Tab ist
            if hasattr(self, 'browsers') and len(self.browsers) > 0:
                browser = self.browsers[0]
                self.loadNewTabPage(browser)
    
    def updateUrlBar(self, q, browser=None):
        # Aktualisiere die URL-Leiste
        if not hasattr(self, 'browsers') or not browser:
            return
            
        # Finde den aktuellen Browser-Index
        current_index = self.tabs.currentIndex()
        if current_index < 0 or current_index >= len(self.browsers):
            return
            
        current_browser = self.browsers[current_index]
        if browser != current_browser:
            return
        
        # Setze den Text in der URL-Leiste - nur die Domain anzeigen
        url_text = q.toString()
        if q.scheme() in ["http", "https"]:
            domain = q.host()
            self.url_bar.setText(domain)
        else:
            self.url_bar.setText(url_text)
    
    def updateTabTitle(self, title):
        # Aktualisiere den Tab-Titel
        current_index = self.tabs.currentIndex()
        
        # Setze einen Standardtitel, wenn keiner vorhanden ist
        if not title:
            title = "Unbenannt"
        
        # Aktualisiere den Tab-Titel (wird von addCloseButtonToTab verwendet)
        self.tabs.setTabText(current_index, title)
        
        # Aktualisiere den Close-Button und den Titel
        self.addCloseButtonToTab(current_index)
        
        # Aktualisiere den Fenstertitel
        self.setWindowTitle(f"{title} - Vortex Browser")
    
    def navigateToUrl(self, qurl=None):
        # Überprüfe, ob eine URL übergeben wurde oder aus der URL-Leiste geholt werden soll
        if qurl is not None:
            url = qurl
        else:
            # Hole die URL aus der URL-Leiste
            url_text = self.url_bar.text().strip()
            
            # Wenn die URL leer ist, nichts tun
            if not url_text:
                return
                
            # Prüfe, ob es sich um eine Suchanfrage oder eine URL handelt
            if not url_text.startswith(('http://', 'https://', 'file://')) and not '.' in url_text:
                # Es ist eine Suchanfrage, verwende die konfigurierte Suchmaschine
                engine = self.settings.get("search_engine", "Google")
                search_url = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["Google"])
                url = QUrl(search_url.replace("{query}", url_text))
            else:
                # Es ist eine URL
                if not url_text.startswith(('http://', 'https://', 'file://')):
                    url_text = 'http://' + url_text
                url = QUrl(url_text)
        
        # Lade die URL in den aktuellen Browser
        if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            self.browsers[self.tabs.currentIndex()].setUrl(url)
    
    def loadNewTabPage(self, browser=None):
        # Startseite oder neue Tab-Seite laden
        if not browser and hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            browser = self.browsers[self.tabs.currentIndex()]
            
        if browser:
            # Erstelle HTML für die neue Tab-Seite mit Favoriten
            html = NEW_TAB_HTML.format(
                pinned_sites=self.generatePinnedSites(),
                search_input_placeholder=f"Mit {self.settings.get('search_engine', 'Google')} suchen oder URL eingeben"
            )
            browser.setHtml(html, QUrl("vortex://newtab"))
            self.tabs.setTabText(self.tabs.currentIndex(), "Neuer Tab")
            self.url_bar.setText("")

    def generatePinnedSites(self):
        # Generiere die HTML für die angepinnten Seiten
        sites_html = ""
        for site in self.settings.get("pinned_sites", DEFAULT_PINNED_SITES):
            icon_name = self.getFaviconForDomain(site["url"])
            sites_html += f"""
            <div class="site-tile">
                <a href="{site['url']}" class="site-link">
                    <div class="site-icon">
                        <i class="{icon_name}"></i>
                    </div>
                    <div class="site-title">{site['title']}</div>
                </a>
                <a href="vortex://unpin-site?url={site['url']}" class="unpin-button">×</a>
            </div>
            """
        return sites_html
        
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
        # Eine Seite aus den Favoriten entfernen
        pinned_sites = self.settings.get("pinned_sites", DEFAULT_PINNED_SITES)
        self.settings["pinned_sites"] = [site for site in pinned_sites if site["url"] != url]
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
        # Einstellungsdatei im Benutzerverzeichnis
        self.settings_file = os.path.join(os.path.expanduser("~"), ".vortex_settings.json")
        
        # Versuche, vorhandene Einstellungen zu laden
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der Einstellungen: {e}")
                
        # Standard-Einstellungen zurückgeben, wenn keine Datei existiert oder ein Fehler auftritt
        return {
            "search_engine": "Google",
            "pinned_sites": DEFAULT_PINNED_SITES
        }
        
    def loadSettingsPage(self):
        # Prüfe, ob Browser verfügbar sind
        if not hasattr(self, 'browsers') or self.tabs.currentIndex() < 0 or self.tabs.currentIndex() >= len(self.browsers):
            return
            
        # Hole den aktuellen Browser
        current_browser = self.browsers[self.tabs.currentIndex()]
        
        # Erstelle die Optionen für die Suchmaschinen
        options = ""
        current_engine = self.settings.get("search_engine", "Google")
        
        for engine in SEARCH_ENGINES.keys():
            selected = "selected" if engine == current_engine else ""
            options += f'<option value="{engine}" {selected}>{engine}</option>'
        
        # Fülle das HTML-Template
        html = SETTINGS_HTML.format(options=options, current=current_engine)
        
        # Lade die Einstellungs-Seite
        current_browser.setHtml(html, QUrl("vortex://settings"))
        
        # Setze die URL-Bar
        self.url_bar.setText("vortex://settings")
        
        # Aktualisiere den Tab-Titel
        self.tabs.setTabText(self.tabs.currentIndex(), "Einstellungen")
    
    def saveSettings(self, new_settings=None):
        # Aktualisiere die Einstellungen, falls neue übergeben wurden
        if new_settings:
            self.settings.update(new_settings)
        
        # Speichere die Einstellungen in der Datei
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
            self.status.showMessage("Einstellungen gespeichert", 3000)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
            self.status.showMessage(f"Fehler beim Speichern: {e}", 3000)

    def navigateBack(self):
        if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            self.browsers[self.tabs.currentIndex()].back()
    
    def navigateForward(self):
        if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            self.browsers[self.tabs.currentIndex()].forward()
    
    def reloadPage(self):
        if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            self.browsers[self.tabs.currentIndex()].reload()

    def enableWindowsDarkMode(self):
        """Aktiviert den Dunkelmodus für die Windows-Titelleiste"""
        try:
            # Windows 10 1809 oder höher unterstützt DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            # Windows 10 (vor 1903) verwendet DWMWA_USE_IMMERSIVE_DARK_MODE = 19
            # Probiere beide Werte
            
            hwnd = int(self.winId())
            
            # Windows 10 1903+ verwenden Wert 20
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            dark_int = 1  # True für Dark Mode
            
            try:
                # ctypes verwenden, um DwmSetWindowAttribute aufzurufen
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(ctypes.c_int(dark_int)),
                    ctypes.sizeof(ctypes.c_int)
                )
            except:
                # Für ältere Windows 10 Versionen Wert 19 probieren
                DWMWA_USE_IMMERSIVE_DARK_MODE = 19
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(ctypes.c_int(dark_int)),
                    ctypes.sizeof(ctypes.c_int)
                )
            
            # Setze App-ID für bessere Integration mit Windows
            QtWin.setCurrentProcessExplicitAppUserModelID("Vortex.Browser")
            
            # Stelle sicher, dass die Fensterdekoration im dunklen Stil dargestellt wird
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            
            print("Dark Mode für Titelleiste aktiviert")
            
        except Exception as e:
            print(f"Fehler bei der Aktivierung des Dark Mode: {e}")
            # Wenn Dark Mode nicht aktiviert werden kann, fahre trotzdem fort

    # Funktion zum Hinzufügen des Close-Buttons zu einem Tab
    def addCloseButtonToTab(self, index):
        # Erstelle den Close-Button
        close_button = QPushButton()
        close_button.setIcon(qta.icon('fa5s.times', color='#9aa0a6'))
        close_button.setObjectName("tab_close_button")
        close_button.setFixedSize(16, 16)
        close_button.setToolTip("Tab schließen")
        close_button.setCursor(Qt.ArrowCursor)
        
        # Verbinde den Button mit der closeTab-Methode
        close_button.clicked.connect(lambda: self.closeTab(index))
        
        # Erstelle ein Widget als Container für den Tab-Titel und den Close-Button
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Füge den Tab-Titel hinzu
        label = QLabel(self.tabs.tabText(index))
        label.setObjectName("tab_label")
        layout.addWidget(label)
        
        # Füge den Close-Button hinzu
        layout.addWidget(close_button)
        
        # Setze das Widget als Tab-Widget
        self.tabs.setTabText(index, "")
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, tab_widget)

    # Füge eine neue Methode hinzu, um die Tab-Indizes in den Close-Buttons zu aktualisieren
    def updateTabCloseButtons(self):
        # Aktualisiere alle Tab-Close-Buttons mit den richtigen Indizes
        for i in range(self.tabs.count()):
            self.addCloseButtonToTab(i)

if __name__ == "__main__":
    # Erstelle die Anwendung
    app = QApplication(sys.argv)
    
    # Setze das Icon für die gesamte Anwendung
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vortex-icon.png")
    app.setWindowIcon(QIcon(icon_path))
    
    # Erstelle das Hauptfenster
    window = Browser()
    window.show()
    
    # Starte die Anwendung
    sys.exit(app.exec_()) 