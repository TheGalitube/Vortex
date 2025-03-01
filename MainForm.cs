using Microsoft.Web.WebView2.Core;

namespace VortexBrowser;

public partial class MainForm : Form
{
    private TextBox urlBar;
    private Microsoft.Web.WebView2.WinForms.WebView2 webView;
    private Button goButton;
    private Button backButton;
    private Button forwardButton;
    private Button refreshButton;

    public MainForm()
    {
        InitializeComponent();
        InitializeBrowser();
    }

    private void InitializeComponent()
    {
        this.Text = "Vortex Browser";
        this.Size = new Size(1200, 800);

        // Toolbar erstellen
        var toolStrip = new ToolStrip();
        
        backButton = new Button { Text = "←", Width = 40 };
        backButton.Click += (s, e) => webView.GoBack();
        
        forwardButton = new Button { Text = "→", Width = 40 };
        forwardButton.Click += (s, e) => webView.GoForward();
        
        refreshButton = new Button { Text = "↻", Width = 40 };
        refreshButton.Click += (s, e) => webView.Reload();

        urlBar = new TextBox { Dock = DockStyle.Fill };
        urlBar.KeyPress += (s, e) => {
            if (e.KeyChar == (char)Keys.Enter)
            {
                NavigateToUrl();
                e.Handled = true;
            }
        };

        goButton = new Button { Text = "Go", Width = 40 };
        goButton.Click += (s, e) => NavigateToUrl();

        var toolPanel = new Panel { Height = 30, Dock = DockStyle.Top };
        backButton.Dock = DockStyle.Left;
        forwardButton.Dock = DockStyle.Left;
        refreshButton.Dock = DockStyle.Left;
        goButton.Dock = DockStyle.Right;
        
        toolPanel.Controls.AddRange(new Control[] { 
            backButton, forwardButton, refreshButton, urlBar, goButton 
        });

        this.Controls.Add(toolPanel);
    }

    private async void InitializeBrowser()
    {
        webView = new Microsoft.Web.WebView2.WinForms.WebView2();
        webView.Dock = DockStyle.Fill;
        
        this.Controls.Add(webView);
        await webView.EnsureCoreWebView2Async();

        webView.NavigationCompleted += (s, e) => {
            urlBar.Text = webView.Source.ToString();
            UpdateNavigationButtons();
        };

        webView.Source = new Uri("https://www.google.com");
    }

    private void NavigateToUrl()
    {
        var url = urlBar.Text;
        if (!url.StartsWith("http://") && !url.StartsWith("https://"))
        {
            url = "https://" + url;
        }
        webView.Source = new Uri(url);
    }

    private void UpdateNavigationButtons()
    {
        backButton.Enabled = webView.CanGoBack;
        forwardButton.Enabled = webView.CanGoForward;
    }
} 