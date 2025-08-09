"""
Model Retraining Trigger System (Bonus Feature)

This module provides automated and manual model retraining capabilities:
1. Data change detection and automatic retraining
2. Manual retraining via API endpoint
3. Performance-based retraining triggers
4. Integration with MLflow for experiment tracking
"""

import os
import hashlib
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Import config constants
try:
    from ..utils.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, MLFLOW_TRACKING_URI, EXPERIMENT_NAME, MODEL_NAME
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, MLFLOW_TRACKING_URI, EXPERIMENT_NAME, MODEL_NAME


class RetrainTrigger:
    """Handles model retraining triggers and automation."""
    
    def __init__(self):
        self.mlflow_uri = MLFLOW_TRACKING_URI
        self.experiment_name = EXPERIMENT_NAME
        self.model_name = MODEL_NAME
        self.client = MlflowClient(tracking_uri=self.mlflow_uri)
        
        # Retraining configuration
        self.config = {
            "min_performance_threshold": 0.5,  # Minimum R² score
            "performance_degradation_threshold": 0.1,  # Trigger if performance drops by this much
            "data_change_check_interval": 3600,  # Check for data changes every hour (in seconds)
            "auto_retrain_enabled": True,
            "max_retrain_frequency": timedelta(hours=6),  # Don't retrain more than once every 6 hours
        }
        
        # State tracking
        self.state_file = "logs/retrain_state.json"
        self.ensure_state_file()
    
    def ensure_state_file(self):
        """Ensure the retraining state file exists."""
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.state_file):
            initial_state = {
                "last_retrain_time": None,
                "last_data_hash": None,
                "last_performance": None,
                "retrain_count": 0,
                "last_check_time": None
            }
            with open(self.state_file, 'w') as f:
                json.dump(initial_state, f, indent=2)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current retraining state."""
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def update_state(self, updates: Dict[str, Any]):
        """Update retraining state."""
        state = self.get_state()
        state.update(updates)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def calculate_data_hash(self, file_path: str) -> str:
        """Calculate hash of data file to detect changes."""
        if not os.path.exists(file_path):
            return ""
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def has_data_changed(self) -> Tuple[bool, str]:
        """Check if data has changed since last training."""
        current_hash = self.calculate_data_hash(PROCESSED_DATA_PATH)
        state = self.get_state()
        last_hash = state.get("last_data_hash")
        
        if last_hash is None or current_hash != last_hash:
            return True, current_hash
        return False, current_hash
    
    def get_current_model_performance(self) -> Optional[float]:
        """Get performance of current production model."""
        try:
            # Get latest model version
            versions = self.client.search_model_versions(f"name='{self.model_name}'")
            if not versions:
                return None
            
            latest_version = sorted(versions, key=lambda x: int(x.version))[-1]
            
            # Get the run that created this model version
            model_uri = f"models:/{self.model_name}/{latest_version.version}"
            model = mlflow.pyfunc.load_model(model_uri)
            
            # Evaluate on current test data
            if os.path.exists(PROCESSED_DATA_PATH):
                df = pd.read_csv(PROCESSED_DATA_PATH)
                X = df.drop("target", axis=1)
                y = df["target"]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                y_pred = model.predict(X_test)
                return r2_score(y_test, y_pred)
            
            return None
            
        except Exception as e:
            print(f"Error getting model performance: {e}")
            return None
    
    def should_retrain(self) -> Tuple[bool, str]:
        """Determine if model should be retrained."""
        state = self.get_state()
        reasons = []
        
        # Check if auto-retrain is enabled
        if not self.config["auto_retrain_enabled"]:
            return False, "Auto-retrain disabled"
        
        # Check minimum time between retrains
        last_retrain = state.get("last_retrain_time")
        if last_retrain:
            last_retrain_dt = datetime.fromisoformat(last_retrain)
            if datetime.now() - last_retrain_dt < self.config["max_retrain_frequency"]:
                return False, f"Too soon since last retrain ({last_retrain_dt})"
        
        # Check for data changes
        data_changed, current_hash = self.has_data_changed()
        if data_changed:
            reasons.append("Data has changed")
        
        # Check model performance
        current_performance = self.get_current_model_performance()
        if current_performance is not None:
            last_performance = state.get("last_performance")
            
            # Check if performance is below minimum threshold
            if current_performance < self.config["min_performance_threshold"]:
                reasons.append(f"Performance below threshold ({current_performance:.3f} < {self.config['min_performance_threshold']})")
            
            # Check if performance has degraded significantly
            elif last_performance and (last_performance - current_performance) > self.config["performance_degradation_threshold"]:
                reasons.append(f"Performance degraded ({last_performance:.3f} -> {current_performance:.3f})")
        
        # Retrain if any trigger conditions are met
        should_retrain = len(reasons) > 0
        reason = "; ".join(reasons) if reasons else "No retrain triggers"
        
        return should_retrain, reason
    
    def trigger_retrain(self, reason: str = "Manual trigger") -> Dict[str, Any]:
        """Trigger model retraining."""
        print(f"🔄 Starting model retraining: {reason}")
        
        start_time = datetime.now()
        
        try:
            # Set MLflow tracking
            mlflow.set_tracking_uri(self.mlflow_uri)
            mlflow.set_experiment(self.experiment_name)
            
            # Run the training script
            result = subprocess.run([
                "python", "src/models/train.py"
            ], capture_output=True, text=True, cwd=".")
            
            if result.returncode != 0:
                raise Exception(f"Training failed: {result.stderr}")
            
            # Get new model performance
            new_performance = self.get_current_model_performance()
            
            # Update state
            data_changed, current_hash = self.has_data_changed()
            self.update_state({
                "last_retrain_time": start_time.isoformat(),
                "last_data_hash": current_hash,
                "last_performance": new_performance,
                "retrain_count": self.get_state()["retrain_count"] + 1,
                "last_check_time": start_time.isoformat()
            })
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "reason": reason,
                "start_time": start_time.isoformat(),
                "duration_seconds": duration,
                "new_performance": new_performance,
                "message": f"✅ Retraining completed successfully in {duration:.1f}s"
            }
            
        except Exception as e:
            error_msg = f"❌ Retraining failed: {str(e)}"
            print(error_msg)
            
            return {
                "success": False,
                "reason": reason,
                "start_time": start_time.isoformat(),
                "error": str(e),
                "message": error_msg
            }
    
    def check_and_retrain(self) -> Optional[Dict[str, Any]]:
        """Check if retraining is needed and trigger if so."""
        self.update_state({"last_check_time": datetime.now().isoformat()})
        
        should_retrain, reason = self.should_retrain()
        
        if should_retrain:
            return self.trigger_retrain(f"Auto-trigger: {reason}")
        else:
            print(f"ℹ️  No retraining needed: {reason}")
            return None
    
    def get_retrain_status(self) -> Dict[str, Any]:
        """Get current retraining status and configuration."""
        state = self.get_state()
        should_retrain, reason = self.should_retrain()
        current_performance = self.get_current_model_performance()
        
        return {
            "auto_retrain_enabled": self.config["auto_retrain_enabled"],
            "should_retrain": should_retrain,
            "retrain_reason": reason,
            "current_performance": current_performance,
            "last_retrain_time": state.get("last_retrain_time"),
            "retrain_count": state.get("retrain_count", 0),
            "last_check_time": state.get("last_check_time"),
            "config": self.config,
            "data_changed": self.has_data_changed()[0]
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update retraining configuration."""
        self.config.update(new_config)
        return {"message": "Configuration updated", "new_config": self.config}


# Global instance
retrain_trigger = RetrainTrigger()


def main():
    """CLI interface for retraining."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            result = retrain_trigger.check_and_retrain()
            if result:
                print(json.dumps(result, indent=2))
        
        elif command == "trigger":
            reason = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Manual CLI trigger"
            result = retrain_trigger.trigger_retrain(reason)
            print(json.dumps(result, indent=2))
        
        elif command == "status":
            status = retrain_trigger.get_retrain_status()
            print(json.dumps(status, indent=2, default=str))
        
        else:
            print("Usage: python -m src.models.retrain_trigger [check|trigger|status] [reason]")
    else:
        print("Usage: python -m src.models.retrain_trigger [check|trigger|status] [reason]")


if __name__ == "__main__":
    main() 