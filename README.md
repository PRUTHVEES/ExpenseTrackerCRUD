# 💳 Smart Expense Tracker (CRUD Application)

A modern, responsive, and lightweight **CRUD Expense Tracker** application built with vanilla **HTML5**, **CSS3**, and **JavaScript (ES6+)**. No build tools or external frameworks required—just open and use!

---

## 🌟 Features

### 1. Full CRUD Operations
- **Create**: Add transactions (expenses or income) with title, amount, date, category, and optional notes.
- **Read**: View transactions with visual badges, category icons, timestamps, and real-time balance calculations.
- **Update**: Edit any existing transaction with pre-filled inputs and instant state updates.
- **Delete**: Remove individual transactions with a confirmation dialog or clear all transactions at once.

### 2. Summary Dashboard & Real-Time Stats
- **Total Balance**: Live net savings indicator with status pill (Surplus, Balanced, Deficit).
- **Total Income**: Sum of all incoming funds.
- **Total Expenses**: Sum of all outgoing expenditures.
- **Savings Rate**: Percentage of income saved.

### 3. Visual Expense Breakdown
- Interactive spending progress bars by category with percentage distribution and custom category colors.

### 4. Search, Filter & Sort
- **Search**: Real-time search across description, category, and notes.
- **Filter**: Filter by type (`All`, `Expenses Only`, `Income Only`) and by category.
- **Sort**: Sort by date (newest/oldest) and amount (highest/lowest).

### 5. Customization & Persistence
- **Local Storage**: Automatically saves all your transactions, currency selection, and theme preferences across browser refreshes.
- **Multi-Currency Support**: Choose between `$ (USD)`, `₹ (INR)`, `€ (EUR)`, `£ (GBP)`, and `¥ (JPY)`.
- **Dark / Light Theme**: Smooth toggle between dark and light themes.
- **Data Export**: Export your complete transaction history to a structured `.json` backup file.
- **Demo Data Loader**: Pre-loaded with demo transactions for quick exploration.

---

## 📁 File Structure

```
expense-tracker/
├── index.html              # Semantic HTML5 layout and modal structure
├── style.css               # Modern responsive styling, CSS variables & dark/light theme
├── app.js                  # Complete CRUD logic, state management, and DOM handlers
├── Dockerfile              # Multi-stage Docker container build (test + production nginx)
├── docker-compose.yml      # Compose configuration for local container deployment
├── nginx.conf              # Optimized Nginx config (gzip, security headers, caching)
├── .dockerignore           # Docker build exclusions
├── requirements.txt        # Python test dependencies (pytest, selenium, beautifulsoup4)
├── pytest.ini              # Pytest configuration and test markers
├── tests/
│   ├── conftest.py         # Test fixtures (HTTP server, headless browser, sample data)
│   ├── test_logic.py       # Unit tests for calculations, filtering, sorting, validation
│   ├── test_dom_contract.py# HTML contract & accessibility test suite
│   └── test_e2e.py         # End-to-end browser automation tests (headless Chrome)
└── README.md               # Documentation and usage guide
```

---

## 🧪 Testing with Pytest

The project includes an automated test suite with **117 tests** across three layers:
1. **Unit Tests (`test_logic.py`)**: Tests financial mathematics, balance calculation, savings rate formulas, expense breakdown percentages, multi-criteria filtering, multi-order sorting, input validations, and XSS sanitization.
2. **DOM Contract Tests (`test_dom_contract.py`)**: Verifies that `index.html` implements all IDs, form constraints, modal attributes, and accessibility roles (`aria-*`) required by `app.js`.
3. **End-to-End Browser Tests (`test_e2e.py`)**: Automates user workflows in headless Chrome using Selenium (adding/editing/deleting transactions, live search, currency switching, theme toggle, demo resets, and `localStorage` persistence).

### Install Test Dependencies
```bash
python -m pip install -r requirements.txt
```

### Run All Tests
```bash
python -m pytest
```

### Run Specific Test Suites
```bash
# Run unit logic tests only
python -m pytest tests/test_logic.py

# Run DOM contract and accessibility tests
python -m pytest tests/test_dom_contract.py

# Run End-to-End browser tests
python -m pytest tests/test_e2e.py
```

### Run by Marker
```bash
python -m pytest -m unit
python -m pytest -m dom
python -m pytest -m e2e
```

---

## 🐳 Docker Setup

### Option 1: Run with Docker Compose (Recommended)
```bash
docker compose up -d
```
Then visit **`http://localhost:8080`** in your browser.

To stop the container:
```bash
docker compose down
```

### Option 2: Build & Run with Docker CLI
```bash
# Build the production image
docker build -t expense-tracker .

# Run container on port 8080
docker run -d -p 8080:80 --name expense-tracker expense-tracker
```

### Option 3: Run Automated Tests Inside Docker
```bash
# Builds and executes the test stage in Docker
docker build --target test -t expense-tracker:test .
```

---

## 🚀 How to Run Locally Without Docker

1. Navigate to the `expense-tracker` folder on your computer.
2. Double-click **`index.html`** to open it directly in any modern web browser (Chrome, Edge, Firefox, Safari).
3. *(Alternative)* If you use VS Code, right-click `index.html` and click **"Open with Live Server"**, or run a simple local server:
   ```bash
   # Python 3
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser.
"# ExpenseTrackerCRUD" 
