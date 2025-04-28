[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Particle MCP Server

A Model Context Protocol server for the Particle IoT platform that enables AI assistants to manage Particle devices using natural language.

## Features/API Endpoints Covered

### Devices
- listDevices - lists all devices in your account

### Diagnostics
- getLastKnownVitals - gets the last known vitals from a specific device

### Organizations
- listOrganizations - lists all organizations apart of your account
- listOrganizationProducts - lists all prodcuts within an organization

### Product Firmware
- listProductFirmware - lists all firmware versions for a specific product id

## Setup and Installation

create a .env file with the sctructure shown

```
# Particle API credentials
PARTICLE_ACCESS_TOKEN = your_api_token
```

to generate a particle api token, make sure the Particle CLI is installed and do this command:

```
particle token create
```

## Usage

Clone this repo

Open Claude Desktop

Navigate to Settings

Click Developer

Click Edit Config

Paste this in:
```
{
    "mcpServers": {
        "particle": {
            "command": "uv",
            "args": [
                "--directory",
                "DIRECT/PATH/TO/particle-mcp-server",
                "run",
                "particle.py"
            ]
        }
    }
}
```

## Contributing

https://docs.particle.io/reference/cloud-apis/api/#postman

Follow along to set up the Particle API environment in Postman, and implement a tool for each API endpoint. Open a PR with your changes for review! Please keep PRs "small"
