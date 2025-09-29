import warnings
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
account = "U9451292"
base_url = "https://localhost:5001/v1/api"


def getPortfolioSummary(account):
    endpoint = f"portfolio/{account}/summary"
    try:
        # The 'verify=False' parameter is crucial to ignore the SSL certificate
        # that the local IBKR API gateway is using.
        sum_req = requests.get(f"{base_url}/{endpoint}", verify=False)
        sum_req.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        sum_json = json.dumps(sum_req.json(), indent=2)

        print(f"Status Code: {sum_req.status_code}")
        print(sum_json)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def getAccountSummary(accountId):
    endpoint = f"iserver/account/{accountId}/summary"
    try:
        resp = requests.get(f"{base_url}/{endpoint}", verify=False)
        resp.raise_for_status()
        resp_json = json.dumps(resp.json(), indent=2)
        print(f"Status Code: {resp.status_code}")
        print(resp_json)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def getAccounts():
    endpoint = f"iserver/accounts"
    try:
        sum_req = requests.get(f"{base_url}/{endpoint}", verify=False)
        sum_req.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        sum_json = json.dumps(sum_req.json(), indent=2)

        print(f"Status Code: {sum_req.status_code}")
        print(sum_json)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def isAuthenticated():
    endpoint = "iserver/auth/status"
    headers = {
        "Host": "api.ibkr.com",
        "Accept": "*/*",
        "User-Agent": "MyPythonApp/1.0",  # Example of a custom User-Agent
        "Connection": "keep-alive"
    }


    try:
        auth_req = requests.get(f"{base_url}/{endpoint}",headers=headers ,verify=False)
        auth_req.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        auth_json = json.dumps(auth_req.json(), indent=2)

        print(f"Status Code: {auth_req.status_code}")
        print(auth_json)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    getPortfolioSummary(account)