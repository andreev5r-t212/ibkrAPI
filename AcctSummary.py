import warnings
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
account = "U9451292"
base_url = "https://localhost:5001/v1/api"


def getPortfolioSummary(account_id):
    endpoint = f"portfolio/{account_id}/summary"
    try:
        sum_req = requests.get(f"{base_url}/{endpoint}", verify=False)
        sum_req.raise_for_status()
        return sum_req.json()
    except requests.exceptions.RequestException:
        return None


def getAccountSummary(accountId):
    endpoint = f"iserver/account/{accountId}/summary"
    try:
        resp = requests.get(f"{base_url}/{endpoint}", verify=False)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return None


def getAccounts():
    endpoint = f"iserver/accounts"
    try:
        sum_req = requests.get(f"{base_url}/{endpoint}", verify=False)
        sum_req.raise_for_status()
        return sum_req.json()
    except requests.exceptions.RequestException:
        return None


def isAuthenticated():
    endpoint = "iserver/auth/status"
    headers = {
        "Host": "api.ibkr.com",
        "Accept": "*/*",
        "User-Agent": "MyPythonApp/1.0",
        "Connection": "keep-alive"
    }

    try:
        auth_req = requests.get(f"{base_url}/{endpoint}", headers=headers, verify=False)
        auth_req.raise_for_status()
        return auth_req.json()
    except requests.exceptions.RequestException:
        return None


if __name__ == "__main__":
    print("Running Account Summary script...")

    auth_status = isAuthenticated()
    if auth_status:
        print("\nAuthentication Status:")
        print(json.dumps(auth_status, indent=2))
    else:
        print("Authentication failed.")

    accts = getAccounts()
    if accts:
        print("\nAccounts:")
        print(json.dumps(accts, indent=2))
    else:
        print("Failed to get accounts.")

    portfolio_summary = getPortfolioSummary(account)
    if portfolio_summary:
        print("\nPortfolio Summary:")
        print(json.dumps(portfolio_summary, indent=2))
    else:
        print("Failed to get portfolio summary.")