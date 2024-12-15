import pytest
from unittest.mock import patch, MagicMock
from src.network_tester import NetworkTester, TestLockManager
from src.config import ThresholdConfig

@pytest.fixture
def test_lock_manager():
    return TestLockManager()

@pytest.fixture
def test_thresholds():
    return ThresholdConfig(
        speed=100,
        speed_units="Gbit/s",
        latency=0.1,
        latency_units="microseconds"
    )

def test_lock_manager(test_lock_manager):
    # Test acquiring and releasing sources
    assert test_lock_manager.acquire_source("192.168.1.1") == True
    assert test_lock_manager.acquire_source("192.168.1.1") == False
    
    test_lock_manager.release_source("192.168.1.1")
    assert test_lock_manager.acquire_source("192.168.1.1") == True

@patch('src.network_tester.NetworkTester._measure_latency')
@patch('src.network_tester.NetworkTester._measure_bandwidth')
def test_network_tester_run_test(mock_bandwidth, mock_latency, test_lock_manager, test_thresholds):
    # Mock measurements
    mock_latency.return_value = 0.05
    mock_bandwidth.return_value = 95

    # Create NetworkTester instance
    tester = NetworkTester(
        network_type="ethernet",
        source_ip="192.168.1.1",
        target_ip="192.168.1.2",
        lock_manager=test_lock_manager,
        thresholds=test_thresholds
    )

    # Run test
    result = tester.run_test()

    # Assertions
    assert result['status'] == 'success'
    assert result['meets_thresholds'] == True
    assert result['latency'] == 0.05
    assert result['bandwidth'] == 95

def test_validate_test_results(test_thresholds):
    # Create a NetworkTester instance
    tester = NetworkTester(
        network_type="ethernet",
        source_ip="192.168.1.1",
        target_ip="192.168.1.2",
        lock_manager=TestLockManager(),
        thresholds=test_thresholds
    )

    # Test meeting thresholds
    assert tester._validate_test_results(0.05, 95) == True

    # Test failing thresholds
    assert tester._validate_test_results(0.2, 80) == False