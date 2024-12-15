import yaml
from pathlib import Path
from typing import Dict
from dataclasses import dataclass

@dataclass
class ThresholdConfig:
    """Configuration for network performance thresholds."""
    speed: float
    speed_units: str
    latency: float
    latency_units: str

class NetworkConfig:
    """Manages network configuration loading and validation."""
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load and validate configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate basic configuration structure
            if 'datacenter_map' not in config:
                raise ValueError("Invalid configuration: Missing 'datacenter_map'")
            
            return config
        except (IOError, yaml.YAMLError) as e:
            raise ValueError(f"Configuration loading error: {e}")
    
    def get_thresholds(self, network_type: str) -> ThresholdConfig:
        """
        Extract and validate network performance thresholds.
        
        :param network_type: Type of network (ethernet or infiniband)
        :return: ThresholdConfig object
        """
        try:
            network_config = self.config_data['datacenter_map'][network_type]
            thresholds = network_config.get('thresholds', [{}])[0]
            
            # Validate required keys
            if not all(key in thresholds for key in ['bw', 'latency']):
                raise ValueError(f"Invalid threshold configuration for {network_type}")
            
            return ThresholdConfig(
                speed=float(thresholds['bw'][0]['speed']),
                speed_units=thresholds['bw'][1]['units'],
                latency=float(thresholds['latency'][0]['lat']),
                latency_units=thresholds['latency'][1]['units']
            )
        except (KeyError, IndexError, ValueError) as e:
            raise ValueError(f"Configuration parsing error: {e}")

    def load_servers_from_config(self, network_type: str) -> list:
        """
        Load servers from configuration based on network type.
        
        :param network_type: Network type to extract servers for
        :return: List of server configurations
        """
        servers = []
        racks = self.config_data['datacenter_map'][network_type].get('racks', {})
        
        for rack_name, rack_servers in racks.items():
            for server_dict in rack_servers:
                for hostname, ip in server_dict.items():
                    servers.append({
                        'rack': rack_name,
                        'hostname': hostname,
                        'ip': ip
                    })
        
        return servers