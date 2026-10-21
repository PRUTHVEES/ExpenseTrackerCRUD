/**
 * Smart Expense Tracker - Modern CRUD Application
 * Pure Vanilla JavaScript (ES6+)
 */

// ==========================================================================
// Category Definitions & Metadata
// ==========================================================================
const CATEGORIES = {
  expense: [
    { id: 'food', label: 'Food & Dining', icon: '🍔', color: '#f97316' },
    { id: 'transport', label: 'Transportation', icon: '🚗', color: '#06b6d4' },
    { id: 'housing', label: 'Housing & Rent', icon: '🏠', color: '#8b5cf6' },
    { id: 'utilities', label: 'Bills & Utilities', icon: '💡', color: '#eab308' },
    { id: 'entertainment', label: 'Entertainment', icon: '🎬', color: '#ec4899' },
    { id: 'shopping', label: 'Shopping', icon: '🛍️', color: '#3b82f6' },
    { id: 'health', label: 'Healthcare', icon: '💊', color: '#10b981' },
    { id: 'education', label: 'Education', icon: '📚', color: '#6366f1' },
    { id: 'other_expense', label: 'Other Expense', icon: '📦', color: '#64748b' }
  ],
  income: [
    { id: 'salary', label: 'Salary / Wages', icon: '💼', color: '#10b981' },
    { id: 'freelance', label: 'Freelance & Projects', icon: '💻', color: '#3b82f6' },
    { id: 'investments', label: 'Investments', icon: '📈', color: '#8b5cf6' },
    { id: 'gifts', label: 'Gifts & Grants', icon: '🎁', color: '#ec4899' },
    { id: 'other_income', label: 'Other Income', icon: '💵', color: '#14b8a6' }
  ]
};

// ==========================================================================
// Initial Demo Data
// ==========================================================================
const DEMO_TRANSACTIONS = [
  {
    id: 'tx-1',
    title: 'Monthly Salary',
    amount: 3500.0,
    type: 'income',
    category: 'salary',
    date: getOffsetDateString(-5),
    note: 'Direct bank deposit'
  },
  {
    id: 'tx-2',
    title: 'Apartment Rent',
    amount: 950.0,
    type: 'expense',
    category: 'housing',
    date: getOffsetDateString(-4),
    note: 'October rent payment'
  },
  {
    id: 'tx-3',
    title: 'Supermarket Groceries',
    amount: 142.5,
    type: 'expense',
    category: 'food',
    date: getOffsetDateString(-3),
    note: 'Fresh produce & household supplies'
  },
  {
    id: 'tx-4',
    title: 'Freelance UI Design',
    amount: 600.0,
    type: 'income',
    category: 'freelance',
    date: getOffsetDateString(-2),
    note: 'Client landing page design'
  },
  {
    id: 'tx-5',
    title: 'Internet & Power Bill',
    amount: 110.0,
    type: 'expense',
    category: 'utilities',
    date: getOffsetDateString(-1),
    note: 'Monthly utilities auto-pay'
  },
  {
    id: 'tx-6',
    title: 'Weekend Cinema & Dinner',
    amount: 65.0,
    type: 'expense',
    category: 'entertainment',
    date: getOffsetDateString(0),
    note: 'Movie tickets and dinner'
  }
];

function getOffsetDateString(offsetDays) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  return d.toISOString().split('T')[0];
}

// ==========================================================================
// Application State
// ==========================================================================
const state = {
  transactions: [],
  currency: '$',
  theme: 'light',
  editingId: null,
  filters: {
    search: '',
    type: 'all',
    category: 'all',
    sortBy: 'date-desc'
  },
  pendingDeleteAction: null // Holds callback or ID to delete
};

// ==========================================================================
// DOM Elements
// ==========================================================================
const DOM = {
  // Theme & Currency
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  themeIconSun: document.getElementById('themeIconSun'),
  themeIconMoon: document.getElementById('themeIconMoon'),
  currencySelect: document.getElementById('currencySelect'),
  currencyPrefix: document.getElementById('currencyPrefix'),
  exportBtn: document.getElementById('exportBtn'),
  resetDemoBtn: document.getElementById('resetDemoBtn'),

  // Summary
  totalBalance: document.getElementById('totalBalance'),
  balanceStatus: document.getElementById('balanceStatus'),
  totalIncome: document.getElementById('totalIncome'),
  incomeCount: document.getElementById('incomeCount'),
  totalExpense: document.getElementById('totalExpense'),
  expenseCount: document.getElementById('expenseCount'),
  savingsRate: document.getElementById('savingsRate'),

  // Form
  form: document.getElementById('transactionForm'),
  formTitle: document.getElementById('formTitle'),
  editIndicator: document.getElementById('editIndicator'),
  editTransactionId: document.getElementById('editTransactionId'),
  typeRadios: document.querySelectorAll('input[name="transactionType"]'),
  titleInput: document.getElementById('titleInput'),
  amountInput: document.getElementById('amountInput'),
  dateInput: document.getElementById('dateInput'),
  categorySelect: document.getElementById('categorySelect'),
  noteInput: document.getElementById('noteInput'),
  submitBtn: document.getElementById('submitBtn'),
  cancelEditBtn: document.getElementById('cancelEditBtn'),

  // Form Errors
  titleError: document.getElementById('titleError'),
  amountError: document.getElementById('amountError'),
  dateError: document.getElementById('dateError'),
  categoryError: document.getElementById('categoryError'),

  // Filters
  searchInput: document.getElementById('searchInput'),
  clearSearchBtn: document.getElementById('clearSearchBtn'),
  filterType: document.getElementById('filterType'),
  filterCategory: document.getElementById('filterCategory'),
  sortBy: document.getElementById('sortBy'),
  clearAllBtn: document.getElementById('clearAllBtn'),
  resultsCount: document.getElementById('resultsCount'),

  // List & Breakdown
  transactionList: document.getElementById('transactionList'),
  emptyState: document.getElementById('emptyState'),
  emptyTitle: document.getElementById('emptyTitle'),
  emptySubtext: document.getElementById('emptySubtext'),
  emptyAddDemoBtn: document.getElementById('emptyAddDemoBtn'),
  breakdownList: document.getElementById('breakdownList'),
  breakdownTotal: document.getElementById('breakdownTotal'),

  // Modal & Toast
  confirmModal: document.getElementById('confirmModal'),
  modalTitle: document.getElementById('modalTitle'),
  modalMessage: document.getElementById('modalMessage'),
  modalCancelBtn: document.getElementById('modalCancelBtn'),
  modalConfirmBtn: document.getElementById('modalConfirmBtn'),
  toast: document.getElementById('toast'),
  toastMessage: document.getElementById('toastMessage')
};

// ==========================================================================
// Initialization
// ==========================================================================
function initApp() {
  loadPreferences();
  loadTransactions();
  setupEventListeners();
  populateFormCategories('expense');
  populateFilterCategories();
  setDefaultDate();
  renderApp();
}

function loadPreferences() {
  const savedTheme = localStorage.getItem('et_theme') || 'light';
  const savedCurrency = localStorage.getItem('et_currency') || '$';

  setTheme(savedTheme);
  state.currency = savedCurrency;
  DOM.currencySelect.value = savedCurrency;
  DOM.currencyPrefix.textContent = savedCurrency;
}

function loadTransactions() {
  const saved = localStorage.getItem('et_transactions');
  if (saved) {
    try {
      state.transactions = JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse transactions:', e);
      state.transactions = [...DEMO_TRANSACTIONS];
      saveTransactions();
    }
  } else {
    // Populate demo transactions initially
    state.transactions = [...DEMO_TRANSACTIONS];
    saveTransactions();
  }
}

function saveTransactions() {
  localStorage.setItem('et_transactions', JSON.stringify(state.transactions));
}

function setDefaultDate() {
  DOM.dateInput.value = new Date().toISOString().split('T')[0];
}

// ==========================================================================
// Event Listeners
// ==========================================================================
function setupEventListeners() {
  // Theme Toggle
  DOM.themeToggleBtn.addEventListener('click', toggleTheme);

  // Currency Selection
  DOM.currencySelect.addEventListener('change', (e) => {
    state.currency = e.target.value;
    DOM.currencyPrefix.textContent = state.currency;
    localStorage.setItem('et_currency', state.currency);
    renderApp();
    showToast(`Currency set to ${state.currency}`);
  });

  // Type change in form: update category options
  DOM.typeRadios.forEach((radio) => {
    radio.addEventListener('change', (e) => {
      populateFormCategories(e.target.value);
    });
  });

  // Form submission (Add or Edit)
  DOM.form.addEventListener('submit', handleFormSubmit);

  // Cancel Edit
  DOM.cancelEditBtn.addEventListener('click', cancelEdit);

  // Search & Filter Listeners
  DOM.searchInput.addEventListener('input', (e) => {
    state.filters.search = e.target.value.trim().toLowerCase();
    DOM.clearSearchBtn.classList.toggle('hidden', state.filters.search.length === 0);
    renderTransactionsList();
  });

  DOM.clearSearchBtn.addEventListener('click', () => {
    DOM.searchInput.value = '';
    state.filters.search = '';
    DOM.clearSearchBtn.classList.add('hidden');
    renderTransactionsList();
  });

  DOM.filterType.addEventListener('change', (e) => {
    state.filters.type = e.target.value;
    populateFilterCategories();
    renderTransactionsList();
  });

  DOM.filterCategory.addEventListener('change', (e) => {
    state.filters.category = e.target.value;
    renderTransactionsList();
  });

  DOM.sortBy.addEventListener('change', (e) => {
    state.filters.sortBy = e.target.value;
    renderTransactionsList();
  });

  // Clear All
  DOM.clearAllBtn.addEventListener('click', () => {
    if (state.transactions.length === 0) return;
    openModal({
      title: 'Clear All Transactions',
      message: 'Are you sure you want to delete all transactions? This cannot be reversed.',
      onConfirm: () => {
        state.transactions = [];
        saveTransactions();
        if (state.editingId) cancelEdit();
        renderApp();
        showToast('All transactions cleared');
      }
    });
  });

  // Export JSON
  DOM.exportBtn.addEventListener('click', exportData);

  // Reset Demo
  DOM.resetDemoBtn.addEventListener('click', () => {
    openModal({
      title: 'Load Demo Data',
      message: 'This will replace your current transactions with sample demo data. Continue?',
      onConfirm: () => {
        state.transactions = [...DEMO_TRANSACTIONS];
        saveTransactions();
        if (state.editingId) cancelEdit();
        renderApp();
        showToast('Demo transactions loaded');
      }
    });
  });

  DOM.emptyAddDemoBtn.addEventListener('click', () => {
    state.transactions = [...DEMO_TRANSACTIONS];
    saveTransactions();
    renderApp();
    showToast('Demo transactions loaded');
  });

  // Modal backdrop click & Cancel
  DOM.modalCancelBtn.addEventListener('click', closeModal);
  DOM.modalConfirmBtn.addEventListener('click', () => {
    if (typeof state.pendingDeleteAction === 'function') {
      state.pendingDeleteAction();
    }
    closeModal();
  });

  DOM.confirmModal.addEventListener('click', (e) => {
    if (e.target === DOM.confirmModal) closeModal();
  });

  // Keyboard accessibility for modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !DOM.confirmModal.classList.contains('hidden')) {
      closeModal();
    }
  });
}

// ==========================================================================
// Category Options Helpers
// ==========================================================================
function getSelectedFormType() {
  const selected = document.querySelector('input[name="transactionType"]:checked');
  return selected ? selected.value : 'expense';
}

function populateFormCategories(type, selectedCategoryId = null) {
  const categories = CATEGORIES[type] || [];
  DOM.categorySelect.innerHTML = '';

  categories.forEach((cat) => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = `${cat.icon} ${cat.label}`;
    if (selectedCategoryId && cat.id === selectedCategoryId) {
      opt.selected = true;
    }
    DOM.categorySelect.appendChild(opt);
  });
}

function populateFilterCategories() {
  const typeFilter = state.filters.type;
  let categories = [];

  if (typeFilter === 'expense') {
    categories = CATEGORIES.expense;
  } else if (typeFilter === 'income') {
    categories = CATEGORIES.income;
  } else {
    categories = [...CATEGORIES.expense, ...CATEGORIES.income];
  }

  const currentSelection = DOM.filterCategory.value;
  DOM.filterCategory.innerHTML = '<option value="all">All Categories</option>';

  categories.forEach((cat) => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = `${cat.icon} ${cat.label}`;
    if (currentSelection === cat.id) {
      opt.selected = true;
    }
    DOM.filterCategory.appendChild(opt);
  });
}

function getCategoryMeta(type, categoryId) {
  const list = CATEGORIES[type] || [];
  const found = list.find((c) => c.id === categoryId);
  if (found) return found;

  // Fallback search across both lists
  const fallback = [...CATEGORIES.expense, ...CATEGORIES.income].find((c) => c.id === categoryId);
  return fallback || { id: categoryId, label: categoryId, icon: '🏷️', color: '#64748b' };
}

// ==========================================================================
// Theme Management
// ==========================================================================
function toggleTheme() {
  const newTheme = state.theme === 'light' ? 'dark' : 'light';
  setTheme(newTheme);
}

function setTheme(theme) {
  state.theme = theme;
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('et_theme', theme);

  if (theme === 'dark') {
    DOM.themeIconSun.classList.add('hidden');
    DOM.themeIconMoon.classList.remove('hidden');
  } else {
    DOM.themeIconSun.classList.remove('hidden');
    DOM.themeIconMoon.classList.add('hidden');
  }
}

// ==========================================================================
// CRUD Operations
// ==========================================================================

// 1. CREATE & UPDATE (Form submission)
function handleFormSubmit(e) {
  e.preventDefault();

  const title = DOM.titleInput.value.trim();
  const amountStr = DOM.amountInput.value.trim();
  const date = DOM.dateInput.value;
  const category = DOM.categorySelect.value;
  const type = getSelectedFormType();
  const note = DOM.noteInput.value.trim();

  // Validate inputs
  let isValid = true;
  clearErrors();

  if (!title) {
    showError(DOM.titleInput, DOM.titleError, 'Please enter a description');
    isValid = false;
  }

  const amount = parseFloat(amountStr);
  if (isNaN(amount) || amount <= 0) {
    showError(DOM.amountInput, DOM.amountError, 'Amount must be greater than 0');
    isValid = false;
  }

  if (!date) {
    showError(DOM.dateInput, DOM.dateError, 'Please select a date');
    isValid = false;
  }

  if (!category) {
    showError(DOM.categorySelect, DOM.categoryError, 'Please select a category');
    isValid = false;
  }

  if (!isValid) return;

  if (state.editingId) {
    // UPDATE
    const index = state.transactions.findIndex((t) => t.id === state.editingId);
    if (index !== -1) {
      state.transactions[index] = {
        id: state.editingId,
        title,
        amount,
        type,
        category,
        date,
        note
      };
      saveTransactions();
      showToast('Transaction updated successfully');
      cancelEdit();
      renderApp();
    }
  } else {
    // CREATE
    const newTx = {
      id: 'tx-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6),
      title,
      amount,
      type,
      category,
      date,
      note
    };
    state.transactions.unshift(newTx);
    saveTransactions();
    showToast('Transaction added successfully');
    resetForm();
    renderApp();
  }
}

// 2. READ & RENDER
function renderApp() {
  renderSummary();
  renderTransactionsList();
  renderBreakdown();
}

function renderSummary() {
  let income = 0;
  let expense = 0;
  let incomeCount = 0;
  let expenseCount = 0;

  state.transactions.forEach((tx) => {
    const amt = Number(tx.amount) || 0;
    if (tx.type === 'income') {
      income += amt;
      incomeCount++;
    } else {
      expense += amt;
      expenseCount++;
    }
  });

  const balance = income - expense;

  // Format currency
  DOM.totalBalance.textContent = formatCurrency(balance);
  DOM.totalIncome.textContent = `+${formatCurrency(income)}`;
  DOM.totalExpense.textContent = `-${formatCurrency(expense)}`;

  // Counts
  DOM.incomeCount.textContent = `${incomeCount} transaction${incomeCount === 1 ? '' : 's'}`;
  DOM.expenseCount.textContent = `${expenseCount} transaction${expenseCount === 1 ? '' : 's'}`;

  // Balance status badge
  if (balance > 0) {
    DOM.balanceStatus.textContent = 'In Surplus';
    DOM.balanceStatus.className = 'stat-badge';
    DOM.balanceStatus.style.backgroundColor = 'var(--income-bg)';
    DOM.balanceStatus.style.color = 'var(--income-text)';
  } else if (balance < 0) {
    DOM.balanceStatus.textContent = 'In Deficit';
    DOM.balanceStatus.className = 'stat-badge';
    DOM.balanceStatus.style.backgroundColor = 'var(--expense-bg)';
    DOM.balanceStatus.style.color = 'var(--expense-text)';
  } else {
    DOM.balanceStatus.textContent = 'Balanced';
    DOM.balanceStatus.className = 'stat-badge';
    DOM.balanceStatus.style.backgroundColor = 'var(--primary-light)';
    DOM.balanceStatus.style.color = 'var(--primary)';
  }

  // Savings rate
  if (income > 0) {
    const rate = ((balance / income) * 100).toFixed(0);
    DOM.savingsRate.textContent = `${rate}%`;
  } else {
    DOM.savingsRate.textContent = '0%';
  }
}

function renderTransactionsList() {
  const filtered = getFilteredTransactions();

  DOM.resultsCount.textContent = `${filtered.length} item${filtered.length === 1 ? '' : 's'}`;

  if (filtered.length === 0) {
    DOM.transactionList.innerHTML = '';
    DOM.emptyState.classList.remove('hidden');

    if (state.transactions.length === 0) {
      DOM.emptyTitle.textContent = 'No transactions yet';
      DOM.emptySubtext.textContent = 'Get started by adding your first transaction using the form on the left.';
      DOM.emptyAddDemoBtn.classList.remove('hidden');
    } else {
      DOM.emptyTitle.textContent = 'No matching transactions';
      DOM.emptySubtext.textContent = 'Try adjusting your search query or filters.';
      DOM.emptyAddDemoBtn.classList.add('hidden');
    }
    return;
  }

  DOM.emptyState.classList.add('hidden');
  DOM.transactionList.innerHTML = '';

  filtered.forEach((tx) => {
    const li = createTransactionElement(tx);
    DOM.transactionList.appendChild(li);
  });
}

function getFilteredTransactions() {
  const { search, type, category, sortBy } = state.filters;

  return state.transactions
    .filter((tx) => {
      // Type filter
      if (type !== 'all' && tx.type !== type) return false;

      // Category filter
      if (category !== 'all' && tx.category !== category) return false;

      // Search filter
      if (search) {
        const titleMatch = (tx.title || '').toLowerCase().includes(search);
        const noteMatch = (tx.note || '').toLowerCase().includes(search);
        const catMeta = getCategoryMeta(tx.type, tx.category);
        const catMatch = catMeta.label.toLowerCase().includes(search);
        if (!titleMatch && !noteMatch && !catMatch) return false;
      }

      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date-asc':
          return new Date(a.date) - new Date(b.date);
        case 'amount-desc':
          return b.amount - a.amount;
        case 'amount-asc':
          return a.amount - b.amount;
        case 'date-desc':
        default:
          return new Date(b.date) - new Date(a.date);
      }
    });
}

function createTransactionElement(tx) {
  const cat = getCategoryMeta(tx.type, tx.category);
  const isIncome = tx.type === 'income';

  const li = document.createElement('li');
  li.className = 'transaction-item';
  li.id = `item-${tx.id}`;

  li.innerHTML = `
    <div class="item-left">
      <div class="category-icon-box" style="background-color: ${cat.color}15;" title="${escapeHtml(cat.label)}">
        <span>${cat.icon}</span>
      </div>
      <div class="item-details">
        <div class="item-title-row">
          <span class="item-title" title="${escapeHtml(tx.title)}">${escapeHtml(tx.title)}</span>
          <span class="item-category-tag">${escapeHtml(cat.label)}</span>
        </div>
        <div class="item-meta">
          <span>${formatDate(tx.date)}</span>
          ${tx.note ? `<span class="item-note" title="${escapeHtml(tx.note)}">&bull; ${escapeHtml(tx.note)}</span>` : ''}
        </div>
      </div>
    </div>

    <div class="item-right">
      <div class="item-amount ${isIncome ? 'income' : 'expense'}">
        ${isIncome ? '+' : '-'}${formatCurrency(tx.amount)}
      </div>
      <div class="item-actions">
        <button class="action-btn edit-btn" data-id="${tx.id}" title="Edit transaction" aria-label="Edit transaction">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
        </button>
        <button class="action-btn delete-btn" data-id="${tx.id}" title="Delete transaction" aria-label="Delete transaction">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>
    </div>
  `;

  // Attach actions
  li.querySelector('.edit-btn').addEventListener('click', () => startEdit(tx.id));
  li.querySelector('.delete-btn').addEventListener('click', () => confirmDelete(tx.id));

  return li;
}

// 3. EDIT (Update UI flow)
function startEdit(id) {
  const tx = state.transactions.find((t) => t.id === id);
  if (!tx) return;

  state.editingId = id;
  DOM.editTransactionId.value = id;

  // Set Type radio
  const targetRadio = document.querySelector(`input[name="transactionType"][value="${tx.type}"]`);
  if (targetRadio) {
    targetRadio.checked = true;
  }

  // Populate categories for that type and select current
  populateFormCategories(tx.type, tx.category);

  // Fill inputs
  DOM.titleInput.value = tx.title;
  DOM.amountInput.value = tx.amount;
  DOM.dateInput.value = tx.date;
  DOM.categorySelect.value = tx.category;
  DOM.noteInput.value = tx.note || '';

  // UI state updates
  DOM.formTitle.textContent = 'Edit Transaction';
  DOM.editIndicator.classList.remove('hidden');
  DOM.submitBtn.querySelector('span').textContent = 'Save Changes';
  DOM.cancelEditBtn.classList.remove('hidden');

  // Clear errors & scroll form into view
  clearErrors();
  DOM.form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  DOM.titleInput.focus();
}

function cancelEdit() {
  state.editingId = null;
  DOM.editTransactionId.value = '';
  DOM.formTitle.textContent = 'Add Transaction';
  DOM.editIndicator.classList.add('hidden');
  DOM.submitBtn.querySelector('span').textContent = 'Add Transaction';
  DOM.cancelEditBtn.classList.add('hidden');
  resetForm();
  clearErrors();
}

// 4. DELETE
function confirmDelete(id) {
  const tx = state.transactions.find((t) => t.id === id);
  if (!tx) return;

  openModal({
    title: 'Delete Transaction',
    message: `Are you sure you want to delete "${tx.title}" (${formatCurrency(tx.amount)})?`,
    onConfirm: () => {
      deleteTransaction(id);
    }
  });
}

function deleteTransaction(id) {
  state.transactions = state.transactions.filter((t) => t.id !== id);
  saveTransactions();

  if (state.editingId === id) {
    cancelEdit();
  }

  renderApp();
  showToast('Transaction removed');
}

// ==========================================================================
// Category Breakdown (Visual Analytics)
// ==========================================================================
function renderBreakdown() {
  const expenses = state.transactions.filter((t) => t.type === 'expense');
  const totalExpense = expenses.reduce((acc, t) => acc + (Number(t.amount) || 0), 0);

  DOM.breakdownTotal.textContent = `${formatCurrency(totalExpense)} spent`;

  if (totalExpense === 0) {
    DOM.breakdownList.innerHTML = `
      <div class="text-muted text-sm" style="text-align: center; padding: 1.5rem 0;">
        No expense data recorded yet.
      </div>
    `;
    return;
  }

  // Aggregate by category
  const categoryTotals = {};
  expenses.forEach((tx) => {
    categoryTotals[tx.category] = (categoryTotals[tx.category] || 0) + Number(tx.amount);
  });

  // Sort by highest spending
  const sortedCategories = Object.keys(categoryTotals).sort(
    (a, b) => categoryTotals[b] - categoryTotals[a]
  );

  DOM.breakdownList.innerHTML = '';

  sortedCategories.forEach((catId) => {
    const amount = categoryTotals[catId];
    const percentage = ((amount / totalExpense) * 100).toFixed(1);
    const cat = getCategoryMeta('expense', catId);

    const item = document.createElement('div');
    item.className = 'breakdown-item';
    item.innerHTML = `
      <div class="breakdown-item-header">
        <span class="breakdown-item-name">
          <span>${cat.icon}</span>
          <span>${escapeHtml(cat.label)}</span>
        </span>
        <span class="text-muted">${formatCurrency(amount)} (${percentage}%)</span>
      </div>
      <div class="breakdown-bar-bg">
        <div class="breakdown-bar-fill" style="width: ${percentage}%; background-color: ${cat.color};"></div>
      </div>
    `;
    DOM.breakdownList.appendChild(item);
  });
}

// ==========================================================================
// Export JSON
// ==========================================================================
function exportData() {
  if (state.transactions.length === 0) {
    showToast('No transactions to export');
    return;
  }

  const exportObj = {
    exportedAt: new Date().toISOString(),
    currency: state.currency,
    transactions: state.transactions
  };

  const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(exportObj, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute('href', dataStr);
  downloadAnchor.setAttribute('download', `expenses_backup_${new Date().toISOString().split('T')[0]}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();

  showToast('Export file downloaded');
}

// ==========================================================================
// Helpers: Validation & Formatting
// ==========================================================================
function resetForm() {
  DOM.form.reset();
  const expenseRadio = document.querySelector('input[name="transactionType"][value="expense"]');
  if (expenseRadio) expenseRadio.checked = true;
  populateFormCategories('expense');
  setDefaultDate();
}

function showError(inputEl, errorEl, message) {
  inputEl.classList.add('is-invalid');
  errorEl.textContent = message;
}

function clearErrors() {
  [DOM.titleInput, DOM.amountInput, DOM.dateInput, DOM.categorySelect].forEach((input) => {
    if (input) input.classList.remove('is-invalid');
  });
  DOM.titleError.textContent = '';
  DOM.amountError.textContent = '';
  DOM.dateError.textContent = '';
  DOM.categoryError.textContent = '';
}

function formatCurrency(num) {
  const formatted = Math.abs(num).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  return `${state.currency}${formatted}`;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('-');
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ==========================================================================
// Modal & Toast Components
// ==========================================================================
function openModal({ title, message, onConfirm }) {
  DOM.modalTitle.textContent = title;
  DOM.modalMessage.textContent = message;
  state.pendingDeleteAction = onConfirm;
  DOM.confirmModal.classList.remove('hidden');
}

function closeModal() {
  DOM.confirmModal.classList.add('hidden');
  state.pendingDeleteAction = null;
}

let toastTimeout = null;
function showToast(message) {
  if (toastTimeout) clearTimeout(toastTimeout);
  DOM.toastMessage.textContent = message;
  DOM.toast.classList.remove('hidden');

  toastTimeout = setTimeout(() => {
    DOM.toast.classList.add('hidden');
  }, 2800);
}

// ==========================================================================
// Run App
// ==========================================================================
document.addEventListener('DOMContentLoaded', initApp);
