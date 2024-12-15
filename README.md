# Network Performance Testing Tool

## Overview
A comprehensive network performance testing utility designed to measure and analyze network performance across different network types (Ethernet and InfiniBand) in datacenter environments.

## Features
- Concurrent network performance testing
- Support for Ethernet and InfiniBand networks
- Configurable performance thresholds
- Detailed result logging
- Thread-safe test execution

## Prerequisites
- Python 3.11+
- `iperf` installed
- `ib_send_lat` and `ib_send_bw` for InfiniBand testing (optional)

## Installation
1. Clone the repository
2. Create a virtual environment
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Edit `network_config.yaml` to define:
- Datacenter network topology
- Server IP addresses
- Performance thresholds

## Usage
```bash
python -m src.main --config network_config.yaml --output test_results.json
```

### Command Line Arguments
- `--config`: Path to network configuration file
- `--output`: Output results file path
- `--max-workers`: Maximum concurrent test workers

## Running Tests
```bash
pytest tests/
```

## License
[Insert your license here]

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request