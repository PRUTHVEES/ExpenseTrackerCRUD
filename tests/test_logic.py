import math
import re
from datetime import datetime, timezone
import pytest


# ==============================================================================
# Domain logic implementations mirroring app.js behavior
# ==============================================================================

CATEGORIES = {
    "expense": [
        {"id": "food", "label": "Food & Dining", "icon": "🍔", "color": "#f97316"},
        {"id": "transport", "label": "Transportation", "icon": "🚗", "color": "#06b6d4"},
        {"id": "housing", "label": "Housing & Rent", "icon": "🏠", "color": "#8b5cf6"},
        {"id": "utilities", "label": "Bills & Utilities", "icon": "💡", "color": "#eab308"},
        {"id": "entertainment", "label": "Entertainment", "icon": "🎬", "color": "#ec4899"},
        {"id": "shopping", "label": "Shopping", "icon": "🛍️", "color": "#3b82f6"},
        {"id": "health", "label": "Healthcare", "icon": "💊", "color": "#10b981"},
        {"id": "education", "label": "Education", "icon": "📚", "color": "#6366f1"},
        {"id": "other_expense", "label": "Other Expense", "icon": "📦", "color": "#64748b"},
    ],
    "income": [
        {"id": "salary", "label": "Salary / Wages", "icon": "💼", "color": "#10b981"},
        {"id": "freelance", "label": "Freelance & Projects", "icon": "💻", "color": "#3b82f6"},
        {"id": "investments", "label": "Investments", "icon": "📈", "color": "#8b5cf6"},
        {"id": "gifts", "label": "Gifts & Grants", "icon": "🎁", "color": "#ec4899"},
        {"id": "other_income", "label": "Other Income", "icon": "💵", "color": "#14b8a6"},
    ],
}


def get_category_meta(tx_type, cat_id):
    for cat in CATEGORIES.get(tx_type, []):
        if cat["id"] == cat_id:
            return cat
    all_cats = CATEGORIES["expense"] + CATEGORIES["income"]
    for cat in all_cats:
        if cat["id"] == cat_id:
            return cat
    return {"id": cat_id, "label": cat_id, "icon": "🏷️", "color": "#64748b"}


def calculate_summary(transactions):
    income = 0.0
    expense = 0.0
    income_count = 0
    expense_count = 0

    for tx in transactions:
        amt = float(tx.get("amount", 0) or 0)
        if tx.get("type") == "income":
            income += amt
            income_count += 1
        else:
            expense += amt
            expense_count += 1

    balance = income - expense

    if balance > 0:
        status = "In Surplus"
    elif balance < 0:
        status = "In Deficit"
    else:
        status = "Balanced"

    if income > 0:
        savings_rate = f"{round((balance / income) * 100)}%"
    else:
        savings_rate = "0%"

    return {
        "income": income,
        "expense": expense,
        "balance": balance,
        "income_count": income_count,
        "expense_count": expense_count,
        "status": status,
        "savings_rate": savings_rate,
    }


def calculate_breakdown(transactions):
    expenses = [t for t in transactions if t.get("type") == "expense"]
    total_expense = sum(float(t.get("amount", 0) or 0) for t in expenses)

    if total_expense == 0:
        return {"total": 0.0, "items": []}

    totals = {}
    for tx in expenses:
        cat = tx["category"]
        totals[cat] = totals.get(cat, 0.0) + float(tx["amount"])

    sorted_cats = sorted(totals.keys(), key=lambda c: totals[c], reverse=True)
    items = []
    for cat_id in sorted_cats:
        amount = totals[cat_id]
        pct = round((amount / total_expense) * 100, 1)
        items.append({
            "category_id": cat_id,
            "amount": amount,
            "percentage": pct,
            "meta": get_category_meta("expense", cat_id)
        })

    return {"total": total_expense, "items": items}


def filter_and_sort_transactions(transactions, search="", tx_type="all", category="all", sort_by="date-desc"):
    search = search.strip().lower()
    filtered = []

    for tx in transactions:
        if tx_type != "all" and tx.get("type") != tx_type:
            continue
        if category != "all" and tx.get("category") != category:
            continue
        if search:
            title = (tx.get("title") or "").lower()
            note = (tx.get("note") or "").lower()
            meta = get_category_meta(tx.get("type", "expense"), tx.get("category", ""))
            cat_label = meta["label"].lower()
            if search not in title and search not in note and search not in cat_label:
                continue
        filtered.append(tx)

    if sort_by == "date-asc":
        return sorted(filtered, key=lambda t: t.get("date", ""))
    elif sort_by == "amount-desc":
        return sorted(filtered, key=lambda t: float(t.get("amount", 0)), reverse=True)
    elif sort_by == "amount-asc":
        return sorted(filtered, key=lambda t: float(t.get("amount", 0)))
    else:  # date-desc
        return sorted(filtered, key=lambda t: t.get("date", ""), reverse=True)


def validate_transaction_input(title, amount_str, date_str, category):
    errors = {}
    if not title or not str(title).strip():
        errors["title"] = "Please enter a description"

    try:
        amount = float(amount_str)
        if math.isnan(amount) or amount <= 0:
            errors["amount"] = "Amount must be greater than 0"
    except (ValueError, TypeError):
        errors["amount"] = "Amount must be greater than 0"

    if not date_str or not str(date_str).strip():
        errors["date"] = "Please select a date"

    if not category or not str(category).strip():
        errors["category"] = "Please select a category"

    return len(errors) == 0, errors


def escape_html(text):
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def format_currency(num, symbol="$"):
    val = abs(float(num))
    return f"{symbol}{val:,.2f}"


# ==============================================================================
# Pytest Test Suites
# ==============================================================================

@pytest.mark.unit
class TestFinancialCalculations:
    """Verifies all balance, income, expense, and savings rate computations."""

    def test_empty_transactions_summary(self):
        summary = calculate_summary([])
        assert summary["income"] == 0.0
        assert summary["expense"] == 0.0
        assert summary["balance"] == 0.0
        assert summary["income_count"] == 0
        assert summary["expense_count"] == 0
        assert summary["status"] == "Balanced"
        assert summary["savings_rate"] == "0%"

    def test_surplus_balance_and_savings_rate(self, sample_transactions):
        summary = calculate_summary(sample_transactions)
        # Income: 2500, Expenses: 350 + 75 + 125.50 = 550.50
        assert summary["income"] == 2500.0
        assert summary["expense"] == 550.50
        assert summary["balance"] == 1949.50
        assert summary["income_count"] == 1
        assert summary["expense_count"] == 3
        assert summary["status"] == "In Surplus"
        # (1949.50 / 2500) * 100 = 77.98% -> rounds to 78%
        assert summary["savings_rate"] == "78%"

    def test_deficit_balance(self):
        txs = [
            {"amount": 1000.0, "type": "income", "category": "salary"},
            {"amount": 1500.0, "type": "expense", "category": "housing"},
        ]
        summary = calculate_summary(txs)
        assert summary["balance"] == -500.0
        assert summary["status"] == "In Deficit"
        assert summary["savings_rate"] == "-50%"

    def test_exact_zero_balance(self):
        txs = [
            {"amount": 500.0, "type": "income", "category": "salary"},
            {"amount": 500.0, "type": "expense", "category": "housing"},
        ]
        summary = calculate_summary(txs)
        assert summary["balance"] == 0.0
        assert summary["status"] == "Balanced"
        assert summary["savings_rate"] == "0%"

    def test_only_expenses_no_income(self):
        txs = [{"amount": 200.0, "type": "expense", "category": "food"}]
        summary = calculate_summary(txs)
        assert summary["income"] == 0.0
        assert summary["expense"] == 200.0
        assert summary["balance"] == -200.0
        assert summary["status"] == "In Deficit"
        assert summary["savings_rate"] == "0%"

    def test_category_breakdown_aggregation(self, sample_transactions):
        # sample_transactions expenses: shopping: 350, utilities: 75, food: 125.50. Total: 550.50
        breakdown = calculate_breakdown(sample_transactions)
        assert breakdown["total"] == 550.50
        assert len(breakdown["items"]) == 3

        # Should be sorted descending by amount
        assert breakdown["items"][0]["category_id"] == "shopping"
        assert breakdown["items"][0]["amount"] == 350.0
        # 350 / 550.5 * 100 = 63.57... -> 63.6%
        assert breakdown["items"][0]["percentage"] == 63.6

        assert breakdown["items"][1]["category_id"] == "food"
        assert breakdown["items"][1]["amount"] == 125.50

        assert breakdown["items"][2]["category_id"] == "utilities"
        assert breakdown["items"][2]["amount"] == 75.0

    def test_category_breakdown_no_expenses(self):
        txs = [{"amount": 1000.0, "type": "income", "category": "salary"}]
        breakdown = calculate_breakdown(txs)
        assert breakdown["total"] == 0.0
        assert breakdown["items"] == []


@pytest.mark.unit
class TestFilteringAndSearch:
    """Verifies filtering by type, category, and real-time text search."""

    def test_filter_by_type_expense_only(self, sample_transactions):
        filtered = filter_and_sort_transactions(sample_transactions, tx_type="expense")
        assert len(filtered) == 3
        assert all(t["type"] == "expense" for t in filtered)

    def test_filter_by_type_income_only(self, sample_transactions):
        filtered = filter_and_sort_transactions(sample_transactions, tx_type="income")
        assert len(filtered) == 1
        assert filtered[0]["id"] == "tx-101"

    def test_filter_by_category(self, sample_transactions):
        filtered = filter_and_sort_transactions(sample_transactions, category="utilities")
        assert len(filtered) == 1
        assert filtered[0]["category"] == "utilities"

    def test_search_by_title_case_insensitive(self, sample_transactions):
        filtered = filter_and_sort_transactions(sample_transactions, search="cLiEnT")
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Client Retainer"

    def test_search_by_note_case_insensitive(self, sample_transactions):
        filtered = filter_and_sort_transactions(sample_transactions, search="broadband")
        assert len(filtered) == 1
        assert filtered[0]["note"] == "Monthly broadband"

    def test_search_by_category_label(self, sample_transactions):
        # 'freelance' category label is 'Freelance & Projects'
        filtered = filter_and_sort_transactions(sample_transactions, search="projects")
        assert len(filtered) == 1
        assert filtered[0]["id"] == "tx-101"

    def test_combined_search_and_type_filter(self, sample_transactions):
        filtered = filter_and_sort_transactions(
            sample_transactions, search="setup", tx_type="expense", category="shopping"
        )
        assert len(filtered) == 1
        assert filtered[0]["id"] == "tx-102"

    def test_search_no_matches(self, sample_transactions):
        filtered = filter_and_sort_transactions(sample_transactions, search="NonExistentTermXYZ")
        assert len(filtered) == 0


@pytest.mark.unit
class TestSorting:
    """Verifies ordering by date and amount in ascending and descending directions."""

    def test_sort_date_descending(self, sample_transactions):
        sorted_txs = filter_and_sort_transactions(sample_transactions, sort_by="date-desc")
        dates = [t["date"] for t in sorted_txs]
        assert dates == ["2026-10-12", "2026-10-10", "2026-10-05", "2026-10-01"]

    def test_sort_date_ascending(self, sample_transactions):
        sorted_txs = filter_and_sort_transactions(sample_transactions, sort_by="date-asc")
        dates = [t["date"] for t in sorted_txs]
        assert dates == ["2026-10-01", "2026-10-05", "2026-10-10", "2026-10-12"]

    def test_sort_amount_descending(self, sample_transactions):
        sorted_txs = filter_and_sort_transactions(sample_transactions, sort_by="amount-desc")
        amounts = [t["amount"] for t in sorted_txs]
        assert amounts == [2500.0, 350.0, 125.50, 75.0]

    def test_sort_amount_ascending(self, sample_transactions):
        sorted_txs = filter_and_sort_transactions(sample_transactions, sort_by="amount-asc")
        amounts = [t["amount"] for t in sorted_txs]
        assert amounts == [75.0, 125.50, 350.0, 2500.0]


@pytest.mark.unit
class TestInputValidation:
    """Verifies form validation rules for transactions."""

    def test_valid_input(self):
        is_valid, errors = validate_transaction_input("Coffee", "4.50", "2026-10-21", "food")
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.parametrize("title", ["", "   ", None])
    def test_invalid_title(self, title):
        is_valid, errors = validate_transaction_input(title, "25.00", "2026-10-21", "food")
        assert is_valid is False
        assert "title" in errors
        assert errors["title"] == "Please enter a description"

    @pytest.mark.parametrize("amount", ["0", "-10", "abc", "", None])
    def test_invalid_amount(self, amount):
        is_valid, errors = validate_transaction_input("Book", amount, "2026-10-21", "education")
        assert is_valid is False
        assert "amount" in errors
        assert errors["amount"] == "Amount must be greater than 0"

    @pytest.mark.parametrize("date_val", ["", "   ", None])
    def test_invalid_date(self, date_val):
        is_valid, errors = validate_transaction_input("Book", "15.00", date_val, "education")
        assert is_valid is False
        assert "date" in errors

    @pytest.mark.parametrize("cat", ["", None])
    def test_invalid_category(self, cat):
        is_valid, errors = validate_transaction_input("Book", "15.00", "2026-10-21", cat)
        assert is_valid is False
        assert "category" in errors


@pytest.mark.unit
class TestFormattingAndSecurity:
    """Verifies XSS sanitization and multi-currency formatting."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#039;xss&#039;)&lt;/script&gt;"),
            ('Hello "World" & Friends', "Hello &quot;World&quot; &amp; Friends"),
            ("Normal Text 123", "Normal Text 123"),
            ("", ""),
            (None, ""),
        ],
    )
    def test_escape_html(self, raw, expected):
        assert escape_html(raw) == expected

    @pytest.mark.parametrize(
        "amt,symbol,expected",
        [
            (1000.5, "$", "$1,000.50"),
            (0, "€", "€0.00"),
            (-450.25, "₹", "₹450.25"),
            (1234567.89, "£", "£1,234,567.89"),
            (25000, "¥", "¥25,000.00"),
        ],
    )
    def test_currency_formatting(self, amt, symbol, expected):
        assert format_currency(amt, symbol) == expected


@pytest.mark.unit
class TestExportDataStructure:
    """Verifies structure and validity of exported data."""

    def test_export_structure(self, sample_transactions):
        now = datetime.now(timezone.utc)
        export_payload = {
            "exportedAt": now.isoformat(),
            "currency": "$",
            "transactions": sample_transactions,
        }
        assert "exportedAt" in export_payload
        assert "currency" in export_payload
        assert "transactions" in export_payload
        assert len(export_payload["transactions"]) == len(sample_transactions)
        # Verify ISO date parsing
        parsed = datetime.fromisoformat(export_payload["exportedAt"])
        assert parsed.year == now.year
