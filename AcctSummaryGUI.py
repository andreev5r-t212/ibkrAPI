import tkinter as tk
from tkinter import scrolledtext
import threading
import json
from AcctSummary import getPortfolioSummary, getAccounts, isAuthenticated, account
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


# -----------------------
# Helpers
# -----------------------

def run_in_thread(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()

    return wrapper


class AcctSummaryGUI(ttk.Window):
    def __init__(self, theme_name="darkly"):
        super().__init__(themename=theme_name)
        self.title("IBKR API GUI (Simplified)")
        self.geometry("980x680")
        self.minsize(860, 560)

        # ---------- Top bar
        topbar = ttk.Frame(self, padding=(18, 14))
        topbar.pack(side=TOP, fill=X)

        title = ttk.Label(topbar, text="IBKR Control Panel", font=("Helvetica", 16, "bold"))
        title.pack(side=LEFT)

        self.status_bar = ttk.Label(topbar, text="Ready.", bootstyle="success")
        self.status_bar.pack(side=RIGHT)

        # ---------- Buttons
        btns = ttk.Frame(self, padding=(18, 0))
        btns.pack(side=TOP, fill=X)
        btns.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_acct_sum = ttk.Button(btns, text="Get Portfolio Summary", command=self.get_portfolio_summary,
                                       bootstyle="info-outline")
        self.btn_get_accts = ttk.Button(btns, text="Get Accounts", command=self.get_accounts, bootstyle="info-outline")
        self.btn_auth = ttk.Button(btns, text="Check Auth Status", command=self.is_authenticated,
                                   bootstyle="info-outline")
        self.btn_clear = ttk.Button(btns, text="Clear", command=self.clear_all, bootstyle="danger-outline")

        self.btn_acct_sum.grid(row=0, column=0, padx=6, pady=8, sticky=EW)
        self.btn_get_accts.grid(row=0, column=1, padx=6, pady=8, sticky=EW)
        self.btn_auth.grid(row=0, column=2, padx=6, pady=8, sticky=EW)
        self.btn_clear.grid(row=0, column=3, padx=6, pady=8, sticky=EW)

        # ---------- Main content with a single text area
        content = ttk.Frame(self, padding=18)
        content.pack(fill=BOTH, expand=YES)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.raw_output_text = scrolledtext.ScrolledText(content, wrap=tk.WORD, font=("Helvetica", 10))
        self.raw_output_text.grid(row=0, column=0, sticky=NSEW)

    def set_status(self, message, style="secondary"):
        self.after(0, lambda: self.status_bar.configure(text=message, bootstyle=style))

    def set_buttons_state(self, state):
        self.after(0, lambda: [btn.configure(state=state) for btn in
                               (self.btn_acct_sum, self.btn_get_accts, self.btn_auth, self.btn_clear)])

    def clear_all(self):
        self.raw_output_text.delete("1.0", tk.END)
        self.set_status("Cleared.", style="success")

    def _handle_result(self, result, kind):
        if result is None:
            self.set_status(f"Error fetching {kind}. Check the API server status.", style="danger")
            self.append_raw(
                f"An error occurred during the API call for {kind}. The API server may not be running or accessible.")
            return

        self.append_raw(f"--- {kind.capitalize()} Data ---\n")
        self.append_raw(json.dumps(result, indent=2))
        self.set_status(f"{kind.capitalize()} data loaded.", style="success")

    def append_raw(self, text):
        if not text:
            return
        self.after(0, lambda: (self.raw_output_text.insert(tk.END, text + "\n\n"), self.raw_output_text.see(tk.END)))

    @run_in_thread
    def get_portfolio_summary(self):
        self.set_status("Fetching account summary…", style="info")
        self.set_buttons_state(ttk.DISABLED)
        try:
            summary_data = getPortfolioSummary(account)
            self.after(0, self._handle_result, summary_data, "summary")
        finally:
            self.after(0, self.set_buttons_state, ttk.NORMAL)

    @run_in_thread
    def get_accounts(self):
        self.set_status("Fetching accounts…", style="info")
        self.set_buttons_state(ttk.DISABLED)
        try:
            accounts_data = getAccounts()
            self.after(0, self._handle_result, accounts_data, "accounts")
        finally:
            self.after(0, self.set_buttons_state, ttk.NORMAL)

    @run_in_thread
    def is_authenticated(self):
        self.set_status("Checking authentication…", style="info")
        self.set_buttons_state(ttk.DISABLED)
        try:
            auth_data = isAuthenticated()
            self.after(0, self._handle_result, auth_data, "auth")
        finally:
            self.after(0, self.set_buttons_state, ttk.NORMAL)


if __name__ == "__main__":
    app = AcctSummaryGUI(theme_name="darkly")
    app.mainloop()