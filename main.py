import sys
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                           QToolBar, QLineEdit, QPushButton, QVBoxLayout, 
                           QWidget, QHBoxLayout, QMenu, QStatusBar, QAction, QStyle, QTabBar, QLabel, QShortcut)
from PyQt5.QtGui import QIcon, QPalette, QColor, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings, QWebEngineProfile, QWebEngineScript
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
MODERN_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

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
        info.setHttpHeader(b"User-Agent", f"{MODERN_USER_AGENT} Vortex/1.1.0".encode())

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.browser = parent

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        # URL-String für Debug-Zwecke ausgeben
        url_str = url.toString()
        print(f"Navigation Request: {url_str}")
        
        if url.scheme() == "vortex":
            print(f"Vortex URL erkannt: {url_str}, Host: {url.host()}")
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
            elif url.host() == "devtools":
                self.browser.openDevTools()
                return False
            else:
                # Unbekannte vortex:// URL behandeln
                print(f"Unbekannte vortex:// URL: {url_str}")
                self.browser.status.showMessage(f"Unbekannte vortex:// URL: {url.host()}", 3000)
                return False
                
        # Chrome-spezifische URLs unterstützen
        elif url.scheme() == "chrome":
            print(f"Chrome URL erkannt: {url_str}, Host: {url.host()}")
            if url.host() == "settings":
                self.browser.loadSettingsPage()
                return False
            elif url.host() == "bookmarks":
                self.browser.loadNewTabPage()  # Anpassbar: Zeigt die Pinned Sites als "Bookmarks"
                return False
            elif url.host() == "history":
                self.browser.loadChromePage("history")
                return False
            elif url.host() == "downloads":
                self.browser.loadChromePage("downloads")
                return False
            elif url.host() == "extensions":
                self.browser.loadChromePage("extensions")
                return False
            elif url.host() == "version":
                self.browser.loadChromePage("version")
                return False
            elif url.host() == "devtools":
                self.browser.openDevTools()
                return False
            elif url.host() == "inspect":
                self.browser.openDevTools()
                return False
            elif url.host() == "newtab":
                self.browser.loadNewTabPage()
                return False
            else:
                # Unbekannte chrome:// URL behandeln
                print(f"Unbekannte chrome:// URL: {url_str}")
                self.browser.status.showMessage(f"Unbekannte chrome:// URL: {url.host()}", 3000)
                return False
            
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browsers = []
        self.dev_tools_windows = {}  # Speichere DevTools-Fenster
        
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
        
        # Developer Tools Button
        dev_tools_btn = QPushButton()
        dev_tools_btn.setIcon(qta.icon('fa5s.code', color='white'))
        dev_tools_btn.setToolTip("Developer Tools (F12)")
        dev_tools_btn.setObjectName("nav_button")
        dev_tools_btn.clicked.connect(self.openDevTools)
        nav_layout.addWidget(dev_tools_btn)
        
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
        
        # Erweiterte Webkompatibilität
        self.setupAdvancedWebCompatibility()
        
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
        
        # Verbessere JavaScript-Kompatibilität für alle Tabs
        self.setupJavaScriptPolyfills()
    
    def setupWebEngineProfile(self):
        # Erstelle ein globales Profil mit optimierten Einstellungen
        self.profile = QWebEngineProfile("vortex_profile")
        
        # Setze Cache-Größe auf 100 MB
        self.profile.setCachePath(os.path.join(os.path.expanduser("~"), ".vortex_cache"))
        self.profile.setPersistentStoragePath(os.path.join(os.path.expanduser("~"), ".vortex_storage"))
        self.profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        self.profile.setHttpCacheMaximumSize(200 * 1024 * 1024)  # Cache auf 200 MB erhöht
        
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
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, False)  # Modernere Websites erlauben
        
        # Verbesserte Unterstützung für Schriftarten
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        
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
        settings.setFontFamily(QWebEngineSettings.CursiveFont, "Comic Sans MS")
        settings.setFontFamily(QWebEngineSettings.FantasyFont, "Impact")
        
        # Standardgröße für Schriften
        settings.setFontSize(QWebEngineSettings.DefaultFontSize, 16)
        settings.setFontSize(QWebEngineSettings.DefaultFixedFontSize, 14)
        settings.setFontSize(QWebEngineSettings.MinimumFontSize, 10)
        settings.setFontSize(QWebEngineSettings.MinimumLogicalFontSize, 10)
        
        # HTML5-Funktionen aktivieren
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        
        # Moderne Premium-Funktionen aktivieren
        try:
            settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
            settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
            settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
            settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
            settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
            settings.setAttribute(QWebEngineSettings.PrintElementBackgrounds, True)
            settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        except:
            print("Einige moderne WebEngine-Einstellungen sind in dieser Qt-Version nicht verfügbar")
        
        # Hardware-Beschleunigung für bessere Performance
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu --enable-accelerated-2d-canvas --enable-accelerated-vpx-decode --ignore-gpu-blacklist --disable-features=UseOzonePlatform --enable-features=VaapiVideoDecoder"
    
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
        
        # Verbesserte CSS-Kompatibilität
        self.enhanceCssCompatibility(browser)
        
        # Verknüpfe das URL-Ändern mit unserer URL-Aktualisierung
        browser.urlChanged.connect(lambda qurl, browser=browser: self.updateUrlBar(qurl, browser))
        
        # Verknüpfe den Seitentitel mit unserem Tab-Titel
        browser.page().titleChanged.connect(self.updateTabTitle)
        
        # Verknüpfe das Laden mit der Statusleiste
        browser.loadStarted.connect(lambda: self.status.showMessage("Laden gestartet..."))
        browser.loadProgress.connect(lambda p: self.status.showMessage(f"Laden: {p}%"))
        browser.loadFinished.connect(lambda: self.status.showMessage("Laden abgeschlossen"))
        
        # Füge Kontext-Menü mit Developer Tools hinzu
        browser.setContextMenuPolicy(Qt.CustomContextMenu)
        browser.customContextMenuRequested.connect(lambda pos, b=browser: self.showContextMenu(pos, b))
        
        # Tastenkombination für Developer Tools (F12)
        dev_tools_shortcut = QAction("Developer Tools", self)
        dev_tools_shortcut.setShortcut("F12")
        dev_tools_shortcut.triggered.connect(self.openDevTools)
        browser.addAction(dev_tools_shortcut)
        
        # Tastenkombination für Neu laden (F5)
        reload_shortcut = QAction("Neu laden", self)
        reload_shortcut.setShortcut("F5")
        reload_shortcut.triggered.connect(self.reloadPage)
        browser.addAction(reload_shortcut)
        
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
            print(f"NavigateToUrl mit übergebener URL: {url.toString()}")
        else:
            # Hole die URL aus der URL-Leiste
            url_text = self.url_bar.text().strip()
            print(f"NavigateToUrl aus URL-Leiste: {url_text}")
            
            # Wenn die URL leer ist, nichts tun
            if not url_text:
                return
                
            # Direkte Unterstützung für vortex://-URLs
            if url_text.startswith("vortex://"):
                url = QUrl(url_text)
                print(f"Direkte vortex:// URL erkannt: {url_text}")
                if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
                    self.browsers[self.tabs.currentIndex()].setUrl(url)
                return
                
            # Direkte Unterstützung für chrome://-URLs
            if url_text.startswith("chrome://"):
                url = QUrl(url_text)
                print(f"Direkte chrome:// URL erkannt: {url_text}")
                if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
                    self.browsers[self.tabs.currentIndex()].setUrl(url)
                return
                
            # Prüfe, ob es sich um eine Suchanfrage oder eine URL handelt
            if (not url_text.startswith(('http://', 'https://', 'file://', 'vortex://', 'chrome://')) and 
                not '.' in url_text):
                # Es ist eine Suchanfrage, verwende die konfigurierte Suchmaschine
                self.performSearch(url_text)
                return
            else:
                # Es ist eine URL
                if not url_text.startswith(('http://', 'https://', 'file://', 'vortex://', 'chrome://')):
                    url_text = 'http://' + url_text
                url = QUrl(url_text)
        
        # Lade die URL in den aktuellen Browser
        if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            self.browsers[self.tabs.currentIndex()].setUrl(url)
    
    def performSearch(self, search_term):
        """Führt eine Suche mit dem angegebenen Suchbegriff durch"""
        if not search_term:
            return
        
        # Verwende die konfigurierte Suchmaschine
        engine = self.settings.get("search_engine", "Google")
        search_url = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["Google"])
        url = QUrl(search_url.replace("{query}", search_term))
        
        # Navigiere zur Suchergebnis-URL im aktuellen Tab
        if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            self.browsers[self.tabs.currentIndex()].setUrl(url)
            self.url_bar.setText(url.toString())
    
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

    def setupAdvancedWebCompatibility(self):
        """Erweiterte Kompatibilitätseinstellungen für problematische Websites"""
        
        # JavaScript-Flag setzen um spezifische Website-Erkennungsprobleme zu umgehen
        script_source = """
        // Website-Kompatibilität verbessern
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        // Verbesserte CSS-Unterstützung
        if (!window.CSS) {
            window.CSS = {};
        }
        
        // Feature-Detection verbessern
        if (!window.chrome) {
            window.chrome = {
                runtime: {},
                webstore: {},
                app: {}
            };
        }
        
        // Verbesserte Touch-Unterstützung
        if (!window.TouchEvent && !window.Touch) {
            window.Touch = class Touch {};
            window.TouchEvent = class TouchEvent {};
        }
        """
        
        # Dieses Skript wird auf jeder Seite ausgeführt
        script = QWebEngineScript()
        script.setSourceCode(script_source)
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(True)
        self.profile.scripts().insert(script)
        
        # Feature-Flags aktivieren für bessere Rendering-Kompatibilität
        flags = [
            "--enable-javascript-harmony",
            "--enable-features=NetworkServiceInProcess",
            "--disable-features=UseChromeOSDirectVideoDecoder",
            "--disable-web-security",  # Nur für bessere Kompatibilität, Vorsicht bei sicherheitskritischen Anwendungen
            "--autoplay-policy=no-user-gesture-required",
            "--disable-site-isolation-trials"
        ]
        
        # Bereits bestehende Flags beibehalten und neue hinzufügen
        existing_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = existing_flags + " " + " ".join(flags)

    def enhanceCssCompatibility(self, browser):
        """Verbessert die CSS-Kompatibilität für problematische Websites"""
        
        # CSS-Fehlertoleranz erhöhen
        settings = browser.settings()
        
        # Zusätzliche CSS-spezifische Einstellungen
        try:
            # Experimentelle Features aktivieren für bessere CSS-Unterstützung
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            
            # Einige Websites benötigen diese CSS-Features explizit aktiviert
            css_fixes = """
            /* Fix für einige flexbox und grid Probleme */
            @supports (display: flex) or (display: grid) {
                body {
                    display: block; /* Fallback */
                }
            }
            
            /* Fix für SVG-Rendering */
            svg {
                transform: translateZ(0);
            }
            """
            
            # Füge globales CSS zur Korrektur von Darstellungsproblemen hinzu
            fix_script = QWebEngineScript()
            fix_script.setSourceCode(f"(function() {{ var style = document.createElement('style'); style.textContent = `{css_fixes}`; document.head.appendChild(style); }})();")
            fix_script.setInjectionPoint(QWebEngineScript.DocumentReady)
            fix_script.setWorldId(QWebEngineScript.MainWorld)
            fix_script.setRunsOnSubFrames(True)
            self.profile.scripts().insert(fix_script)
            
        except Exception as e:
            print(f"Fehler bei der CSS-Kompatibilitätsverbesserung: {e}")

    def setupJavaScriptPolyfills(self):
        """Fügt JavaScript-Polyfills für bessere Kompatibilität hinzu"""
        
        # Umfassendere JavaScript-Polyfills für problematische Seiten
        js_polyfills = """
        // Promise-Polyfill für ältere Websites
        if (typeof Promise === 'undefined') {
            window.Promise = function(executor) {
                this.then = function(onFulfilled) { return this; };
                this.catch = function(onRejected) { return this; };
            };
            Promise.resolve = function(value) { return new Promise(); };
            Promise.reject = function(reason) { return new Promise(); };
            Promise.all = function(promises) { return new Promise(); };
        }
        
        // Fetch-API-Polyfill
        if (!window.fetch) {
            window.fetch = function() { 
                return Promise.resolve({ 
                    json: function() { return Promise.resolve({}); },
                    text: function() { return Promise.resolve(''); }
                });
            };
        }
        
        // DOM-Methoden-Polyfills
        if (!Element.prototype.closest) {
            Element.prototype.closest = function(s) {
                var el = this;
                do {
                    if (el.matches(s)) return el;
                    el = el.parentElement || el.parentNode;
                } while (el !== null && el.nodeType === 1);
                return null;
            };
        }
        
        // IntersectionObserver-Polyfill
        if (!window.IntersectionObserver) {
            window.IntersectionObserver = function() {
                return { observe: function() {}, unobserve: function() {}, disconnect: function() {} };
            };
        }
        """
        
        # Füge die Polyfills zu jedem Tab hinzu
        polyfill_script = QWebEngineScript()
        polyfill_script.setSourceCode(js_polyfills)
        polyfill_script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        polyfill_script.setWorldId(QWebEngineScript.MainWorld)
        polyfill_script.setRunsOnSubFrames(True)
        self.profile.scripts().insert(polyfill_script)

    def openDevTools(self):
        """Öffnet die nativen Chromium Developer Tools in einem separaten Fenster"""
        if hasattr(self, 'browsers') and self.tabs.currentIndex() >= 0 and self.tabs.currentIndex() < len(self.browsers):
            current_tab_index = self.tabs.currentIndex()
            current_browser = self.browsers[current_tab_index]
            
            # Prüfe, ob bereits DevTools für diesen Tab geöffnet sind
            if current_tab_index in self.dev_tools_windows and self.dev_tools_windows[current_tab_index].isVisible():
                # Bring das existierende DevTools-Fenster in den Vordergrund
                print(f"Existierende DevTools für Tab {current_tab_index} werden fokussiert")
                self.dev_tools_windows[current_tab_index].activateWindow()
                self.dev_tools_windows[current_tab_index].raise_()
                return
            
            # Erstelle ein neues Fenster für die DevTools
            print(f"Erstelle neue DevTools für Tab {current_tab_index}")
            dev_tools_window = QMainWindow()
            dev_tools_window.setWindowTitle(f"Developer Tools - {self.tabs.tabText(current_tab_index)}")
            dev_tools_window.setMinimumSize(800, 600)
            
            # Erstelle eine WebView für die DevTools
            dev_tools_view = QWebEngineView()
            dev_tools_window.setCentralWidget(dev_tools_view)
            
            # Verknüpfe die Haupt-Webseite mit den DevTools
            # Wichtig: setDevToolsPage muss vor dem Öffnen der DevTools aufgerufen werden
            current_browser.page().setDevToolsPage(dev_tools_view.page())
            
            # Führe den JavaScript-Befehl aus, um die DevTools zu öffnen
            current_browser.page().triggerAction(QWebEnginePage.InspectElement)
            
            # Verbinde das Schließen-Signal
            dev_tools_window.closeEvent = lambda event, tab_index=current_tab_index: self.onDevToolsClosed(event, tab_index)
            
            # Speichere das Fenster in der Liste
            self.dev_tools_windows[current_tab_index] = dev_tools_window
            
            # Zeige das Fenster
            dev_tools_window.show()
            self.status.showMessage("Developer Tools geöffnet", 3000)
        else:
            self.status.showMessage("Kein Browser-Tab gefunden", 3000)
    
    def onDevToolsClosed(self, event, tab_index):
        """Wird aufgerufen, wenn ein DevTools-Fenster geschlossen wird"""
        print(f"DevTools für Tab {tab_index} wurden geschlossen")
        if tab_index in self.dev_tools_windows:
            self.dev_tools_windows[tab_index] = None
        event.accept()

    def loadChromePage(self, page_type):
        """Lädt Chrome-ähnliche interne Seiten"""
        if not hasattr(self, 'browsers') or self.tabs.currentIndex() < 0 or self.tabs.currentIndex() >= len(self.browsers):
            return
            
        current_browser = self.browsers[self.tabs.currentIndex()]
        
        # HTML-Template für Chrome-Seiten
        chrome_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vortex {title}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #202124;
                    color: #e8eaed;
                    margin: 0;
                    padding: 40px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                
                .content-container {
                    width: 100%;
                    max-width: 800px;
                }
                
                h1 {
                    margin-bottom: 30px;
                    text-align: center;
                    color: #e8eaed;
                }
                
                .chrome-section {
                    background-color: #303134;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                
                .section-title {
                    font-size: 18px;
                    font-weight: 500;
                    margin-bottom: 15px;
                    color: #e8eaed;
                }
                
                .info-text {
                    font-size: 14px;
                    color: #9aa0a6;
                    line-height: 1.5;
                }
                
                .button {
                    background-color: #8ab4f8;
                    color: #202124;
                    border: none;
                    border-radius: 4px;
                    padding: 10px 20px;
                    font-size: 14px;
                    cursor: pointer;
                    margin-top: 20px;
                    transition: background-color 0.2s;
                    text-decoration: none;
                    display: inline-block;
                }
                
                .button:hover {
                    background-color: #aecbfa;
                }
                
                .item-list {
                    list-style: none;
                    padding: 0;
                }
                
                .item-list li {
                    padding: 10px 0;
                    border-bottom: 1px solid #5f6368;
                }
                
                .item-list li:last-child {
                    border-bottom: none;
                }
            </style>
        </head>
        <body>
            <div class="content-container">
                <h1>{title}</h1>
                
                {content}
            </div>
        </body>
        </html>
        """
        
        # Inhalte je nach Seitentyp generieren
        if page_type == "history":
            title = "Verlauf"
            content = """
            <div class="chrome-section">
                <div class="section-title">Verlauf</div>
                <div class="info-text">
                    Der Verlauf wird in Vortex aktuell nicht gespeichert.
                </div>
                <a href="vortex://new-tab" class="button">Zurück zur Startseite</a>
            </div>
            """
        elif page_type == "downloads":
            title = "Downloads"
            content = """
            <div class="chrome-section">
                <div class="section-title">Downloads</div>
                <div class="info-text">
                    Downloads werden in Vortex aktuell nicht verwaltet.
                </div>
                <a href="vortex://new-tab" class="button">Zurück zur Startseite</a>
            </div>
            """
        elif page_type == "extensions":
            title = "Erweiterungen"
            content = """
            <div class="chrome-section">
                <div class="section-title">Erweiterungen</div>
                <div class="info-text">
                    Vortex unterstützt aktuell keine Erweiterungen.
                </div>
                <a href="vortex://new-tab" class="button">Zurück zur Startseite</a>
            </div>
            """
        elif page_type == "version":
            title = "Version"
            content = f"""
            <div class="chrome-section">
                <div class="section-title">Vortex Browser</div>
                <div class="info-text">
                    Version: 1.1.0<br>
                    Based on: Chromium/QtWebEngine {MODERN_USER_AGENT.split('Chrome/')[1].split(' ')[0]}<br>
                    User-Agent: {MODERN_USER_AGENT} Vortex/1.1.0<br>
                    Platform: {sys.platform}<br>
                    Python: {sys.version}<br>
                    Qt: {QWebEngineProfile.defaultProfile().httpUserAgent()}<br>
                </div>
                <a href="vortex://new-tab" class="button">Zurück zur Startseite</a>
            </div>
            """
        else:
            title = "Nicht verfügbar"
            content = """
            <div class="chrome-section">
                <div class="section-title">Diese Seite ist nicht verfügbar</div>
                <div class="info-text">
                    Die angeforderte Chrome-Funktion wird in Vortex nicht unterstützt.
                </div>
                <a href="vortex://new-tab" class="button">Zurück zur Startseite</a>
            </div>
            """
        
        # Fülle das Template
        html = chrome_html.format(title=title, content=content)
        
        # Lade die Seite
        current_browser.setHtml(html, QUrl(f"chrome://{page_type}"))
        
        # Aktualisiere die URL-Bar
        self.url_bar.setText(f"chrome://{page_type}")
        
        # Aktualisiere den Tab-Titel
        self.tabs.setTabText(self.tabs.currentIndex(), title)
            
    def showContextMenu(self, pos, browser):
        """Zeigt ein Kontextmenü mit zusätzlichen Funktionen an"""
        menu = QMenu()
        
        # Standard-Aktionen hinzufügen
        back_action = menu.addAction("Zurück")
        back_action.triggered.connect(self.navigateBack)
        
        forward_action = menu.addAction("Vorwärts")
        forward_action.triggered.connect(self.navigateForward)
        
        reload_action = menu.addAction("Neu laden")
        reload_action.triggered.connect(self.reloadPage)
        
        menu.addSeparator()
        
        # Entwickler-Optionen
        inspect_action = menu.addAction("Element untersuchen")
        inspect_action.triggered.connect(lambda: self.inspectElement(browser, pos))
        
        dev_tools_action = menu.addAction("Developer Tools (F12)")
        dev_tools_action.triggered.connect(self.openDevTools)
        
        view_source_action = menu.addAction("Seitenquelltext anzeigen")
        view_source_action.triggered.connect(lambda: self.viewPageSource(browser))
        
        menu.addSeparator()
        
        # Chrome-spezifische Optionen
        chrome_menu = menu.addMenu("Chrome-Seiten")
        
        settings_action = chrome_menu.addAction("Einstellungen")
        settings_action.triggered.connect(lambda: self.navigateToUrl(QUrl("chrome://settings")))
        
        history_action = chrome_menu.addAction("Verlauf")
        history_action.triggered.connect(lambda: self.navigateToUrl(QUrl("chrome://history")))
        
        downloads_action = chrome_menu.addAction("Downloads")
        downloads_action.triggered.connect(lambda: self.navigateToUrl(QUrl("chrome://downloads")))
        
        extensions_action = chrome_menu.addAction("Erweiterungen")
        extensions_action.triggered.connect(lambda: self.navigateToUrl(QUrl("chrome://extensions")))
        
        version_action = chrome_menu.addAction("Version")
        version_action.triggered.connect(lambda: self.navigateToUrl(QUrl("chrome://version")))
        
        # Zeige das Menü an der Position des Mauszeigers
        menu.exec_(browser.mapToGlobal(pos))
    
    def inspectElement(self, browser, pos):
        """Element an der angegebenen Position untersuchen"""
        print(f"Inspektor für Element an Position {pos} wird aufgerufen")
        # Element an der aktuellen Position auswählen
        # Dies muss vor dem Öffnen der DevTools geschehen
        browser.page().runJavaScript("""
            (function() {
                // Erstelle ein temporäres Ereignis, um die Position zu markieren
                var element = document.elementFromPoint(%d, %d);
                if (element) {
                    // Element markieren
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    
                    // Für temporäre visuelle Hervorhebung
                    var oldBorder = element.style.border;
                    var oldBackground = element.style.background;
                    
                    element.style.border = '2px solid #8ab4f8';
                    element.style.background = 'rgba(138, 180, 248, 0.2)';
                    
                    // Alten Stil nach kurzer Zeit wiederherstellen
                    setTimeout(function() {
                        element.style.border = oldBorder;
                        element.style.background = oldBackground;
                    }, 1500);
                    
                    return 'Element ausgewählt: ' + element.tagName;
                }
                return 'Kein Element an dieser Position gefunden';
            })();
        """ % (pos.x(), pos.y()), self.handleInspectorCallback)
        
        # Öffne die DevTools und fokussiere auf das Element
        self.openDevTools()
    
    def handleInspectorCallback(self, result):
        """Callback für die JavaScript-Element-Auswahl"""
        print(f"Element-Auswahl Ergebnis: {result}")
        self.status.showMessage(result, 2000)
    
    def viewPageSource(self, browser):
        """Zeigt den Quelltext der aktuellen Seite in einem formatierten Tab an"""
        # Hole die aktuelle URL und den Quelltext
        current_url = browser.url().toString()
        print(f"Zeige Quelltext für {current_url}")
        
        # Erzeuge ein JavaScript, das den Seitenquelltext abruft
        browser.page().runJavaScript("""
            (function() {
                return document.documentElement.outerHTML;
            })();
        """, self.handleSourceViewCallback)
        
    def handleSourceViewCallback(self, html_source):
        """Callback für die Quelltextanzeige"""
        if not html_source:
            self.status.showMessage("Quelltext konnte nicht abgerufen werden", 3000)
            return
            
        # Erstelle einen neuen Tab für den Quelltext
        tab_index, view = self.addTab()
        
        # Formatiere den Quelltext mit Syntax-Highlighting
        formatted_source = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Quelltext</title>
            <meta charset="UTF-8">
            <style>
                body {{
                    background-color: #202124;
                    color: #e8eaed;
                    font-family: 'Courier New', monospace;
                    padding: 20px;
                    line-height: 1.5;
                    margin: 0;
                }}
                .line-numbers {{
                    border-right: 1px solid #5f6368;
                    background-color: #161718;
                    text-align: right;
                    padding: 0 10px;
                    margin-right: 10px;
                    user-select: none;
                    min-width: 3em;
                    display: inline-block;
                    color: #9aa0a6;
                }}
                pre {{
                    margin: 0;
                    white-space: pre-wrap;
                    max-width: 100%;
                    overflow-x: auto;
                }}
                .html-tag {{
                    color: #5db0d7;
                }}
                .html-attribute {{
                    color: #9bddfb;
                }}
                .html-attribute-value {{
                    color: #f9c859;
                }}
                .html-comment {{
                    color: #6c7986;
                    font-style: italic;
                }}
                .html-text {{
                    color: #e8eaed;
                }}
                .toolbar {{
                    background-color: #35363a;
                    padding: 10px;
                    margin-bottom: 15px;
                    position: sticky;
                    top: 0;
                    display: flex;
                    justify-content: space-between;
                    border-bottom: 1px solid #5f6368;
                }}
                .search-box {{
                    background-color: #202124;
                    border: 1px solid #5f6368;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    min-width: 200px;
                }}
                .button {{
                    background-color: #3c4043;
                    border: none;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-left: 5px;
                }}
                .button:hover {{
                    background-color: #5f6368;
                }}
                .content {{
                    display: flex;
                }}
                .highlight {{
                    background-color: rgba(255, 215, 0, 0.2);
                }}
            </style>
            <script>
                // Einfache Suchfunktion
                function searchText() {{
                    // Entferne vorherige Hervorhebungen
                    let highlighted = document.querySelectorAll('.highlight');
                    highlighted.forEach(elem => {{
                        elem.classList.remove('highlight');
                    }});
                    
                    // Hole den Suchtext
                    const searchText = document.getElementById('search-input').value.toLowerCase();
                    if (!searchText) return;
                    
                    // Suche im Quelltext
                    const codeLines = document.querySelectorAll('.html-line');
                    let matchCount = 0;
                    let firstMatch = null;
                    
                    codeLines.forEach(line => {{
                        const text = line.textContent.toLowerCase();
                        if (text.includes(searchText)) {{
                            line.classList.add('highlight');
                            matchCount++;
                            if (!firstMatch) firstMatch = line;
                        }}
                    }});
                    
                    // Scrolle zur ersten Übereinstimmung
                    if (firstMatch) {{
                        firstMatch.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                    
                    // Zeige Ergebnis an
                    document.getElementById('search-results').textContent = 
                        matchCount ? `${{matchCount}} Übereinstimmungen gefunden` : 'Keine Übereinstimmungen';
                }}
                
                // Bei Tastendruck im Suchfeld suchen
                function handleSearchKeyPress(event) {{
                    if (event.key === 'Enter') {{
                        searchText();
                    }}
                }}
                
                // Syntax-Highlighting formatieren
                window.onload = function() {{
                    const codeContent = document.getElementById('code-content');
                    if (!codeContent) return;
                    
                    let html = codeContent.innerHTML;
                    
                    // HTML-Syntax hervorheben
                    html = html.replace(/&lt;!--(.+?)--&gt;/g, '&lt;!--<span class="html-comment">$1</span>--&gt;');
                    html = html.replace(/&lt;(\\/?)([\\w-]+)(.*?)(\\/?)&gt;/g, function(match, endSlash, tag, attrs, selfClose) {{
                        let formattedAttrs = attrs.replace(/\\s([\\w-]+)="([^"]*)"/g, ' <span class="html-attribute">$1</span>=<span class="html-attribute-value">"$2"</span>');
                        return '&lt;' + endSlash + '<span class="html-tag">' + tag + '</span>' + formattedAttrs + selfClose + '&gt;';
                    }});
                    
                    codeContent.innerHTML = html;
                }};
            </script>
        </head>
        <body>
            <div class="toolbar">
                <div>
                    <input type="text" id="search-input" class="search-box" placeholder="Im Quelltext suchen..." onkeypress="handleSearchKeyPress(event)">
                    <button class="button" onclick="searchText()">Suchen</button>
                    <span id="search-results"></span>
                </div>
                <button class="button" onclick="window.print()">Drucken</button>
            </div>
            
            <div class="content">
                <pre id="code-content">{html_source.replace('<', '&lt;').replace('>', '&gt;')}</pre>
            </div>
            
            <script>
                // Zeilennummern hinzufügen
                window.onload = function() {{
                    const codeContent = document.getElementById('code-content');
                    const lines = codeContent.innerHTML.split('\\n');
                    let numberedLines = '';
                    
                    for (let i = 0; i < lines.length; i++) {{
                        numberedLines += `<div class="html-line"><span class="line-numbers">${{i+1}}</span>${{lines[i]}}</div>`;
                    }}
                    
                    codeContent.innerHTML = numberedLines;
                    
                    // Syntax-Highlighting formatieren
                    const codeLines = document.querySelectorAll('.html-line');
                    codeLines.forEach(line => {{
                        // HTML-Syntax hervorheben
                        let html = line.innerHTML;
                        // HTML-Tags hervorheben - aber nicht in den line-numbers
                        const content = line.innerHTML.split('</span>')[1];
                        if (content) {{
                            let formattedContent = content
                                // Kommentare
                                .replace(/(&lt;!--)(.*?)(--&gt;)/g, '<span class="html-comment">$1$2$3</span>')
                                // Tags
                                .replace(/(&lt;\\/?)([\\w-]+)(.*?)(\\/?)(&gt;)/g, function(match, startBracket, tag, attrs, selfClose, endBracket) {{
                                    let formattedAttrs = attrs.replace(/(\\s)([\\w-]+)(=)(".*?")/g, '$1<span class="html-attribute">$2</span>$3<span class="html-attribute-value">$4</span>');
                                    return startBracket + '<span class="html-tag">' + tag + '</span>' + formattedAttrs + selfClose + endBracket;
                                }});
                            
                            line.innerHTML = line.innerHTML.split('</span>')[0] + '</span>' + formattedContent;
                        }}
                    }});
                }};
            </script>
        </body>
        </html>
        """
        
        # Zeige den formatierten Quelltext im neuen Tab
        self.browsers[tab_index].setHtml(formatted_source, QUrl("vortex://source"))
        self.tabs.setTabText(tab_index, "Quelltext")
        self.status.showMessage("Quelltext angezeigt", 3000)

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