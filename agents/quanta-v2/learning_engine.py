import json
import logging
import os
from datetime import datetime
from config import LEARNING_DB, STRATEGY_KEYWORDS

logger = logging.getLogger(__name__)

class LearningEngine:
    """Learn from trader commentary and patterns"""
    
    def __init__(self):
        self.db_file = LEARNING_DB
        self.lessons = []
        self._load_lessons()
    
    def _load_lessons(self):
        """Load existing lessons"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    for line in f:
                        self.lessons.append(json.loads(line))
            except Exception as e:
                logger.error(f"Error loading lessons: {e}")
    
    def _save_lesson(self, lesson):
        """Save lesson to file"""
        try:
            with open(self.db_file, 'a') as f:
                f.write(json.dumps(lesson) + '\n')
        except Exception as e:
            logger.error(f"Error saving lesson: {e}")
    
    def analyze_commentary(self, text, timestamp=None):
        """Extract insights from commentary"""
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        text_lower = text.lower()
        
        # Extract strategy keywords
        strategies_found = []
        for keyword in STRATEGY_KEYWORDS:
            if keyword in text_lower:
                strategies_found.append(keyword)
        
        # Extract sentiment
        sentiment = 'neutral'
        if any(word in text_lower for word in ['bullish', 'strong', 'breakout', 'moon']):
            sentiment = 'bullish'
        elif any(word in text_lower for word in ['bearish', 'weak', 'dump', 'crash']):
            sentiment = 'bearish'
        elif any(word in text_lower for word in ['caution', 'careful', 'risky']):
            sentiment = 'cautious'
        
        # Extract levels (support/resistance)
        levels = []
        level_pattern = r'(support|resistance)\s+(?:at|around)?\s+([\d.]+)'
        import re
        matches = re.finditer(level_pattern, text_lower)
        for match in matches:
            level_type = match.group(1)
            price = float(match.group(2))
            levels.append({'type': level_type, 'price': price})
        
        # Build lesson
        lesson = {
            'timestamp': timestamp,
            'text': text,
            'strategies': strategies_found,
            'sentiment': sentiment,
            'levels': levels,
            'confidence': self._calculate_confidence(text_lower)
        }
        
        if strategies_found or levels:
            self._save_lesson(lesson)
            self.lessons.append(lesson)
            logger.info(f"Learned: {len(strategies_found)} strategies, {len(levels)} levels")
        
        return lesson
    
    def _calculate_confidence(self, text):
        """Calculate confidence level from text"""
        high_confidence = ['high confidence', 'strong setup', 'perfect', 'ideal']
        low_confidence = ['low confidence', 'weak', 'uncertain', 'risky', 'careful']
        
        for phrase in high_confidence:
            if phrase in text:
                return 'high'
        
        for phrase in low_confidence:
            if phrase in text:
                return 'low'
        
        return 'medium'
    
    def get_context_for_signal(self, symbol):
        """Get relevant context for a symbol"""
        relevant = []
        
        for lesson in self.lessons[-20:]:  # Last 20 lessons
            if symbol.lower() in lesson['text'].lower():
                relevant.append(lesson)
        
        return relevant
    
    def detect_command(self, text):
        """Detect manual commands in text"""
        text_lower = text.lower()
        
        commands = {
            'move_sl_be': ['move sl to be', 'sl to entry', 'breakeven', 'be'],
            'close_half': ['close half', '50%', 'half position'],
            'take_partial': ['take partial', 'partial profits', 'close 10%'],
            'runner_active': ['runner active', 'let it run', 'trail'],
            'protect_profits': ['protect profits', 'lock profits', 'secure']
        }
        
        for command, phrases in commands.items():
            for phrase in phrases:
                if phrase in text_lower:
                    return command
        
        return None
