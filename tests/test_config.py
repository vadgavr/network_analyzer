import pytest
from pathlib import Path
from src.config import NetworkConfig

def test_config_loading(tmp_path):
    # Create a temporary config file
    config_file = tmp_path / "test_config.yaml"
    config_content = """
    datacenter_map:
      ethernet:
        type: "Test Ethernet"
        version: "v1.0"
        racks:
          rack_1:
            - host1: "192.168.1.1"
        thresholds:
          - bw:
              - speed: 100
              - units: "Gbit/s"
            latency:
              - lat: 0.1
              - units: "microseconds"
    """
    config_file.write_text(config_content)

    # Load the config
    config = NetworkConfig(config_file)
    
    # Check basic config structure
    assert config.config_data is not None
    assert 'datacenter_map' in config.config_data

def test_get_thresholds():
    # Create a temporary config file
    tmp_path = Path("/tmp")
    config_file = tmp_path / "test_config.yaml"
    config_content = """
    datacenter_map:
      ethernet:
        type: "Test Ethernet"
        version: "v1.0"
        thresholds:
          - bw:
              - speed: 100
              - units: "Gbit/s"
            latency:
              - lat: 0.1
              - units: "microseconds"
    """
    config_file.write_text(config_content)

    # Load the config
    config = NetworkConfig(config_file)
    
    # Test threshold extraction
    thresholds = config.get_thresholds('ethernet')
    assert thresholds.speed == 100
    assert thresholds.speed_units == "Gbit/s"
    assert thresholds.latency == 0.1
    assert thresholds.latency_units == "microseconds"

def test_invalid_config():
    # Create a temporary config file
    tmp_path = Path("/tmp")
    config_file = tmp_path / "invalid_config.yaml"
    config_content = "{}"
    config_file.write_text(config_content)

    # Expect a ValueError
    with pytest.raises(ValueError):
        NetworkConfig(config_file)