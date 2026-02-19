from typing import Dict, List
import requests


class OandaClient:
    def __init__(self, account_id: str, api_key: str, base_url: str):
        self.account_id = account_id
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})

    def get_account_summary(self) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/summary"
            res = self.session.get(url, timeout=20)
            res.raise_for_status()
            return res.json().get("account", {})
        except Exception:
            raise

    def _get_instruments(self, symbol: str = "") -> List[Dict]:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/instruments"
            params = {"instruments": symbol} if symbol else None
            res = self.session.get(url, params=params, timeout=20)
            res.raise_for_status()
            return res.json().get("instruments", [])
        except Exception:
            raise

    def get_price(self, instrument: str) -> float:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/pricing"
            res = self.session.get(url, params={"instruments": instrument}, timeout=20)
            res.raise_for_status()
            row = res.json().get("prices", [])[0]
            bid = float(row["bids"][0]["price"])
            ask = float(row["asks"][0]["price"])
            return (bid + ask) / 2
        except Exception:
            raise

    def get_instrument_metadata(self, symbol: str) -> Dict:
        try:
            rows = self._get_instruments(symbol)
            for row in rows:
                if row.get("name") == symbol:
                    return {
                        "name": row.get("name"),
                        "pipLocation": int(row.get("pipLocation", -4)),
                        "displayPrecision": int(row.get("displayPrecision", 5)),
                        "tradeUnitsPrecision": int(row.get("tradeUnitsPrecision", 0)),
                        "type": str(row.get("type", "UNKNOWN")),
                    }
            raise RuntimeError(f"Instrument {symbol} not found")
        except Exception:
            raise

    def get_pip_size(self, symbol: str) -> float:
        try:
            md = self.get_instrument_metadata(symbol)
            return 10 ** (-abs(int(md["pipLocation"])))
        except Exception:
            return 0.0001

    def get_instrument_spec(self, instrument: str) -> Dict:
        try:
            md = self.get_instrument_metadata(instrument)
            pip_size = self.get_pip_size(instrument)
            inst_type = str(md.get("type", "UNKNOWN")).upper()
            if "CURRENCY" in inst_type:
                contract_size = 100000.0
            elif any(k in instrument.upper() for k in ["XAU", "XAG", "XCU"]):
                contract_size = 100.0
            elif any(k in instrument.upper() for k in ["WTI", "BRENT", "UKOIL", "USOIL", "NGAS"]):
                contract_size = 1000.0
            elif "BTC" in instrument.upper():
                contract_size = 1.0
            else:
                contract_size = 1.0
            return {
                "symbol": instrument.upper(),
                "pip_size": pip_size,
                "display_precision": int(md.get("displayPrecision", 5)),
                "trade_units_precision": int(md.get("tradeUnitsPrecision", 0)),
                "contract_size": contract_size,
                "type": inst_type,
            }
        except Exception:
            return {
                "symbol": instrument.upper(),
                "pip_size": 0.0001,
                "display_precision": 5,
                "trade_units_precision": 0,
                "contract_size": 1.0,
                "type": "UNKNOWN",
            }

    def get_conversion_rate(self, base: str, quote: str) -> float:
        try:
            if base == quote:
                return 1.0
            symbol = f"{base}_{quote}"
            try:
                return self.get_price(symbol)
            except Exception:
                inv = f"{quote}_{base}"
                inv_price = self.get_price(inv)
                if inv_price <= 0:
                    raise RuntimeError("invalid inverse conversion rate")
                return 1.0 / inv_price
        except Exception:
            raise

    def get_pip_value(self, symbol: str, entry_price: float) -> float:
        try:
            pip_size = self.get_pip_size(symbol)
            quote = symbol.split("_")[-1] if "_" in symbol else symbol[-3:]
            if quote == "USD":
                return pip_size
            if entry_price <= 0:
                return pip_size
            return pip_size / entry_price
        except Exception:
            return 0.0001

    def get_account_ccy_loss_per_unit(self, symbol: str, entry_price: float, stop_price: float) -> float:
        try:
            md = self.get_instrument_metadata(symbol)
            pip_size = 10 ** (-abs(int(md["pipLocation"])))
            price_distance = abs(entry_price - stop_price)
            pip_distance = price_distance / pip_size if pip_size > 0 else 0.0

            pip_value_per_unit_usd = self.get_pip_value(symbol, entry_price)
            usd_sgd = self.get_conversion_rate("USD", "SGD")
            pip_value_per_unit_sgd = pip_value_per_unit_usd * usd_sgd
            account_ccy_loss_per_unit = pip_distance * pip_value_per_unit_sgd
            if account_ccy_loss_per_unit <= 0:
                raise RuntimeError("account_ccy_loss_per_unit invalid")
            return account_ccy_loss_per_unit
        except Exception:
            raise

    def get_sgd_loss_per_unit(self, symbol: str, entry_price: float, stop_price: float) -> float:
        try:
            return self.get_account_ccy_loss_per_unit(symbol, entry_price, stop_price)
        except Exception:
            raise

    def create_limit_order(self, instrument: str, units: int, price: float, stop_loss: float, client_tag: str) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/orders"
            payload = {
                "order": {
                    "type": "LIMIT",
                    "instrument": instrument,
                    "units": str(units),
                    "price": f"{price:.5f}",
                    "timeInForce": "GTC",
                    "positionFill": "DEFAULT",
                    "clientExtensions": {"tag": client_tag},
                    "stopLossOnFill": {"price": f"{stop_loss:.5f}"},
                }
            }
            res = self.session.post(url, json=payload, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise

    def list_open_trades(self) -> List[Dict]:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/openTrades"
            res = self.session.get(url, timeout=20)
            res.raise_for_status()
            return res.json().get("trades", [])
        except Exception:
            raise

    def close_trade_units(self, trade_id: str, units: str) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/trades/{trade_id}/close"
            res = self.session.put(url, json={"units": units}, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise

    def update_trade_sl(self, trade_id: str, sl_price: float) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/trades/{trade_id}/orders"
            payload = {"stopLoss": {"price": f"{sl_price:.5f}"}}
            res = self.session.put(url, json=payload, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise
