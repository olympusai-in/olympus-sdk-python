# Olympus Python SDK

Official Python SDK for [Olympus](https://olympusai.in) — AI-powered log analysis and debugging platform.

## Installation

```bash
pip install olympus-sdk
```

## Quick Start

```python
from olympus import Olympus

with Olympus(api_key='ol_your_key_here', service='payment-svc') as client:
    client.info('Payment processed — $14.99')
    client.warn('Retry attempt 2/3')
    client.error('Connection timeout after 30s')
    client.debug('Query executed in 42ms')
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | str | required | Your Olympus API key (`ol_...`) |
| `service` | str | required | Service name for log grouping |
| `endpoint` | str | `https://api.olympusai.in` | Olympus server URL |
| `flush_interval` | float | `10.0` | Seconds between auto-flushes |
| `batch_size` | int | `100` | Max logs per flush |

## Features

- Buffers logs in memory, flushes in batches
- Auto-flushes every 10s (configurable)
- Auto-flushes when buffer hits batch size
- Retries on failure (puts logs back in buffer)
- Context manager support (`with` statement)
- Zero dependencies (stdlib only)
