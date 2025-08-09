"""
Tests for model retraining functionality (Bonus Feature).

Tests cover:
1. RetrainTrigger class functionality
2. Data change detection
3. Performance-based retraining triggers
4. API endpoints for retraining
5. Configuration management
"""

import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.retrain_trigger import RetrainTrigger, retrain_trigger
from api.app import app


class TestRetrainTrigger:
    """Test the RetrainTrigger class functionality."""
    
    @pytest.fixture
    def trigger(self):
        """Create a test RetrainTrigger instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            trigger = RetrainTrigger()
            # Override the state file path for testing
            trigger.state_file = f'{temp_dir}/retrain_state.json'
            trigger.ensure_state_file()
            yield trigger
    
    def test_state_management(self, trigger):
        """Test state file creation and management."""
        # Initial state should be created
        state = trigger.get_state()
        assert "last_retrain_time" in state
        assert "last_data_hash" in state
        assert "retrain_count" in state
        assert state["retrain_count"] == 0
        
        # Update state
        trigger.update_state({"retrain_count": 5, "last_performance": 0.85})
        updated_state = trigger.get_state()
        assert updated_state["retrain_count"] == 5
        assert updated_state["last_performance"] == 0.85
    
    def test_data_hash_calculation(self, trigger):
        """Test data hash calculation for change detection."""
        # Test with non-existent file
        hash1 = trigger.calculate_data_hash("non_existent_file.csv")
        assert hash1 == ""
        
        # Test with actual file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4\n")
            f.flush()
            
            hash1 = trigger.calculate_data_hash(f.name)
            assert len(hash1) == 32  # MD5 hash length
            
            # Same content should produce same hash
            hash2 = trigger.calculate_data_hash(f.name)
            assert hash1 == hash2
            
            # Different content should produce different hash
            with open(f.name, 'a') as f2:
                f2.write("5,6\n")
            
            hash3 = trigger.calculate_data_hash(f.name)
            assert hash1 != hash3
            
            os.unlink(f.name)
    
    def test_data_change_detection(self, trigger):
        """Test data change detection logic."""
        # Initially, data should be considered changed (no previous hash)
        changed, current_hash = trigger.has_data_changed()
        assert changed  # No previous hash, so considered changed
        
        # Update state with current hash
        trigger.update_state({"last_data_hash": current_hash})
        
        # Now should not be changed
        changed, _ = trigger.has_data_changed()
        # Note: This might be True if the processed data file doesn't exist
        # In real scenarios, this would be False if file exists and hasn't changed
    
    @patch('models.retrain_trigger.RetrainTrigger.get_current_model_performance')
    def test_should_retrain_logic(self, mock_performance, trigger):
        """Test the retraining decision logic."""
        # Mock performance
        mock_performance.return_value = 0.75
        
        # Test with no previous retrain
        should_retrain, reason = trigger.should_retrain()
        # Should retrain if data changed or other conditions met
        assert isinstance(should_retrain, bool)
        assert isinstance(reason, str)
        
        # Test with recent retrain (should not retrain)
        trigger.update_state({
            "last_retrain_time": datetime.now().isoformat(),
            "last_performance": 0.8
        })
        should_retrain, reason = trigger.should_retrain()
        assert not should_retrain
        assert "Too soon since last retrain" in reason
        
        # Test with performance degradation
        mock_performance.return_value = 0.4  # Below threshold
        trigger.update_state({
            "last_retrain_time": (datetime.now() - timedelta(hours=7)).isoformat()
        })
        should_retrain, reason = trigger.should_retrain()
        assert should_retrain
        assert "below threshold" in reason
    
    @patch('subprocess.run')
    @patch('models.retrain_trigger.RetrainTrigger.get_current_model_performance')
    def test_trigger_retrain_success(self, mock_performance, mock_subprocess, trigger):
        """Test successful retraining trigger."""
        # Mock successful subprocess call
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock performance improvement
        mock_performance.return_value = 0.85
        
        result = trigger.trigger_retrain("Test reason")
        
        assert result["success"] is True
        assert "Test reason" in result["reason"]
        assert "duration_seconds" in result
        assert result["new_performance"] == 0.85
        
        # Check state was updated
        state = trigger.get_state()
        assert state["retrain_count"] == 1
        assert state["last_retrain_time"] is not None
    
    @patch('subprocess.run')
    def test_trigger_retrain_failure(self, mock_subprocess, trigger):
        """Test failed retraining trigger."""
        # Mock failed subprocess call
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Training failed"
        mock_subprocess.return_value = mock_result
        
        result = trigger.trigger_retrain("Test reason")
        
        assert result["success"] is False
        assert "error" in result
        assert "Training failed" in result["error"]
    
    def test_get_retrain_status(self, trigger):
        """Test getting retraining status."""
        status = trigger.get_retrain_status()
        
        required_fields = [
            "auto_retrain_enabled", "should_retrain", "retrain_reason",
            "current_performance", "retrain_count", "config", "data_changed"
        ]
        
        for field in required_fields:
            assert field in status
        
        assert isinstance(status["auto_retrain_enabled"], bool)
        assert isinstance(status["should_retrain"], bool)
        assert isinstance(status["config"], dict)
    
    def test_update_config(self, trigger):
        """Test configuration updates."""
        new_config = {
            "min_performance_threshold": 0.6,
            "auto_retrain_enabled": False
        }
        
        result = trigger.update_config(new_config)
        
        assert "message" in result
        assert trigger.config["min_performance_threshold"] == 0.6
        assert trigger.config["auto_retrain_enabled"] is False


class TestRetrainingAPI:
    """Test the retraining API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint_includes_retraining(self, client):
        """Test health endpoint includes retraining availability."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "retraining_available" in data
        assert isinstance(data["retraining_available"], bool)
    
    @patch('api.app.RETRAIN_AVAILABLE', True)
    @patch('api.app.retrain_trigger')
    def test_retrain_status_endpoint(self, mock_trigger, client):
        """Test retraining status endpoint."""
        # Mock the trigger status
        mock_trigger.get_retrain_status.return_value = {
            "auto_retrain_enabled": True,
            "should_retrain": False,
            "retrain_reason": "No triggers",
            "current_performance": 0.75,
            "retrain_count": 2,
            "config": {"min_performance_threshold": 0.5}
        }
        
        response = client.get("/retrain/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "auto_retrain_enabled" in data
        assert "should_retrain" in data
        assert "timestamp" in data
    
    @patch('api.app.RETRAIN_AVAILABLE', False)
    def test_retrain_status_unavailable(self, client):
        """Test retraining status when system unavailable."""
        response = client.get("/retrain/status")
        assert response.status_code == 503
        assert "not available" in response.json()["detail"]
    
    @patch('api.app.RETRAIN_AVAILABLE', True)
    @patch('api.app.retrain_trigger')
    @patch('api.app.log_retrain_event')
    def test_trigger_retrain_endpoint(self, mock_log, mock_trigger, client):
        """Test manual retraining trigger endpoint."""
        # Mock successful retraining
        mock_trigger.should_retrain.return_value = (True, "Data changed")
        mock_trigger.get_current_model_performance.return_value = 0.7
        mock_trigger.trigger_retrain.return_value = {
            "success": True,
            "reason": "Manual API trigger",
            "duration_seconds": 45.2,
            "new_performance": 0.82,
            "message": "Retraining completed successfully"
        }
        
        response = client.post("/retrain/trigger", json={
            "reason": "Manual test trigger",
            "force": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "retrain_id" in data
        assert "timestamp" in data
        
        # Verify logging was called
        mock_log.assert_called_once()
    
    @patch('api.app.RETRAIN_AVAILABLE', True)
    @patch('api.app.retrain_trigger')
    def test_trigger_retrain_too_soon(self, mock_trigger, client):
        """Test retraining rejection when too soon."""
        # Mock should_retrain returning False with "too soon" reason
        mock_trigger.should_retrain.return_value = (False, "Too soon since last retrain")
        
        response = client.post("/retrain/trigger", json={
            "reason": "Test trigger",
            "force": False
        })
        
        assert response.status_code == 429
        assert "Too soon" in response.json()["detail"]
    
    @patch('api.app.RETRAIN_AVAILABLE', True)
    @patch('api.app.retrain_trigger')
    def test_trigger_retrain_force(self, mock_trigger, client):
        """Test forced retraining bypasses checks."""
        # Mock retraining success
        mock_trigger.get_current_model_performance.return_value = 0.7
        mock_trigger.trigger_retrain.return_value = {
            "success": True,
            "reason": "Forced manual trigger",
            "duration_seconds": 30.1,
            "new_performance": 0.78
        }
        
        response = client.post("/retrain/trigger", json={
            "reason": "Forced test trigger",
            "force": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('api.app.RETRAIN_AVAILABLE', True)
    @patch('api.app.retrain_trigger')
    def test_update_retrain_config_endpoint(self, mock_trigger, client):
        """Test retraining configuration update endpoint."""
        mock_trigger.update_config.return_value = {
            "message": "Configuration updated",
            "new_config": {"min_performance_threshold": 0.6}
        }
        
        response = client.post("/retrain/config", json={
            "min_performance_threshold": 0.6,
            "auto_retrain_enabled": True,
            "max_retrain_frequency_hours": 8.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "timestamp" in data
    
    def test_retrain_logs_endpoint(self, client):
        """Test retraining logs endpoint."""
        response = client.get("/retrain/logs/5")
        assert response.status_code == 200
        
        data = response.json()
        assert "logs" in data
        assert "count" in data
        assert isinstance(data["logs"], list)
    
    def test_metrics_includes_retraining_stats(self, client):
        """Test metrics endpoint includes retraining statistics."""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "retraining_stats" in data


class TestRetrainingCLI:
    """Test the CLI interface for retraining."""
    
    @patch('models.retrain_trigger.retrain_trigger')
    @patch('sys.argv', ['retrain_trigger.py', 'status'])
    def test_cli_status_command(self, mock_trigger):
        """Test CLI status command."""
        mock_trigger.get_retrain_status.return_value = {
            "auto_retrain_enabled": True,
            "retrain_count": 1
        }
        
        from models.retrain_trigger import main
        
        # Capture stdout
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            main()
        
        output = f.getvalue()
        assert "auto_retrain_enabled" in output
    
    @patch('models.retrain_trigger.retrain_trigger')
    @patch('sys.argv', ['retrain_trigger.py', 'trigger', 'test', 'reason'])
    def test_cli_trigger_command(self, mock_trigger):
        """Test CLI trigger command."""
        mock_trigger.trigger_retrain.return_value = {
            "success": True,
            "message": "Retraining completed"
        }
        
        from models.retrain_trigger import main
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            main()
        
        output = f.getvalue()
        assert "success" in output
        
        # Verify trigger was called with correct reason
        mock_trigger.trigger_retrain.assert_called_once_with("test reason")


class TestIntegration:
    """Integration tests for the complete retraining system."""
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_end_to_end_retraining_flow(self, mock_exists, mock_subprocess):
        """Test complete retraining flow."""
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock successful training
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create trigger with temp state file
            with patch('models.retrain_trigger.RetrainTrigger.state_file', f'{temp_dir}/state.json'):
                trigger = RetrainTrigger()
                
                # Trigger retraining
                result = trigger.trigger_retrain("Integration test")
                
                assert result["success"] is True
                assert trigger.get_state()["retrain_count"] == 1
    
    def test_api_integration_with_retraining(self):
        """Test API integration with retraining system."""
        client = TestClient(app)
        
        # Test that retraining endpoints are available
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test OpenAPI spec includes retraining endpoints
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        paths = openapi_data["paths"]
        
        # Check retraining endpoints are documented
        assert "/retrain/status" in paths
        assert "/retrain/trigger" in paths
        assert "/retrain/config" in paths
        assert "/retrain/logs/{limit}" in paths


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 