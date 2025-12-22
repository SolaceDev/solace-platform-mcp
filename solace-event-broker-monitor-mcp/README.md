# Solace Event Broker Monitor MCP Server

The Solace Event Broker Monitor MCP (Model Context Protocol) Server provides comprehensive monitoring capabilities for Solace event brokers through the SEMPv2 API. This integration enables developers to monitor broker health, message VPNs, queues, clients, and event mesh connectivity directly from AI-assisted IDEs like Claude Code and Cline.

With this MCP server, you can seamlessly query broker statistics, inspect queue depths, monitor client connections, and analyze event mesh bridges—all through natural language conversations in your development environment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Recommended: No installation needed](#recommended-no-installation-needed)
  - [Alternative: Pre-install with pip](#alternative-pre-install-with-pip)
- [Configuration](#configuration)
- [Environment Variables](#environment-variables)
- [Available Tools](#available-tools)
  - [Example Usage](#example-usage)
- [Troubleshooting](#troubleshooting)
  - [Verify your setup is working](#verify-your-setup-is-working)
  - [Common Issues](#common-issues)
- [Development](#development)
  - [Running Tests](#running-tests)
  - [Manual Testing](#manual-testing)

## Prerequisites

- **Python 3.10+** - Required to run the MCP server (includes `pip3`)
- **[uv](https://docs.astral.sh/uv/)** - Required if using `uvx` in your MCP client configuration (recommended). Not needed if using pip installation method.
- **MCP Client** - Such as [Claude Desktop](https://claude.ai/download) or [Cline](https://github.com/cline/cline)
- **Solace Broker** - Access to a Solace event broker with SEMPv2 enabled

## Quick Start

1. **Ensure you have SEMPv2 access** to your Solace broker with a username and password.

2. **Add to your MCP client configuration** (e.g., Claude Desktop, Cline):

```json
{
  "mcpServers": {
    "solace-event-broker-monitor": {
      "command": "uvx",
      "args": [
        "--from",
        "solace-event-broker-monitor-mcp",
        "solace-broker-monitor-mcp"
      ],
      "env": {
        "SOLACE_SEMP_BASE_URL": "http://localhost:8080/SEMP/v2/monitor",
        "SOLACE_SEMP_USERNAME": "admin",
        "SOLACE_SEMP_PASSWORD": "admin"
      }
    }
  }
}
```

3. **Restart your MCP client** and start monitoring your broker.

**Example prompts:**
- "What is the health status of my broker?"
- "List all message VPNs on my broker"
- "Show me queue statistics for queue ABC in VPN default"
- "What clients are connected to VPN default?"
- "Show me subscriptions for client XYZ"

## Usage Guidelines

This MCP server is intended for use with AI assistants (such as Claude Desktop or Cline) in a controlled environment with human oversight. It is not designed for automated workflows like GitHub Actions or unattended automation systems.

When using this tool, ensure proper security practices for your broker credentials. Use read-only SEMPv2 accounts when possible and follow your organization's security policies.

## Installation

### Recommended: No installation needed

If you use `uvx` in your MCP client configuration (as shown in Quick Start), the package will be automatically downloaded and updated when your client starts. No manual installation is required.

### Alternative: Install with pip

```bash
# Install from Git
pip install git+https://github.com/SolaceLabs/solace-platform-mcp.git#subdirectory=solace-event-broker-monitor-mcp
```

If you pre-install with pip, update your MCP client configuration to use:
```json
{
  "mcpServers": {
    "solace-event-broker-monitor": {
      "command": "solace-broker-monitor-mcp",
      "env": {
        "SOLACE_SEMP_BASE_URL": "http://localhost:8080/SEMP/v2/monitor",
        "SOLACE_SEMP_USERNAME": "admin",
        "SOLACE_SEMP_PASSWORD": "admin"
      }
    }
  }
}
```

## Configuration

The server connects to your Solace broker using SEMPv2 Basic Authentication. Configure the connection using environment variables in your MCP client configuration.

**Example configuration for local broker:**
```json
{
  "mcpServers": {
    "solace-event-broker-monitor": {
      "command": "uvx",
      "args": [
        "--from",
        "solace-event-broker-monitor-mcp",
        "solace-broker-monitor-mcp"
      ],
      "env": {
        "SOLACE_SEMP_BASE_URL": "http://localhost:8080/SEMP/v2/monitor",
        "SOLACE_SEMP_USERNAME": "admin",
        "SOLACE_SEMP_PASSWORD": "admin"
      }
    }
  }
}
```

**Example configuration for Solace Cloud broker:**
```json
{
  "mcpServers": {
    "solace-event-broker-monitor": {
      "command": "uvx",
      "args": [
        "--from",
        "solace-event-broker-monitor-mcp",
        "solace-broker-monitor-mcp"
      ],
      "env": {
        "SOLACE_SEMP_BASE_URL": "https://mr-xxxxx.messaging.solace.cloud:943/SEMP/v2/monitor",
        "SOLACE_SEMP_USERNAME": "your-username",
        "SOLACE_SEMP_PASSWORD": "your-password"
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SOLACE_SEMP_BASE_URL` | No | `http://localhost:8080/SEMP/v2/monitor` | Base URL for the Solace SEMPv2 Monitor API |
| `SOLACE_SEMP_USERNAME` | Yes | - | Username for SEMPv2 Basic Authentication |
| `SOLACE_SEMP_PASSWORD` | Yes | - | Password for SEMPv2 Basic Authentication |

See [Solace SEMPv2 Documentation](https://docs.solace.com/Admin/SEMP/Using-SEMP.htm) for details on SEMPv2 access.

## Available Tools

This server provides comprehensive monitoring capabilities for Solace event brokers:

### Broker Monitoring
- **Broker information** - Get broker health, version, uptime, and redundancy status

### Message VPN Monitoring
- **List VPNs** - Get all message VPNs on the broker
- **VPN details** - Get detailed statistics for a specific VPN

### Queue Monitoring
- **List queues** - Get all queues in a VPN
- **Queue statistics** - Get queue depth, message rates, consumer counts, and more
- **Queue subscriptions** - View topic subscriptions for a queue

### Client Monitoring
- **List clients** - Get all connected clients in a VPN
- **Client details** - Get connection details and statistics for a client
- **Client connections** - View TCP connection information
- **Client subscriptions** - List all topic subscriptions for a client

### Example Usage

Use your AI assistant to:
- "List all message VPNs on my broker"
- "Show queue statistics for queue orders in VPN production"
- "What clients are connected to VPN default?"
- "Show me the subscriptions on queue inventory-updates"
- "What is the health status of my broker?"
- "Show details for client ABC in VPN default"

## Troubleshooting

### Verify your setup is working

After configuring your MCP client, verify the connection:

1. **Restart your MCP client** (e.g., Claude Desktop, Cline)
2. **Ask a simple question** like: "What is my broker's version?"
3. If it works, you'll see results from your Solace broker

### Common Issues

**"SOLACE_SEMP_USERNAME and SOLACE_SEMP_PASSWORD environment variables must be set" error:**
- Ensure both `SOLACE_SEMP_USERNAME` and `SOLACE_SEMP_PASSWORD` are set correctly in your MCP client configuration
- Check for typos in the environment variable names

**"Connection refused" or timeout errors:**
- Verify `SOLACE_SEMP_BASE_URL` is correct and includes `/SEMP/v2/monitor`
- Ensure your broker is running and SEMPv2 is enabled
- Check network connectivity to the broker
- For Solace Cloud brokers, ensure you're using HTTPS and the correct port (typically 943)

**Authentication errors:**
- Verify your username and password are correct
- Ensure the user has appropriate SEMPv2 read permissions
- For Solace Cloud, use your Management Username and Password (not API token)

**"Command not found" errors:**
- Verify you have the [prerequisites](#prerequisites) installed
- If using pip install, run `which solace-broker-monitor-mcp` to verify installation

## Development

This project uses [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management.

```bash
# Clone repo
git clone https://github.com/SolaceLabs/solace-platform-mcp.git
cd solace-platform-mcp/solace-event-broker-monitor-mcp

# Install dependencies
uv sync

# Install in editable mode
uv pip install -e .

# Make changes, test immediately (no rebuild needed)
```

### Running Tests

```bash
# Install development dependencies
uv sync --extra dev

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=solace_event_broker_monitor_mcp --cov-report=term-missing
```

### Manual Testing

```bash
# Verify installation
which solace-broker-monitor-mcp

# Test server starts (will wait for MCP protocol input on stdin)
export SOLACE_SEMP_BASE_URL="http://localhost:8080/SEMP/v2/monitor"
export SOLACE_SEMP_USERNAME="admin"
export SOLACE_SEMP_PASSWORD="admin"
solace-broker-monitor-mcp
# Press Ctrl+C to exit
```

**Testing with a local broker:**
```bash
# Run a Solace broker with Docker
docker run -d -p 8080:8080 -p 55555:55555 \
  --shm-size=2g \
  --env username_admin_globalaccesslevel=admin \
  --env username_admin_password=admin \
  --name=solace solace/solace-pubsub-standard

# Wait for broker to start (check logs)
docker logs -f solace

# Access SEMPv2 at http://localhost:8080/SEMP/v2/monitor
# Username: admin, Password: admin
```
