import subprocess
import threading
import time
import shlex
import logging
from typing import Dict, Any

from .config import ThresholdConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLockManager:
    """
    Manages concurrent test execution to prevent 
    multiple tests from same source simultaneously.
    """
    def __init__(self):
        self.active_sources = set()
        self.lock = threading.Lock()
        
    def acquire_source(self, source_ip: str) -> bool:
        """
        Attempt to acquire exclusive access to a source IP.
        
        :param source_ip: IP address of the source
        :return: True if source can be used, False otherwise
        """
        with self.lock:
            if source_ip in self.active_sources:
                return False
            self.active_sources.add(source_ip)
            return True
    
    def release_source(self, source_ip: str):
        """
        Release exclusive access to a source IP.
        
        :param source_ip: IP address of the source
        """
        with self.lock:
            self.active_sources.discard(source_ip)

class NetworkTester:
    """Performs network performance tests for different network types."""
    def __init__(self, 
                 network_type: str, 
                 source_ip: str, 
                 target_ip: str, 
                 lock_manager: TestLockManager,
                 thresholds: ThresholdConfig):
        self.network_type = network_type
        self.source_ip = source_ip
        self.target_ip = target_ip
        self.lock_manager = lock_manager
        self.thresholds = thresholds
    
    def run_test(self) -> Dict[str, Any]:
        """
        Execute network performance test with error handling.
        
        :return: Test results dictionary
        """
        # Prevent testing same source multiple times
        if not self.lock_manager.acquire_source(self.source_ip):
            logger.warning(f"Source {self.source_ip} is already running tests")
            return {"status": "skipped", "reason": "Source busy"}
        
        try:
            latency = self._measure_latency()
            bandwidth = self._measure_bandwidth()
            
            return {
                "latency": latency,
                "bandwidth": bandwidth,
                "status": "success",
                "meets_thresholds": self._validate_test_results(latency, bandwidth)
            }
        except Exception as e:
            logger.error(f"Test failed for {self.source_ip} -> {self.target_ip}: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
        finally:
            self.lock_manager.release_source(self.source_ip)
    
    def _validate_test_results(self, latency: float, bandwidth: float) -> bool:
        """
        Validate if test results meet performance thresholds.
        
        :param latency: Measured latency
        :param bandwidth: Measured bandwidth
        :return: True if meets thresholds, False otherwise
        """
        bw_threshold = self.thresholds.speed * 0.95
        return (bandwidth >= bw_threshold and 
                latency <= self.thresholds.latency)
    
    def _measure_latency(self) -> float:
        """Measure network latency with retry mechanism."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.network_type == "infiniband":
                    return self._measure_ib_latency()
                return self._measure_eth_latency()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1 * (attempt + 1))  # Exponential backoff
    
    def _measure_bandwidth(self) -> float:
        """Measure network bandwidth with retry mechanism."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.network_type == "infiniband":
                    return self._measure_ib_bandwidth()
                return self._measure_eth_bandwidth()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1 * (attempt + 1))  # Exponential backoff
    
    def _measure_ib_latency(self) -> float:
        """Measure InfiniBand latency."""
        cmd = f"ib_send_lat --bind_source_ip {shlex.quote(self.source_ip)} {shlex.quote(self.target_ip)}"
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30, check=True)
        return float(result.stderr.split('\n')[-2].split()[5])
    
    def _measure_eth_latency(self) -> float:
        """Measure Ethernet latency."""
        server_cmd = f"iperf -s -u -B {shlex.quote(self.target_ip)}"
        client_cmd = f"iperf -c {shlex.quote(self.target_ip)} -u -B {shlex.quote(self.source_ip)} -b 5M -t 1"
        
        with subprocess.Popen(server_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE) as server:
            try:
                result = subprocess.run(client_cmd.split(), capture_output=True, text=True, timeout=30, check=True)
                return float(result.stdout.split('\n')[-2].split()[8])
            finally:
                server.terminate()

    def _measure_ib_bandwidth(self) -> float:
        """Measure InfiniBand bandwidth."""
        cmd = f"ib_send_bw {shlex.quote(self.target_ip)} -D5 --output bandwidth --report_gbits -F"
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30, check=True)
        return float(result.stdout.strip())
    
    def _measure_eth_bandwidth(self) -> float:
        """Measure Ethernet bandwidth."""
        server_cmd = f"iperf -s -u -B {shlex.quote(self.target_ip)}"
        client_cmd = f"iperf -c {shlex.quote(self.target_ip)} -P 32 -t 5 -f g"
        
        with subprocess.Popen(server_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE) as server:
            try:
                result = subprocess.run(client_cmd.split(), capture_output=True, text=True, timeout=30, check=True)
                return float(result.stdout.split('SUM')[1].split()[5])
            finally:
                server.terminate()