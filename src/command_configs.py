from dataclasses import dataclass

@dataclass
class IperfCommand:
    """Configuration for Iperf commands"""
    ethernet_server: str = "iperf -s -u -B {target_ip}"
    ethernet_client: str = "iperf -c {target_ip} -P 32 -t 5 -f g"
    ethernet_latency_client: str = "iperf -c {target_ip} -u -B {source_ip} -b 5M -t 1"

@dataclass
class InfiniBandCommand:
    """Configuration for InfiniBand-specific commands"""
    latency_cmd: str = "ib_send_lat --bind_source_ip {source_ip} {target_ip}"
    bandwidth_cmd: str = "ib_send_bw {target_ip} -D5 --output bandwidth --report_gbits -F"