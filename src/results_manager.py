import json
import time
from pathlib import Path
from typing import Dict
from filelock import FileLock

from .config import ThresholdConfig

class ResultsManager:
    """Manages and logs network performance test results."""
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.lock = FileLock(f"{output_path}.lock")
        self.results = self._init_results()
    
    def _init_results(self) -> Dict:
        """Initialize results structure."""
        return {
            "datacenter": {
                "ethernet": {"type": "Gigabit Ethernet", "version": "v2.0"},
                "infiniband": {"type": "InfiniBand", "version": "v4.0"}
            },
            "connections": []
        }
        
    def add_result(self, 
                   source_rack: str, 
                   source_ip: str, 
                   target_rack: str, 
                   target_ip: str, 
                   network_type: str, 
                   test_results: Dict,
                   thresholds: ThresholdConfig):
        """
        Add performance test results, focusing on problematic connections.
        
        :param source_rack: Source rack identifier
        :param source_ip: Source IP address
        :param target_rack: Target rack identifier
        :param target_ip: Target IP address
        :param network_type: Network type (ethernet/infiniband)
        :param test_results: Test performance results
        :param thresholds: Performance thresholds
        """
        with self.lock:
            try:
                with open(self.output_path, 'r') as f:
                    current_results = json.load(f)
            except FileNotFoundError:
                current_results = self._init_results()
            
            # Only log problematic connections
            if not test_results.get('meets_thresholds', True):
                connection_result = {
                    "rack_1": source_ip,
                    "rack_2": target_ip,
                    "type": network_type,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                connection_result.update({
                    "BW": {
                        "expected_speed": thresholds.speed,
                        "actual_speed": test_results.get('bandwidth', 0),
                        "units": thresholds.speed_units,
                        "degradation_percentage": 
                            ((thresholds.speed - test_results.get('bandwidth', 0)) / thresholds.speed) * 100
                    },
                    "latency": {
                        "lat": test_results.get('latency', 0),
                        "units": thresholds.latency_units
                    }
                })
                
                current_results["connections"].append(connection_result)
            
            with open(self.output_path, 'w') as f:
                json.dump(current_results, f, indent=2)