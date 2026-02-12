# QUANTA TESTING & VALIDATION PROTOCOL

## PHASE 0: PAPER TRADING (Before Real Money)

### Demo Mode (No OANDA API Required)
```python
TESTING_CONFIG = {
    "mode": "PAPER_TRADING",  # No real money
    "account_balance": 2000,   # Virtual
    "risk_per_trade": 2,       # 2% of virtual balance
    "trade_size": "MINIMUM",   # Smallest possible (test execution)
    "max_trades_per_day": 10,  # Unlimited from signals
    "validation_required": True # Must understand signal before trading
}
```

### Validation Gate (MUST Pass Before Each Trade)
```python
class TradeValidation:
    def validate_signal(self, signal):
        """Agent MUST answer these before trading"""
        
        validation = {
            "signal_understood": False,
            "trading_plan": None,
            "user_approval": False
        }
        
        # 1. Parse signal
        parsed = self.parse_signal(signal)
        
        # 2. Create trading plan
        plan = {
            "symbol": parsed["symbol"],
            "direction": parsed["direction"],
            "entries": self.calculate_split_entries(parsed),
            "total_risk": self.calculate_total_risk(parsed),
            "tp_strategy": self.describe_tp_ladder(parsed),
            "breakeven_rule": "Move SL to entry when TP1 hits",
            "why_this_trade": self.analyze_setup(parsed)
        }
        
        # 3. Present to user (me/you)
        report = f"""
        TRADE PROPOSAL:
        
        Signal: {plan['symbol']} {plan['direction']}
        
        Execution Plan:
        - Entry 1 (High): {plan['entries'][0]['price']} @ {plan['entries'][0]['size']} lots
        - Entry 2 (Mid): {plan['entries'][1]['price']} @ {plan['entries'][1]['size']} lots  
        - Entry 3 (Low): {plan['entries'][2]['price']} @ {plan['entries'][2]['size']} lots
        
        Risk Management:
        - Total Risk: ${plan['total_risk']:.2f} (2% of balance)
        - SL: {parsed['sl']}
        - TP Ladder: Close 10% @ TP1, 10% @ TP2, 20% @ TP3, 30% @ TP4, 30% runner
        - Breakeven: When TP1 hits, move remaining SL to entry
        
        Analysis:
        {plan['why_this_trade']}
        
        Do you approve this trade? (YES/NO/MODIFY)
        """
        
        return report
```

## PHASE 1: MINIMUM SIZE TESTING ($2 Trades)

### After 10 Successful Paper Trades
```python
REAL_TESTING = {
    "account": "OANDA Practice/Demo",
    "trade_size": "MINIMUM",  # $2-5 per trade
    "duration": "20 trades",
    "validation": "STILL_REQUIRED",  # Present plan each time
    
    "success_criteria": {
        "win_rate": ">= 60%",
        "average_risk_reward": ">= 1:2",
        "max_drawdown": "< 5%",
        "execution_accuracy": "100%"  # No mistakes clicking
    }
}
```

### What "Understands OANDA" Means:
```python
OANDA_MASTERY = {
    "login": "Can navigate to login page",
    "new_order": "Can click 'New Order' button",
    "symbol_entry": "Can select correct symbol (XAUUSD)",
    "direction": "Can select Buy/Sell correctly",
    "size": "Can enter lot size accurately",
    "sl_tp": "Can set SL and TP prices",
    "execute": "Can click 'Place Order'",
    "verify": "Can confirm trade opened successfully",
    "modify": "Can modify SL to breakeven when needed",
    "close": "Can close partial positions at TPs"
}

# Test Each Function:
TEST_CHECKLIST = [
    "✓ Open OANDA",
    "✓ Navigate to trading page", 
    "✓ Select XAUUSD",
    "✓ Click New Order",
    "✓ Enter 0.01 lot (minimum test)",
    "✓ Set SL correctly",
    "✓ Set TP1 correctly",
    "✓ Place order",
    "✓ Confirm in positions list",
    "✓ Modify SL to breakeven",
    "✓ Close partial position"
]
```

## PHASE 2: GRADUAL SIZE INCREASE

### Scaling Up (Only After 20 Successful Small Trades)
```python
SCALING_PLAN = {
    "trades_1_20": {
        "size": "Minimum ($2-5)",
        "validation": "Every trade approved by user"
    },
    "trades_21_30": {
        "size": "Small ($10-20)",
        "validation": "Every 3rd trade approved"
    },
    "trades_31_40": {
        "size": "Medium ($40-80)",  # Real 2% risk
        "validation": "Daily review only"
    },
    "trades_41+": {
        "size": "Full 2% risk",
        "validation": "Autonomous (unless requested)"
    }
}
```

## RISK PER TRADE (Multiple Signals Per Day)

### Each Signal = 2% Risk (Independent)
```python
DAILY_RISK_EXAMPLE = {
    "account_balance": 2000,
    "risk_per_trade": 40,  # 2%
    
    "scenario_1": {
        "signals_today": 3,
        "total_risk": 120,  # 3 × $40
        "exposure": "6% of account (acceptable)"
    },
    
    "scenario_2": {
        "signals_today": 6,
        "total_risk": 240,  # 6 × $40
        "exposure": "12% of account (HIGH)",
        "action": "Skip signals 5-6 or reduce size to 1% each"
    },
    
    "max_rule": {
        "max_concurrent_trades": 3,
        "max_daily_risk": "10% of account",
        "if_exceeded": "Reduce size to 1% per trade or skip"
    }
}
```

## TEACHING OANDA TO QUANTA

### Step-by-Step OANDA Tutorial
```python
OANDA_TUTORIAL = {
    "lesson_1": {
        "topic": "Login and Navigation",
        "screenshots": [
            "oanda_login_page.png",
            "dashboard_overview.png",
            "trading_page.png"
        ],
        "coordinates": {
            "login_button": "(x, y)",
            "username_field": "(x, y)",
            "password_field": "(x, y)",
            "submit": "(x, y)"
        }
    },
    
    "lesson_2": {
        "topic": "Placing a Trade",
        "steps": [
            "Click 'New Order'",
            "Select XAUUSD from dropdown",
            "Click BUY or SELL",
            "Enter units (lot size)",
            "Enter SL price",
            "Enter TP price",
            "Click 'Place Order'",
            "Verify in 'Positions' tab"
        ]
    },
    
    "lesson_3": {
        "topic": "Managing Open Trades",
        "steps": [
            "Find position in 'Positions' tab",
            "Click 'Modify' on position",
            "Change SL to new price",
            "Click 'Update'",
            "Close partial: Click 'Close'",
            "Enter units to close",
            "Click 'Close Position'"
        ]
    }
}

# Teaching Method:
# 1. I demonstrate each step (you watch)
# 2. Quanta tries with $2 trade
# 3. Verify she did it correctly
# 4. Repeat 5 times
# 5. Move to next lesson
```

## VERIFICATION CHECKLIST (Before Real Money)

### Must Pass All:
```python
VERIFICATION = {
    "vision_accuracy": {
        "test": "Read 20 CallistoFx signals",
        "pass": ">= 90% correct parsing",
        "status": "NOT_TESTED"
    },
    
    "oanda_navigation": {
        "test": "Complete 10 practice trades",
        "pass": "Zero mistakes clicking",
        "status": "NOT_TESTED"
    },
    
    "risk_calculation": {
        "test": "Calculate position size for 10 scenarios",
        "pass": "100% accurate sizing",
        "status": "NOT_TESTED"
    },
    
    "trade_execution": {
        "test": "Execute 20 paper trades",
        "pass": ">= 60% win rate, proper exits",
        "status": "NOT_TESTED"
    },
    
    "reporting": {
        "test": "Send 5 trade reports",
        "pass": "Clear, accurate information",
        "status": "NOT_TESTED"
    }
}

# Only when ALL = "PASSED" → Give OANDA API
```

## SAFETY PROTOCOLS

### Emergency Stops
```python
EMERGENCY_PROTOCOLS = {
    "user_can_stop": [
        "Close agent window",
        "Turn off PC",
        "Revoke OANDA API key",
        "Change OANDA password"
    ],
    
    "agent_auto_stops": [
        "3 consecutive losses → Pause, alert user",
        "Daily loss >5% → Stop trading",
        "Wrong symbol entered → Cancel order",
        "SL not set → Reject trade",
        "Price moved >50 pips from signal → Skip trade (stale)"
    ]
}
```

## TIMELINE

### Week 1: Learning Phase
- Day 1-2: Install Ollama, test vision
- Day 3-4: Teach OANDA navigation
- Day 5-7: 20 paper trades with validation

### Week 2: Testing Phase  
- Day 8-10: $2-5 real trades (20 trades)
- Day 11-12: Review performance
- Day 13-14: $10-20 trades if passing

### Week 3: Production Phase
- Day 15+: Full 2% risk trades
- Ongoing: Daily monitoring

**Only proceed to next phase after passing all checkpoints.**
