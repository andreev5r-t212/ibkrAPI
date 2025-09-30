// =========================================================================
// UI Element References
// =========================================================================
const outputEl = document.getElementById('output');
const statusEl = document.getElementById('status');
const accountIdEl = document.getElementById('accountId');
const conidInput = document.getElementById('conidInput');

// Button references
const portfolioBtn = document.getElementById('portfolioBtn');
const accountsBtn = document.getElementById('accountsBtn');
const authBtn = document.getElementById('authBtn');
const clearBtn = document.getElementById('clearBtn');
const contractBtn = document.getElementById('contractBtn');
const buttons = document.querySelectorAll('button');

// =========================================================================
// Event Listeners
// =========================================================================
portfolioBtn.addEventListener('click', getPortfolioSummary);
accountsBtn.addEventListener('click', getAccounts);
authBtn.addEventListener('click', isAuthenticated);
clearBtn.addEventListener('click', clearOutput);
contractBtn.addEventListener('click', getContractInfo);

// =========================================================================
// UI State Management Functions
// =========================================================================
function setStatus(message, style = 'text-muted') {
    statusEl.textContent = message;
    statusEl.className = `text-center mb-3 ${style}`;
}

function toggleButtons(state) {
    buttons.forEach(btn => btn.disabled = !state);
    accountIdEl.disabled = !state;
    conidInput.disabled = !state;
}

// =========================================================================
// API & Data Fetching
// =========================================================================
async function fetchData(endpoint) {
    toggleButtons(false);
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Error fetching data:', error);
        return { success: false, error: error.message };
    } finally {
        toggleButtons(true);
    }
}

// =========================================================================
// API Call Functions
// =========================================================================
async function getPortfolioSummary() {
    const accountId = accountIdEl.value;
    if (!accountId) {
        setStatus('Please enter an Account ID.', 'text-warning');
        return;
    }
    setStatus('Fetching portfolio summary...', 'text-primary');
    const result = await fetchData(`/api/portfolio-summary/${accountId}`);
    if (result.success) {
        displayPortfolioSummary(result.data);
        setStatus('Portfolio summary loaded.', 'text-success');
    } else {
        displayError(result.error);
        setStatus('Failed to load portfolio summary.', 'text-danger');
    }
}

async function getAccounts() {
    setStatus('Fetching accounts...', 'text-primary');
    const result = await fetchData('/api/accounts');
    if (result.success) {
        displayAccounts(result.data);
        setStatus('Accounts loaded.', 'text-success');
    } else {
        displayError(result.error);
        setStatus('Failed to load accounts.', 'text-danger');
    }
}

async function isAuthenticated() {
    setStatus('Checking authentication status...', 'text-primary');
    const result = await fetchData('/api/auth-status');
    if (result.success) {
        displayAuthStatus(result.data);
        const authStatus = result.data.authenticated || result.data.is_authenticated;
        const statusMessage = authStatus ? 'Authentication successful.' : 'Authentication failed.';
        const statusStyle = authStatus ? 'text-success' : 'text-danger';
        setStatus(statusMessage, statusStyle);
    } else {
        displayError(result.error);
        setStatus('Failed to check authentication.', 'text-danger');
    }
}

async function getContractInfo() {
    const conid = conidInput.value;
    if (!conid) {
        setStatus('Please enter a Contract ID.', 'text-warning');
        return;
    }
    setStatus('Fetching contract information...', 'text-info');
    const result = await fetchData(`/api/contract-info/${conid}`);
    if (result.success) {
        displayContractInfo(result.data);
        setStatus('Contract information loaded.', 'text-success');
    } else {
        displayError(result.error);
        setStatus('Failed to load contract information.', 'text-danger');
    }
}

// =========================================================================
// Display Functions
// =========================================================================
function clearOutput() {
    outputEl.innerHTML = '';
    setStatus('Ready.', 'text-muted');
}

function displayError(error) {
    outputEl.innerHTML = `<div class="alert alert-danger" role="alert"><strong>Error:</strong> ${error}</div>`;
}

/**
 * Creates and returns a single HTML card element.
 * @param {string} title The title of the card.
 * @param {string} value The value to display in the card.
 * @returns {string} The HTML string for the card.
 */
function createStatCard(title, value) {
    return `
        <div class="col">
            <div class="card stat-card">
                <div class="card-body">
                    <h5 class="card-title">${title}</h5>
                    <p class="card-text">${value}</p>
                </div>
            </div>
        </div>
    `;
}

function displayPortfolioSummary(data) {
    const requestedFields = [
        'netliquidation', 'equitywithloanvalue', 'totalcashvalue', 'initmarginreq',
        'maintmarginreq', 'availablefunds', 'excessliquidity', 'buyingpower'
    ];

    let cardsHtml = '';
    for (const key of requestedFields) {
        const fieldData = data[key];
        if (!fieldData) continue;

        let formattedValue = '—';
        if (fieldData.amount !== undefined && fieldData.amount !== null) {
            formattedValue = parseFloat(fieldData.amount).toFixed(2);
            if (fieldData.currency) {
                formattedValue += ` ${fieldData.currency}`;
            }
        } else if (fieldData.value !== undefined && fieldData.value !== null && fieldData.value !== "null") {
            formattedValue = fieldData.value;
        }

        const friendlyKey = key
            .replace(/([a-z])([A-Z])/g, '$1 $2')
            .replace(/-/g, ' ')
            .replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')
            .replace(/\b\w/g, char => char.toUpperCase());

        cardsHtml += createStatCard(friendlyKey, formattedValue);
    }

    const html = `
        <div class="card bg-light">
            <div class="card-header">Account Summary</div>
            <div class="card-body">
                <div class="row row-cols-1 row-cols-md-3 g-4">
                    ${cardsHtml}
                </div>
            </div>
        </div>
    `;
    outputEl.innerHTML = html;
}

function displayAccounts(data) {
    const accounts = Array.isArray(data.accounts) ? data.accounts : Object.values(data.accounts || {});

    const listItemsHtml = accounts.map(account => `
        <li class="list-group-item">${account}</li>
    `).join('');

    const html = `
        <div class="card bg-light">
            <div class="card-header">Accounts</div>
            <div class="card-body">
                <ul class="list-group list-group-flush">
                    ${listItemsHtml}
                </ul>
            </div>
        </div>
    `;
    outputEl.innerHTML = html;
}

function displayAuthStatus(data) {
    const authStatus = data.authenticated || data.is_authenticated;
    const statusText = authStatus ? 'Authenticated' : 'Not Authenticated';
    const statusStyle = authStatus ? 'text-success' : 'text-danger';

    const html = `
        <div class="card text-center bg-light">
            <div class="card-body">
                <h5 class="card-title mb-0">Authentication Status</h5>
                <p class="card-text ${statusStyle} fs-4 fw-bold mt-2">${statusText}</p>
            </div>
        </div>
    `;
    outputEl.innerHTML = html;
}

function displayContractInfo(data) {
    const cardData = [
        { key: 'symbol', label: 'Symbol' },
        { key: 'con_id', label: 'Contract ID' },
        { key: 'company_name', label: 'Company Name' },
        { key: 'sec_type', label: 'Security Type' },
        { key: 'exchange', label: 'Exchange' },
        { key: 'trading_class', label: 'Trading Class' },
        { key: 'currency', label: 'Currency' },
        { key: 'category', label: 'Category' }
    ];

    let cardsHtml = '';
    cardData.forEach(item => {
        const value = data[item.key] || '—';
        cardsHtml += createStatCard(item.label, value);
    });

    let validExchangesHtml = '';
    if (Array.isArray(data.valid_exchanges) && data.valid_exchanges.length > 0) {
        const listItems = data.valid_exchanges.map(exchange => `
            <li class="list-group-item stat-card">${exchange}</li>
        `).join('');
        validExchangesHtml = `
            <div class="mt-4">
                <h5 class="card-title">Valid Exchanges</h5>
                <ul class="list-group list-group-flush">
                    ${listItems}
                </ul>
            </div>
        `;
    }

    const html = `
        <div class="card bg-light">
            <div class="card-header">Contract Information</div>
            <div class="card-body">
                <div class="row row-cols-1 row-cols-md-3 g-4">
                    ${cardsHtml}
                </div>
                ${validExchangesHtml}
            </div>
        </div>
    `;
    outputEl.innerHTML = html;
}