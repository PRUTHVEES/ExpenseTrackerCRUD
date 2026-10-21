import functools
import http.server
import socket
import threading
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def root_dir():
    return ROOT_DIR


@pytest.fixture(scope="session")
def html_path(root_dir):
    return root_dir / "index.html"


@pytest.fixture(scope="session")
def html_content(html_path):
    return html_path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def soup(html_content):
    return BeautifulSoup(html_content, "html.parser")


@pytest.fixture(scope="session")
def app_js_content(root_dir):
    return (root_dir / "app.js").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def http_server(root_dir):
    """Starts a local HTTP server serving the workspace directory."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root_dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    server.shutdown()
    server.server_close()


@pytest.fixture(scope="session")
def chrome_driver():
    """Session-scoped headless Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(4)
    yield driver
    driver.quit()


@pytest.fixture
def page(chrome_driver, http_server):
    """Provides a freshly loaded page with a clean demo state."""
    chrome_driver.get(f"{http_server}/index.html")
    chrome_driver.execute_script("localStorage.clear();")
    chrome_driver.refresh()
    return chrome_driver


@pytest.fixture
def sample_transactions():
    """Sample dataset for calculation and logic tests."""
    return [
        {
            "id": "tx-101",
            "title": "Client Retainer",
            "amount": 2500.0,
            "type": "income",
            "category": "freelance",
            "date": "2026-10-01",
            "note": "Design system project"
        },
        {
            "id": "tx-102",
            "title": "Desk Setup",
            "amount": 350.0,
            "type": "expense",
            "category": "shopping",
            "date": "2026-10-05",
            "note": "Ergonomic chair"
        },
        {
            "id": "tx-103",
            "title": "Internet Fiber",
            "amount": 75.0,
            "type": "expense",
            "category": "utilities",
            "date": "2026-10-10",
            "note": "Monthly broadband"
        },
        {
            "id": "tx-104",
            "title": "Grocery Run",
            "amount": 125.50,
            "type": "expense",
            "category": "food",
            "date": "2026-10-12",
            "note": "Weekly groceries"
        }
    ]
