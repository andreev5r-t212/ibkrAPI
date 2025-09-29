import tkinter as tk
from tkinter import scrolledtext
import threading
import json
from AcctSummary import getPortfolioSummary, getAccountSummary, getAccounts, isAuthenticated, account
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# -----------------------
# Helpers
# -----------------------

def run_in_thread(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper

class StatCard(ttk.Frame):
    """Small labeled value card."""
    def __init__(self, master, title, value="—", width=220, **kwargs):
        super().__init__(master, padding=12, bootstyle="secondary", **kwargs)
        self.columnconfigure(0, weight=1)
        self._title = ttk.Label(self, text=title, bootstyle="secondary", anchor=W)
        self._title.grid(row=0, column=0, sticky=EW)
        self._value = ttk.Label(self, text=str(value), font=("Helvetica", 14, "bold"), anchor=W)
        self._value.grid(row=1, column=0, sticky=EW, pady=(4,0))
        self._width = width
        self._title.bind("<Configure>", self._resize)

    def _resize(self, *_):
        self.update_idletasks()
        self.configure(width=self._width)

    def set(self, value):
        self._value.configure(text=str(value))

class Collapsible(ttk.Frame):
    """Simple collapsible section."""
    def __init__(self, master, title, initially_open=True, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self._open = initially_open
        self._btn = ttk.Button(self, text=("▾ " if initially_open else "▸ ") + title,
                               bootstyle="link", cursor="hand2", command=self._toggle)
        self._btn.grid(row=0, column=0, sticky=EW, pady=(6,2))
        self.body = ttk.Frame(self)
        self.body.grid(row=1, column=0, sticky=EW)
        if not initially_open:
            self.body.grid_remove()

    def _toggle(self):
        self._open = not self._open
        self._btn.configure(text=("▾ " if self._open else "▸ ") + self._btn.cget("text")[2:])
        if self._open:
            self.body.grid()
        else:
            self.body.grid_remove()

class AcctSummaryGUI(ttk.Window):
    def __init__(self, theme_name="darkly"):
        super().__init__(themename=theme_name)
        self.title("IBKR API GUI")
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
        btns.grid_columnconfigure((0,1,2,3), weight=1)

        self.btn_acct_sum = ttk.Button(btns, text="Get Portfolio Summary", command=self.get_portfolio_summary, bootstyle="info-outline")
        self.btn_get_accts = ttk.Button(btns, text="Get Accounts", command=self.get_accounts, bootstyle="info-outline")
        self.btn_auth     = ttk.Button(btns, text="Check Auth Status", command=self.is_authenticated, bootstyle="info-outline")
        self.btn_clear    = ttk.Button(btns, text="Clear", command=self.clear_all, bootstyle="danger-outline")

        self.btn_acct_sum.grid(row=0, column=0, padx=6, pady=8, sticky=EW)
        self.btn_get_accts.grid(row=0, column=1, padx=6, pady=8, sticky=EW)
        self.btn_auth.grid(row=0, column=2, padx=6, pady=8, sticky=EW)
        self.btn_clear.grid(row=0, column=3, padx=6, pady=8, sticky=EW)

        # ---------- Main content with 2 columns
        content = ttk.Frame(self, padding=18)
        content.pack(fill=BOTH, expand=YES)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # Left: Account Summary (cards grid)
        left = ttk.LabelFrame(content, text="Account Summary", padding=14)
        left.grid(row=0, column=0, sticky=NSEW, padx=(0, 10))
        left.grid_columnconfigure((0,1,2), weight=1, uniform="cards")

        self.cards = {}
        preset_fields = [
            "NetLiquidation", "TotalCashValue", "GrossPositionValue", "BuyingPower",
            "AvailableFunds", "ExcessLiquidity", "EquityWithLoanValue", "InitMarginReq",
            "MaintMarginReq", "FullInitMarginReq", "FullMaintMarginReq"
        ]
        r, c = 0, 0
        for f in preset_fields:
            card = StatCard(left, f, "—")
            card.grid(row=r, column=c, sticky=EW, padx=6, pady=6)
            self.cards[f] = card
            c += 1
            if c > 2:
                c = 0
                r += 1

        self.dynamic_container = ttk.Frame(left)
        self.dynamic_container.grid(row=r+1, column=0, columnspan=3, sticky=EW)
        self.dynamic_container.grid_columnconfigure((0,1,2), weight=1, uniform="dyn")
        self._dyn_next_row = 0
        self._dyn_next_col = 0

        # Right: Accounts + Auth + Raw
        right = ttk.Frame(content)
        right.grid(row=0, column=1, sticky=NSEW)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        auth_sec = ttk.LabelFrame(right, text="Authentication", padding=12)
        auth_sec.grid(row=0, column=0, sticky=EW, pady=(0,10))
        self.lbl_auth = ttk.Label(auth_sec, text="Unknown", bootstyle="warning")
        self.lbl_auth.pack(anchor=W)

        accts_sec = ttk.LabelFrame(right, text="Accounts", padding=12)
        accts_sec.grid(row=1, column=0, sticky=EW)

        self.acct_list = ttk.Treeview(accts_sec, columns=("#","Account"), show="headings", height=6, bootstyle="info")
        self.acct_list.heading("#", text="#")
        self.acct_list.heading("Account", text="Account")
        self.acct_list.column("#", width=44, anchor=CENTER)
        self.acct_list.column("Account", width=180, anchor=W)
        self.acct_list.pack(fill=X)

        self.raw = Collapsible(right, "Raw Output (debug)", initially_open=False)
        self.raw.grid(row=2, column=0, sticky=NSEW, pady=(10,0))
        self.raw_body_text = scrolledtext.ScrolledText(self.raw.body, wrap=tk.WORD, height=8, font=("Helvetica", 10))
        self.raw_body_text.pack(fill=BOTH, expand=YES)

    def set_status(self, message, style="secondary"):
        self.after(0, lambda: self.status_bar.configure(text=message, bootstyle=style))

    def set_buttons_state(self, state):
        self.after(0, lambda: [btn.configure(state=state) for btn in (self.btn_acct_sum, self.btn_get_accts, self.btn_auth, self.btn_clear)])

    def clear_all(self):
        for card in self.cards.values():
            card.set("—")
        for w in self.dynamic_container.winfo_children():
            w.destroy()
        self._dyn_next_row = 0
        self._dyn_next_col = 0
        for i in self.acct_list.get_children():
            self.acct_list.delete(i)
        self.lbl_auth.configure(text="Unknown", bootstyle="warning")
        self.raw_body_text.delete("1.0", tk.END)
        self.set_status("Cleared.", style="success")

    def _append_dynamic_card(self, key, value):
        card = StatCard(self.dynamic_container, key, value)
        card.grid(row=self._dyn_next_row, column=self._dyn_next_col, sticky=EW, padx=6, pady=6)
        self._dyn_next_col += 1
        if self._dyn_next_col > 2:
            self._dyn_next_col = 0
            self._dyn_next_row += 1

    def update_summary_cards(self, data: dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                try:
                    v = json.dumps(v)
                except Exception:
                    v = str(v)
            if k in self.cards:
                self.cards[k].set(v)
            else:
                self._append_dynamic_card(k, v)

    def update_accounts(self, items):
        if isinstance(items, dict):
            if "accounts" in items:
                items = items.get("accounts")
            elif "Accounts" in items:
                items = items.get("Accounts")
            else:
                items = [str(v) for v in items.values() if isinstance(v, (str,int))]
        if not isinstance(items, list):
            items = [str(items)]
        for i in self.acct_list.get_children():
            self.acct_list.delete(i)
        for idx, acc in enumerate(items, start=1):
            self.acct_list.insert("", END, values=(idx, str(acc)))

    def update_auth(self, status):
        txt = str(status)
        style = "success" if str(status).lower() in ("true", "authenticated", "ok", "yes", "1") else "danger"
        self.lbl_auth.configure(text=txt, bootstyle=style)

    def _capture_stdout(self, callable_or_func):
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            if callable(callable_or_func):
                callable_or_func()
            else:
                callable_or_func
        finally:
            sys.stdout = old_stdout
        out = mystdout.getvalue().strip()
        return out

    @staticmethod
    def _parse_output(text):
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            pass
        try:
            start = text.rfind('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                maybe = text[start:end+1]
                return json.loads(maybe)
        except Exception:
            pass
        data = {}
        for line in text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        return data if data else text

    def _handle_result(self, result, kind):
        if kind == "summary":
            if isinstance(result, dict):
                self.update_summary_cards(result)
                self.set_status("Account summary loaded.", style="success")
            else:
                self.set_status("Unexpected summary format (see Raw Output).", style="warning")
        elif kind == "accounts":
            self.update_accounts(result)
            self.set_status("Accounts loaded.", style="success")
        elif kind == "auth":
            if isinstance(result, dict) and len(result) == 1:
                result = list(result.values())[0]
            self.update_auth(result)
            self.set_status("Auth status updated.", style="success")

    def append_raw(self, text):
        if not text:
            return
        self.after(0, lambda: (self.raw_body_text.insert(tk.END, text + "\n\n"), self.raw_body_text.see(tk.END)))

    @run_in_thread
    def get_portfolio_summary(self):
        self.set_status("Fetching account summary…", style="info")
        self.set_buttons_state(ttk.DISABLED)
        try:
            out = self._capture_stdout(lambda: getPortfolioSummary(account))
            self.append_raw(out)
            parsed = self._parse_output(out)
            self.after(0, self._handle_result, parsed, "summary")
        finally:
            self.after(0, self.set_buttons_state, ttk.NORMAL)

    @run_in_thread
    def get_accounts(self):
        self.set_status("Fetching accounts…", style="info")
        self.set_buttons_state(ttk.DISABLED)
        try:
            out = self._capture_stdout(getAccounts)
            self.append_raw(out)
            parsed = self._parse_output(out)
            self.after(0, self._handle_result, parsed, "accounts")
        finally:
            self.after(0, self.set_buttons_state, ttk.NORMAL)

    @run_in_thread
    def is_authenticated(self):
        self.set_status("Checking authentication…", style="info")
        self.set_buttons_state(ttk.DISABLED)
        try:
            out = self._capture_stdout(isAuthenticated)
            self.append_raw(out)
            parsed = self._parse_output(out)
            self.after(0, self._handle_result, parsed, "auth")
        finally:
            self.after(0, self.set_buttons_state, ttk.NORMAL)

if __name__ == "__main__":
    app = AcctSummaryGUI(theme_name="darkly")
    app.mainloop()