import pytest
import json
from pathlib import Path
from src.results_manager import ResultsManager
from src.config import ThresholdConfig

@pytest.fixture
def test_thresholds():
    return ThresholdConfig(
        speed=100,
        speed_units="Gbit/s", 
        latency=0.1,
        latency_units="microseconds"
    )

def test_results_manager_init(tmp_path):
    output_path = tmp_path / "test_results.json"
    results_manager = ResultsManager(output_path)

    # Check initial results structure
    assert results_manager.results['datacenter']['ethernet']['type'] == "Gigabit Ethernet"
    assert results_manager.results['connections'] == []

def test_results_manager_add_result(tmp_path, test_thresholds):
    output_path = tmp_path / "test_results.json"
    results_manager = ResultsManager(output_path)

    # Simulate a failed test result
    test_results = {
        'bandwidth': 80,
        'latency': 0.2,
        'meets_thresholds': False,
        'status': 'success'
    }

    # Add the result
    results_manager.add_result(
        source_rack="rack1",
        source_ip="192.168.1.1",
        target_rack="rack2",
        target_ip="192.168.1.2",
        network_type="ethernet",
        test_results=test_results,
        thresholds=test_thresholds
    )

    # Read the output file
    with open(output_path, 'r') as f:
        results = json.load(f)

    # Check the connection was added
    assert len(results['connections']) == 1
    
    connection = results['connections'][0]
    assert connection['rack_1'] == "192.168.1.1"
    assert connection['rack_2'] == "192.168.1.2"
    assert connection['type'] == "ethernet"
    assert connection['BW']['degradation_percentage'] == 20.0