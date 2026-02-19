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

    def get_instrument_spec(self, instrument: str) -> Dict:
        try:
            if instrument.upper() == "XAUUSD":
                return {
                    "symbol": "XAUUSD",
                    "pip_size": 0.01,
                    "display_precision": 2,
                    "trade_units_precision": 0,
                    "contract_size": 100.0,
                    "type": "METAL",
                }

            row = self._get_instruments(instrument)[0]
            pip_location = int(row.get("pipLocation", -4))
            pip_size = abs(float(10 ** pip_location))
            display_precision = int(row.get("displayPrecision", 5))
            trade_units_precision = int(row.get("tradeUnitsPrecision", 0))
            inst_type = str(row.get("type", "UNKNOWN")).upper()

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
                "display_precision": display_precision,
                "trade_units_precision": trade_units_precision,
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

    def get_pip_value(self, symbol: str) -> float:
        """Approximate USD pip value per unit for sizing conversion."""
        try:
            spec = self.get_instrument_spec(symbol)
            pip_size = float(spec.get("pip_size", 0.0001))
            price = self.get_price(symbol)
            if symbol.endswith("USD"):
                return pip_size
            if price <= 0:
                return pip_size
            return pip_size / price
        except Exception:
            return 0.0001

    def get_usd_loss_per_unit(self, symbol: str, entry: float, stop: float) -> float:
        try:
            instruments = self._get_instruments(symbol)
            for row in instruments:
                if row.get("name") == symbol:
                    pip_loc = abs(int(row.get("pipLocation", -4)))
                    break
            else:
                raise RuntimeError(f"Instrument {symbol} not found")

            broker_pip_size = 10 ** (-pip_loc)
            price_distance = abs(entry - stop)
            pip_distance = price_distance / broker_pip_size if broker_pip_size > 0 else 0.0

            pip_value = self.get_pip_value(symbol)
            usd_loss_per_unit = pip_distance * pip_value
            if usd_loss_per_unit <= 0:
                raise RuntimeError("usd_loss_per_unit invalid")
            return usd_loss_per_unit
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
