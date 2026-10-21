import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


@pytest.mark.e2e
class TestExpenseTrackerE2E:
    """End-to-end browser automation tests running against the live UI."""

    def test_initial_page_load(self, page):
        wait = WebDriverWait(page, 5)
        wait.until(EC.visibility_of_element_located((By.ID, "transactionList")))

        # Check page title
        assert "Expense Tracker" in page.title

        # Initial demo items: 6 demo transactions
        items = page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert len(items) == 6

        # Check overview stats
        balance_elem = page.find_element(By.ID, "totalBalance")
        assert "$2,832.50" in balance_elem.text

        income_elem = page.find_element(By.ID, "totalIncome")
        assert "+$4,100.00" in income_elem.text

        expense_elem = page.find_element(By.ID, "totalExpense")
        assert "-$1,267.50" in expense_elem.text

        status_badge = page.find_element(By.ID, "balanceStatus")
        assert "In Surplus" in status_badge.text

        savings_rate = page.find_element(By.ID, "savingsRate")
        assert "69%" in savings_rate.text

        results_count = page.find_element(By.ID, "resultsCount")
        assert "6 items" in results_count.text

    def test_add_new_expense_transaction(self, page):
        wait = WebDriverWait(page, 5)

        # Fill expense form
        title_input = page.find_element(By.ID, "titleInput")
        title_input.clear()
        title_input.send_keys("Gym Membership")

        amount_input = page.find_element(By.ID, "amountInput")
        amount_input.clear()
        amount_input.send_keys("55.00")

        date_input = page.find_element(By.ID, "dateInput")
        date_input.clear()
        date_input.send_keys("2026-10-21")

        cat_select = Select(page.find_element(By.ID, "categorySelect"))
        cat_select.select_by_value("health")

        note_input = page.find_element(By.ID, "noteInput")
        note_input.clear()
        note_input.send_keys("Monthly fitness pass")

        # Submit form
        page.find_element(By.ID, "submitBtn").click()

        # Check toast
        toast = wait.until(EC.visibility_of_element_located((By.ID, "toast")))
        assert "Transaction added successfully" in toast.text

        # Verify new item at the top of transaction list
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert "Gym Membership" in first_item.text
        assert "Healthcare" in first_item.text
        assert "-$55.00" in first_item.text

        # 6 + 1 = 7 items
        results_count = page.find_element(By.ID, "resultsCount")
        assert "7 items" in results_count.text

        # Expense updated: 1267.50 + 55 = 1322.50
        expense_elem = page.find_element(By.ID, "totalExpense")
        assert "$1,322.50" in expense_elem.text

        # Balance updated: 2832.50 - 55 = 2777.50
        balance_elem = page.find_element(By.ID, "totalBalance")
        assert "$2,777.50" in balance_elem.text

    def test_add_new_income_transaction(self, page):
        wait = WebDriverWait(page, 5)

        # Select Income radio button
        income_radio = page.find_element(By.CSS_SELECTOR, 'input[name="transactionType"][value="income"]')
        page.execute_script("arguments[0].click();", income_radio)

        # Check categories updated to income categories
        cat_select = Select(page.find_element(By.ID, "categorySelect"))
        options = [opt.get_attribute("value") for opt in cat_select.options]
        assert "salary" in options
        assert "freelance" in options
        assert "investments" in options

        # Fill income fields
        page.find_element(By.ID, "titleInput").send_keys("Dividend Payout")
        page.find_element(By.ID, "amountInput").send_keys("300.00")
        page.find_element(By.ID, "dateInput").send_keys("2026-10-21")
        cat_select.select_by_value("investments")

        page.find_element(By.ID, "submitBtn").click()

        # Toast
        toast = wait.until(EC.visibility_of_element_located((By.ID, "toast")))
        assert "Transaction added successfully" in toast.text

        # Verify list item
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert "Dividend Payout" in first_item.text
        assert "+$300.00" in first_item.text

        # Income updated: 4100 + 300 = 4400
        income_elem = page.find_element(By.ID, "totalIncome")
        assert "$4,400.00" in income_elem.text

    def test_client_side_validation_errors(self, page):
        # Empty out title and amount
        title_input = page.find_element(By.ID, "titleInput")
        title_input.clear()

        amount_input = page.find_element(By.ID, "amountInput")
        amount_input.clear()

        page.find_element(By.ID, "submitBtn").click()

        # Check invalid styling and error texts
        assert "is-invalid" in title_input.get_attribute("class")
        assert "is-invalid" in amount_input.get_attribute("class")

        title_error = page.find_element(By.ID, "titleError")
        assert "Please enter a description" in title_error.text

        amount_error = page.find_element(By.ID, "amountError")
        assert "Amount must be greater than 0" in amount_error.text

    def test_edit_transaction_flow(self, page):
        wait = WebDriverWait(page, 5)

        # Click Edit on first item
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        edit_btn = first_item.find_element(By.CSS_SELECTOR, ".edit-btn")
        edit_btn.click()

        # Verify form is in Edit mode
        form_title = page.find_element(By.ID, "formTitle")
        assert form_title.text == "Edit Transaction"

        edit_indicator = page.find_element(By.ID, "editIndicator")
        assert "hidden" not in edit_indicator.get_attribute("class")

        cancel_btn = page.find_element(By.ID, "cancelEditBtn")
        assert "hidden" not in cancel_btn.get_attribute("class")

        # Change description and amount
        title_input = page.find_element(By.ID, "titleInput")
        title_input.clear()
        title_input.send_keys("Updated Cinema Tickets")

        amount_input = page.find_element(By.ID, "amountInput")
        amount_input.clear()
        amount_input.send_keys("85.00")

        # Submit edits
        page.find_element(By.ID, "submitBtn").click()

        # Toast
        toast = wait.until(EC.visibility_of_element_located((By.ID, "toast")))
        assert "Transaction updated successfully" in toast.text

        # Verify updated text in item
        assert "Updated Cinema Tickets" in page.find_element(By.ID, "transactionList").text

        # Verify form reset to Add mode
        assert form_title.text == "Add Transaction"
        assert "hidden" in cancel_btn.get_attribute("class")

    def test_cancel_edit_flow(self, page):
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        first_item.find_element(By.CSS_SELECTOR, ".edit-btn").click()

        cancel_btn = page.find_element(By.ID, "cancelEditBtn")
        assert "hidden" not in cancel_btn.get_attribute("class")

        # Click cancel
        cancel_btn.click()

        # Form reverted
        form_title = page.find_element(By.ID, "formTitle")
        assert form_title.text == "Add Transaction"
        assert "hidden" in cancel_btn.get_attribute("class")

    def test_delete_transaction_modal_flow(self, page):
        wait = WebDriverWait(page, 5)

        initial_count = len(page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item"))
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        first_title = first_item.find_element(By.CSS_SELECTOR, ".item-title").text

        # Click Delete button
        first_item.find_element(By.CSS_SELECTOR, ".delete-btn").click()

        # Modal opens
        modal = wait.until(EC.visibility_of_element_located((By.ID, "confirmModal")))
        assert "hidden" not in modal.get_attribute("class")
        assert first_title in page.find_element(By.ID, "modalMessage").text

        # Cancel deletion first
        page.find_element(By.ID, "modalCancelBtn").click()
        assert "hidden" in modal.get_attribute("class")
        assert len(page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")) == initial_count

        # Open delete modal again and confirm
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        first_item.find_element(By.CSS_SELECTOR, ".delete-btn").click()
        wait.until(EC.visibility_of_element_located((By.ID, "modalConfirmBtn"))).click()

        # Check toast
        toast = wait.until(EC.visibility_of_element_located((By.ID, "toast")))
        assert "Transaction removed" in toast.text

        # Count reduced by 1
        new_count = len(page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item"))
        assert new_count == initial_count - 1

    def test_search_filtering(self, page):
        search_input = page.find_element(By.ID, "searchInput")
        search_input.clear()
        search_input.send_keys("Rent")

        # Should match "Apartment Rent"
        items = page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert len(items) == 1
        assert "Apartment Rent" in items[0].text

        # Results badge shows 1 item
        results_count = page.find_element(By.ID, "resultsCount")
        assert "1 item" in results_count.text

        # Clear search
        clear_btn = page.find_element(By.ID, "clearSearchBtn")
        clear_btn.click()

        # Restores 6 items
        items_restored = page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert len(items_restored) == 6

    def test_type_filtering(self, page):
        filter_type = Select(page.find_element(By.ID, "filterType"))

        # Expenses only
        filter_type.select_by_value("expense")
        items = page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert len(items) == 4
        for item in items:
            assert "-" in item.find_element(By.CSS_SELECTOR, ".item-amount").text

        # Income only
        filter_type.select_by_value("income")
        items = page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert len(items) == 2
        for item in items:
            assert "+" in item.find_element(By.CSS_SELECTOR, ".item-amount").text

        # All
        filter_type.select_by_value("all")
        assert len(page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")) == 6

    def test_sorting(self, page):
        sort_by = Select(page.find_element(By.ID, "sortBy"))

        # Highest amount first
        sort_by.select_by_value("amount-desc")
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        # Highest demo item is Monthly Salary ($3,500.00)
        assert "Monthly Salary" in first_item.text

        # Lowest amount first
        sort_by.select_by_value("amount-asc")
        first_item = page.find_element(By.CSS_SELECTOR, "#transactionList .transaction-item")
        # Lowest demo item is Weekend Cinema & Dinner ($65.00)
        assert "Weekend Cinema & Dinner" in first_item.text

    def test_currency_selection(self, page):
        currency_select = Select(page.find_element(By.ID, "currencySelect"))

        # Switch to Euro (€)
        currency_select.select_by_value("€")

        # Prefix in form input updates
        prefix = page.find_element(By.ID, "currencyPrefix")
        assert prefix.text == "€"

        # Balance displays €
        balance = page.find_element(By.ID, "totalBalance")
        assert "€" in balance.text

        # Switch to INR (₹)
        currency_select.select_by_value("₹")
        assert prefix.text == "₹"
        assert "₹" in balance.text

    def test_theme_toggle(self, page):
        body = page.find_element(By.TAG_NAME, "body")
        assert body.get_attribute("data-theme") == "light"

        theme_btn = page.find_element(By.ID, "themeToggleBtn")
        theme_btn.click()
        assert body.get_attribute("data-theme") == "dark"

        theme_btn.click()
        assert body.get_attribute("data-theme") == "light"

    def test_clear_all_and_demo_restore(self, page):
        wait = WebDriverWait(page, 5)

        # Click Clear All
        page.find_element(By.ID, "clearAllBtn").click()

        # Confirm modal
        wait.until(EC.visibility_of_element_located((By.ID, "modalConfirmBtn"))).click()

        # Toast
        toast = wait.until(EC.visibility_of_element_located((By.ID, "toast")))
        assert "All transactions cleared" in toast.text

        # Empty state is shown
        empty_state = page.find_element(By.ID, "emptyState")
        assert "hidden" not in empty_state.get_attribute("class")

        # Total balance is 0
        assert "$0.00" in page.find_element(By.ID, "totalBalance").text

        # Click Add Demo button in empty state
        page.find_element(By.ID, "emptyAddDemoBtn").click()

        # Demo items restored
        items = page.find_elements(By.CSS_SELECTOR, "#transactionList .transaction-item")
        assert len(items) == 6
        assert "$2,832.50" in page.find_element(By.ID, "totalBalance").text

    def test_localstorage_persistence(self, page):
        # Add a unique test transaction
        title_input = page.find_element(By.ID, "titleInput")
        title_input.send_keys("Persistent Server Subscription")

        amount_input = page.find_element(By.ID, "amountInput")
        amount_input.send_keys("49.99")

        page.find_element(By.ID, "submitBtn").click()

        # Refresh the browser
        page.refresh()

        # Wait for list to load and verify item survived the refresh
        WebDriverWait(page, 5).until(EC.visibility_of_element_located((By.ID, "transactionList")))
        assert "Persistent Server Subscription" in page.find_element(By.ID, "transactionList").text
        assert "-$49.99" in page.find_element(By.ID, "transactionList").text
