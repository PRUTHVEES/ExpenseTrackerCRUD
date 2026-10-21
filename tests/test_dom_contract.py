import re
import pytest

REQUIRED_DOM_IDS = [
    # Theme & Currency
    "themeToggleBtn",
    "themeIconSun",
    "themeIconMoon",
    "currencySelect",
    "currencyPrefix",
    "exportBtn",
    "resetDemoBtn",
    # Summary
    "totalBalance",
    "balanceStatus",
    "totalIncome",
    "incomeCount",
    "totalExpense",
    "expenseCount",
    "savingsRate",
    # Form
    "transactionForm",
    "formTitle",
    "editIndicator",
    "editTransactionId",
    "titleInput",
    "amountInput",
    "dateInput",
    "categorySelect",
    "noteInput",
    "submitBtn",
    "cancelEditBtn",
    # Errors
    "titleError",
    "amountError",
    "dateError",
    "categoryError",
    # Filters
    "searchInput",
    "clearSearchBtn",
    "filterType",
    "filterCategory",
    "sortBy",
    "clearAllBtn",
    "resultsCount",
    # List & Breakdown
    "transactionList",
    "emptyState",
    "emptyTitle",
    "emptySubtext",
    "emptyAddDemoBtn",
    "breakdownList",
    "breakdownTotal",
    # Modal & Toast
    "confirmModal",
    "modalTitle",
    "modalMessage",
    "modalCancelBtn",
    "modalConfirmBtn",
    "toast",
    "toastMessage",
]


@pytest.mark.dom
class TestDOMContract:
    """Validates that index.html satisfies the exact contract expected by app.js and modern accessibility standards."""

    def test_document_metadata(self, soup):
        title = soup.find("title")
        assert title is not None, "HTML should have a <title> element"
        assert "Expense Tracker" in title.text

        viewport = soup.find("meta", attrs={"name": "viewport"})
        assert viewport is not None, "Responsive viewport meta tag must be present"

        css_link = soup.find("link", attrs={"rel": "stylesheet", "href": "style.css"})
        assert css_link is not None, "style.css must be linked in <head>"

        js_script = soup.find("script", attrs={"src": "app.js"})
        assert js_script is not None, "app.js script tag must be included"

    @pytest.mark.parametrize("element_id", REQUIRED_DOM_IDS)
    def test_required_dom_id_exists(self, soup, element_id):
        elem = soup.find(id=element_id)
        assert elem is not None, f"Required DOM element id='{element_id}' is missing from index.html"

    def test_transaction_type_radios(self, soup):
        radios = soup.find_all("input", attrs={"name": "transactionType"})
        assert len(radios) == 2, "There must be exactly 2 transactionType radio inputs (expense, income)"
        values = {r.get("value") for r in radios}
        assert values == {"expense", "income"}

        expense_radio = next(r for r in radios if r.get("value") == "expense")
        assert expense_radio.has_attr("checked"), "Expense radio button should be checked by default"

    def test_form_fields_validation_attributes(self, soup):
        form = soup.find(id="transactionForm")
        assert form is not None
        assert form.has_attr("novalidate"), "Form should have novalidate to allow custom JS error handling"

        title_input = soup.find(id="titleInput")
        assert title_input.get("type") == "text"
        assert title_input.has_attr("required")
        assert int(title_input.get("maxlength", 0)) > 0

        amount_input = soup.find(id="amountInput")
        assert amount_input.get("type") == "number"
        assert amount_input.has_attr("required")
        assert float(amount_input.get("min", "0")) > 0
        assert amount_input.get("step") == "0.01"

        date_input = soup.find(id="dateInput")
        assert date_input.get("type") == "date"
        assert date_input.has_attr("required")

        cat_select = soup.find(id="categorySelect")
        assert cat_select.name == "select"
        assert cat_select.has_attr("required")

    def test_currency_options(self, soup):
        currency_select = soup.find(id="currencySelect")
        assert currency_select is not None
        options = {opt.get("value") for opt in currency_select.find_all("option")}
        expected_currencies = {"$", "₹", "€", "£", "¥"}
        assert expected_currencies.issubset(options), f"Missing currencies: {expected_currencies - options}"

    def test_sort_options(self, soup):
        sort_by = soup.find(id="sortBy")
        assert sort_by is not None
        options = {opt.get("value") for opt in sort_by.find_all("option")}
        assert {"date-desc", "date-asc", "amount-desc", "amount-asc"}.issubset(options)

    def test_filter_type_options(self, soup):
        filter_type = soup.find(id="filterType")
        assert filter_type is not None
        options = {opt.get("value") for opt in filter_type.find_all("option")}
        assert {"all", "expense", "income"}.issubset(options)

    def test_modal_accessibility_roles(self, soup):
        modal = soup.find(id="confirmModal")
        assert modal is not None
        assert modal.get("role") == "dialog"
        assert modal.get("aria-modal") == "true"
        assert modal.get("aria-labelledby") == "modalTitle"
        assert "hidden" in modal.get("class", [])

    def test_toast_accessibility_roles(self, soup):
        toast = soup.find(id="toast")
        assert toast is not None
        assert toast.get("role") == "status"
        assert toast.get("aria-live") == "polite"
        assert "hidden" in toast.get("class", [])

    def test_edit_indicator_initial_state(self, soup):
        indicator = soup.find(id="editIndicator")
        assert indicator is not None
        assert "hidden" in indicator.get("class", [])

        cancel_btn = soup.find(id="cancelEditBtn")
        assert cancel_btn is not None
        assert "hidden" in cancel_btn.get("class", [])
