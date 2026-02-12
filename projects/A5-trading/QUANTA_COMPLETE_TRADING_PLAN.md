# QUANTA TRADING PLAN - Complete Strategy

## 1. DYNAMIC RISK MANAGEMENT

### Account Growth Tracking
```python
class RiskManager:
    def __init__(self):
        self.initial_balance = 2000
        self.current_balance = 2000  # Updates after each trade
        self.risk_percent = 2  # Always 2% of CURRENT balance
        
    def calculate_risk_amount(self):
        """Calculate $ risk based on current balance"""
        return self.current_balance * (self.risk_percent / 100)
    
    def update_balance(self, pnl):
        """Update balance after trade closes"""
        self.current_balance += pnl
        # Risk auto-adjusts: $40 at $2k, $80 at $4k, $100 at $5k
```

### Position Sizing Formula
```
Account: $2,000 → Risk: $40
Account: $4,000 → Risk: $80  
Account: $10,000 → Risk: $200

For each trade:
Risk Amount = Current Balance × 0.02
Lot Size = Risk Amount ÷ (Entry - SL) in pips
```

## 2. SIGNAL DETECTION & PARSING

### Primary Signal Format (CallistoFx)
```
🟢 XAUUSD BUY
Buy Range: 2685 - 2675
SL: 2665
TP: 2695 / 2715 / 2735 / 2755 / 2775
```

### Advanced Pattern Recognition
```python
SIGNAL_PATTERNS = {
    "primary": {
        "symbols": ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY"],
        "format": "emoji + symbol + direction",
        "entry_type": "range",  # Always range, never single price
        "tp_count": 5,  # Always 5 take profits
    },
    "secondary_indicators": {
        "swept_inside_bar": "High probability setup",
        "1hr_breakout": "Momentum trade",
        "daily_level": "Key support/resistance",
        "london_ny_session": "Best timing"
    }
}
```

## 3. SPLIT ENTRY STRATEGY (3-Tier)

### Why Split Entry?
- **Reduces risk** if price reverses
- **Better average entry** across range
- **Partial fills** protect capital

### Execution
```python
SPLIT_STRATEGY = {
    "entries": 3,
    "allocation": {
        "entry_1_high": {
            "price": "range_high",  # 2685
            "size": "33%",  # Conservative
            "risk": "highest",  # If hits SL, lose most here
        },
        "entry_2_mid": {
            "price": "range_mid",   # 2680
            "size": "33%",  # Balanced
            "risk": "medium",
        },
        "entry_3_low": {
            "price": "range_low",   # 2675
            "size": "34%",  # Aggressive
            "risk": "lowest",  # Best price, safest
        }
    }
}

# Example: $2,000 account, $40 risk
# Entry 1 (2685): 0.013 lots, risk $13
# Entry 2 (2680): 0.013 lots, risk $13  
# Entry 3 (2675): 0.014 lots, risk $14
# Total: 0.04 lots, $40 risk
```

## 4. EXIT STRATEGY (5-TIER TP LADDER)

### Breakeven Protection
```
When TP1 (+20 pips) hits:
→ Close Entry 1 (33% position)
→ Move SL of Entry 2 & 3 to breakeven (2680)
→ Result: Cannot lose money on remaining 67%
```

### TP Ladder Execution
```python
TP_STRATEGY = {
    "tp1": {
        "pips": 20,
        "close": "33%",  # Entry 1
        "action": "breakeven_others"
    },
    "tp2": {
        "pips": 50,
        "close": "20%",  # Small profit
        "action": "trail_sl_to_entry_plus_20"
    },
    "tp3": {
        "pips": 100,
        "close": "20%",
        "action": "lock_profit"
    },
    "tp4": {
        "pips": 150,
        "close": "15%",
        "action": "wide_trail"
    },
    "tp5_runner": {
        "pips": 200,
        "close": "12%",  # Let run with trailing SL
        "trail_rule": "SL = Current Price - 50 pips"
    }
}
```

## 5. LEARNING SYSTEM FROM CHANNEL CONTENT

### Content Types to Parse
```python
LEARNING_CONTENT = {
    "trade_signals": {
        "priority": "CRITICAL",
        "action": "execute_trade",
        "parse": ["symbol", "direction", "entry", "sl", "tp"]
    },
    
    "trade_breakdown": {
        "priority": "HIGH",
        "action": "analyze_and_learn",
        "content": "Post-trade analysis with pips gained/lost",
        "learn": {
            "what_worked": "Document successful setups",
            "what_failed": "Avoid these patterns",
            "market_conditions": "When to trade, when to skip"
        }
    },
    
    "educational_posts": {
        "priority": "MEDIUM",
        "action": "update_knowledge_base",
        "topics": [
            "Support/resistance levels",
            "Trend identification",
            "Risk management rules",
            "Session timing (London/NY/Asian)"
        ]
    },
    
    "video_transcripts": {
        "priority": "MEDIUM",
        "action": "extract_lessons",
        "method": "If video link posted, note topic",
        "learn": "Trading philosophy and strategy"
    },
    
    "chart_analysis": {
        "priority": "HIGH",
        "action": "pattern_recognition",
        "identify": [
            "Inside bar sweeps",
            "Breakout levels",
            "Trend continuation",
            "Reversal patterns"
        ]
    }
}
```

### Learning Database
```python
class LearningDatabase:
    def __init__(self):
        self.successful_setups = []  # What worked
        self.failed_setups = []      # What to avoid
        self.market_context = {}      # Current conditions
        
    def log_trade_result(self, signal, result, pnl):
        """Learn from each trade"""
        trade_data = {
            "signal": signal,
            "result": result,  # win/loss
            "pnl": pnl,
            "timestamp": datetime.now(),
            "market_conditions": self.get_current_context()
        }
        
        if pnl > 0:
            self.successful_setups.append(trade_data)
        else:
            self.failed_setups.append(trade_data)
    
    def get_current_context(self):
        """What should we know before trading?"""
        return {
            "session": self.detect_session(),  # London/NY/Asian
            "trend": self.detect_trend(),      # Up/Down/Sideways
            "recent_performance": self.last_5_trades(),
            "news_events": self.check_economic_calendar()
        }
```

## 6. RISK MANAGEMENT RULES

### Hard Rules (Never Break)
```python
HARD_RULES = {
    "max_daily_risk": "6% of account",  # 3 trades × 2%
    "max_concurrent_trades": 2,         # Never more than 2 open
    "no_trade_without_sl": True,        # Mandatory stop loss
    "breakeven_required": True,         # Must move to BE at TP1
    "no_overtrading": "Max 5 trades/day",
    "weekend_close": True,              # Close all before Friday 5PM EST
}
```

### Soft Rules (Can Adapt)
```python
SOFT_RULES = {
    "avoid_news": "30 min before/after high impact news",
    "session_preference": "London/NY overlap (8-11 AM EST)",
    "symbol_rotation": "If XAUUSD choppy, wait for EURUSD",
    "confidence_threshold": "Skip if signal score < 70%",
}
```

## 7. SIGNAL QUALITY SCORING

### Before Taking Trade
```python
def calculate_signal_score(signal, context):
    score = 0
    
    # Base score
    score += 40  # Signal from trusted channel
    
    # Session timing
    if context["session"] in ["london", "ny_overlap"]:
        score += 20
    
    # Trend alignment
    if signal["direction"] == context["trend"]:
        score += 15
    
    # Risk:Reward
    rr = calculate_risk_reward(signal)
    if rr >= 1:3:
        score += 15
    elif rr >= 1:2:
        score += 10
    
    # Recent performance
    if context["recent_win_rate"] > 60%:
        score += 10
    
    return score

# Trade size based on score
if score >= 80:
    size = "100%"  # Full 2% risk
elif score >= 60:
    size = "75%"   # 1.5% risk
elif score >= 40:
    size = "50%"   # 1% risk
else:
    size = "SKIP"  # Don't trade
```

## 8. REPORTING SYSTEM

### How Quanta Reports to Me
```python
REPORTING_LEVELS = {
    "critical": {
        "events": ["trade_executed", "trade_closed", "error_occurred"],
        "action": "immediate_notification",
        "format": "ALERT: [Event] - [Details]"
    },
    
    "daily": {
        "events": ["daily_summary", "pnl_report"],
        "action": "end_of_day_digest",
        "format": "Daily Report: [Trades] [Win/Loss] [P&L]"
    },
    
    "learning": {
        "events": ["pattern_detected", "insight_gained"],
        "action": "update_knowledge_base",
        "format": "Learned: [What] [Context]"
    }
}
```

### Example Reports
```
[CRITICAL] Trade Executed: XAUUSD BUY @ 2680 | SL: 2665 | TP: 2700
[CRITICAL] Trade Closed: XAUUSD | +45 pips | +$36 profit
[DAILY] Summary: 3 trades, 2 wins, 1 loss | Net: +$52
[LEARNING] Pattern: Inside bar sweeps have 78% win rate in London session
```

## 9. SCALING TO OTHER MARKETS

### Once Quanta Masters XAUUSD
```python
MARKET_EXPANSION = {
    "phase_1": {
        "market": "XAUUSD (Gold)",
        "timeline": "Week 1-2",
        "goal": "Consistent profitability",
        "criteria": "5+ consecutive winning days"
    },
    
    "phase_2": {
        "market": "EURUSD, GBPUSD",
        "timeline": "Week 3-4", 
        "goal": "Multi-market trading",
        "criteria": "Same pattern recognition works"
    },
    
    "phase_3": {
        "market": "Indices (US30, NAS100)",
        "timeline": "Month 2",
        "goal": "Diversified portfolio",
        "criteria": "Risk remains at 2% per trade"
    },
    
    "phase_4": {
        "market": "Crypto (BTC, ETH)",
        "timeline": "Month 3",
        "goal": "24/7 markets",
        "criteria": "Adapt to higher volatility"
    }
}
```

## 10. IMPLEMENTATION CHECKLIST

### Before First Trade
- [ ] Install Ollama + LLaVA
- [ ] Test vision accuracy (80%+ required)
- [ ] Connect OANDA API (practice account first)
- [ ] Program all parameters
- [ ] Test 5 paper trades
- [ ] Verify reports work

### Daily Operations
- [ ] Start agent (double-click)
- [ ] Verify connection
- [ ] Monitor first trade
- [ ] Review end-of-day report

### Success Metrics
- [ ] 60%+ win rate
- [ ] Average R:R 1:2 or better
- [ ] Max drawdown <10%
- [ ] Consistent daily profits

---

**This is the complete trading plan. Anything missing?**
