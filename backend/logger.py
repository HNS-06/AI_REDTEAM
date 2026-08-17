import json
import time
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "attack_log.json"
MAX_LOGS = 100

class Logger:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self._load_existing()
    
    def _load_existing(self):
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r") as f:
                    self.logs = json.load(f)
            except:
                self.logs = []
    
    def _save(self):
        try:
            with open(LOG_FILE, "w") as f:
                json.dump(self.logs[-MAX_LOGS:], f, indent=2)
        except:
            pass
    
    def log_exchange(self, 
                     mode: str,
                     user_input: str,
                     model_output: str,
                     guardrail_triggered: bool = False,
                     guardrail_reason: str = "",
                     secret_leaked: bool = False,
                     secret_redacted: bool = False):
        """Log a chat exchange with guardrail info."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "user_input": user_input,
            "model_output": model_output,
            "guardrail_triggered": guardrail_triggered,
            "guardrail_reason": guardrail_reason,
            "secret_leaked": secret_leaked,
            "secret_redacted": secret_redacted
        }
        self.logs.append(entry)
        self._save()
    
    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.logs[-limit:]
    
    def clear(self):
        self.logs = []
        self._save()

logger = Logger()