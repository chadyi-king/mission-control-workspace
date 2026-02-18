import re
import logging

logger = logging.getLogger(__name__)

class SignalParser:
    """Parse trading signals from CallistoFX format"""
    
    def __init__(self):
        # Clean emojis and special chars for parsing
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
    
    def clean_text(self, text):
        """Remove emojis and normalize text"""
        # Remove emojis
        text = self.emoji_pattern.sub('', text)
        # Normalize spaces
        text = ' '.join(text.split())
        return text.strip()
    
    def parse(self, text):
        """Parse signal from CallistoFX format"""
        original_text = text
        text = self.clean_text(text.upper())
        
        logger.info(f"Parsing: {text[:80]}...")
        
        # Pattern 1: 🟢XAUUSD🟢 BUY RANGE: 4922-4928 SL 4918 TP: 4958/4968/4988/4998
        # Pattern 2: 🔴XAUUSD🔴 SELL RANGE: 4922-4928 SL 4932 TP: 4888/4878
        
        # Extract symbol
        symbol_match = re.search(r'(XAUUSD|XAGUSD|EURUSD|GBPUSD|USDJPY|BTCUSD|US30|NAS100)', text)
        if not symbol_match:
            logger.debug("No symbol found")
            return None
        symbol = symbol_match.group(1)
        
        # Extract direction (BUY or SELL)
        direction_match = re.search(r'\b(BUY|SELL)\b', text)
        if not direction_match:
            logger.debug("No direction found")
            return None
        direction = direction_match.group(1)
        
        # Extract entry range (various formats)
        entry_patterns = [
            r'RANGE[:\s]+(\d+(?:\.\d+)?)[\s/-]+(\d+(?:\.\d+)?)',  # RANGE: 4922-4928
            r'(?:@|AT)[:\s]*(\d+(?:\.\d+)?)',  # @ 4925 or AT 4925
            r'(\d+(?:\.\d+)?)[\s/-]+(\d+(?:\.\d+)?)',  # 4922-4928
        ]
        
        entry_low = entry_high = None
        for pattern in entry_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    entry_low = float(match.group(1))
                    entry_high = float(match.group(2))
                else:
                    entry_low = entry_high = float(match.group(1))
                break
        
        if entry_low is None:
            logger.debug("No entry range found")
            return None
        
        # Extract SL
        sl_match = re.search(r'\bSL[:\s]*(\d+(?:\.\d+)?)\b', text)
        if not sl_match:
            logger.debug("No SL found")
            return None
        stop_loss = float(sl_match.group(1))
        
        # Extract TPs (multiple formats)
        tps = []
        
        # Format: TP: 4958/4968/4988/4998
        tp_match = re.search(r'TP[:\s]+([\d/\.\s]+)', text)
        if tp_match:
            tp_text = tp_match.group(1)
            # Split by / or space
            tp_values = re.findall(r'\d+(?:\.\d+)?', tp_text)
            tps = [float(tp) for tp in tp_values]
        
        # Alternative: TP1: 4958, TP2: 4968, etc.
        if not tps:
            for i in range(1, 6):
                tp_match = re.search(rf'TP{i}[:\s]*(\d+(?:\.\d+)?)', text)
                if tp_match:
                    tps.append(float(tp_match.group(1)))
        
        # Build signal
        signal = {
            'symbol': symbol,
            'direction': direction,
            'entry_low': entry_low,
            'entry_high': entry_high,
            'entry_mid': (entry_low + entry_high) / 2,
            'stop_loss': stop_loss,
            'take_profits': tps,
            'raw': original_text
        }
        
        logger.info(f"✅ Parsed: {symbol} {direction} @ {entry_low}-{entry_high}, SL: {stop_loss}, TPs: {tps}")
        return signal
    
    def validate(self, signal):
        """Validate signal has required fields and logic"""
        required = ['symbol', 'direction', 'entry_low', 'entry_high', 'stop_loss']
        
        for field in required:
            if field not in signal or signal[field] is None:
                logger.warning(f"Missing field: {field}")
                return False
        
        # Validate direction
        if signal['direction'] not in ['BUY', 'SELL']:
            logger.warning(f"Invalid direction: {signal['direction']}")
            return False
        
        # Validate SL logic
        if signal['direction'] == 'BUY':
            if signal['stop_loss'] >= signal['entry_low']:
                logger.warning(f"Invalid SL for BUY: SL {signal['stop_loss']} should be below entry {signal['entry_low']}")
                return False
        else:  # SELL
            if signal['stop_loss'] <= signal['entry_high']:
                logger.warning(f"Invalid SL for SELL: SL {signal['stop_loss']} should be above entry {signal['entry_high']}")
                return False
        
        logger.info("✅ Signal validated")
        return True
