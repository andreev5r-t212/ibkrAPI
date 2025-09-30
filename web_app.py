from flask import Flask, jsonify, render_template
from api_services import getPortfolioSummary, getAccounts, isAuthenticated, getContractInfo

app = Flask(__name__)

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get portfolio summary
@app.route('/api/portfolio-summary/<account_id>')
def portfolio_summary_api(account_id):
    data = getPortfolioSummary(account_id)
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to retrieve portfolio summary"}), 500

# API endpoint to get accounts
@app.route('/api/accounts')
def accounts_api():
    data = getAccounts()
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to retrieve accounts"}), 500

# API endpoint to check authentication status
@app.route('/api/auth-status')
def auth_status_api():
    data = isAuthenticated()
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to retrieve authentication status"}), 500

# API endpoint to get contract info
@app.route('/api/contract-info/<conid>')
def contract_info_api(conid):
    data = getContractInfo(conid)
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to retrieve contract info"}), 500

if __name__ == '__main__':
    app.run(debug=True)