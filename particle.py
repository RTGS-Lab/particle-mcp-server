from typing import Any, Dict, List
import httpx
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("particle")

# Constants
PARTICLE_API_BASE = "https://api.particle.io"

# Get access token from environment variables
ACCESS_TOKEN = os.getenv("PARTICLE_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise EnvironmentError("PARTICLE_ACCESS_TOKEN environment variable is not set. Please add it to your .env file.")

# Define a tool to list devices
@mcp.tool("list_devices")
async def list_devices() -> Dict[str, Any]:
    """List all Particle devices in your account."""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        }
        
        response = await client.get(
            f"{PARTICLE_API_BASE}/v1/devices",
            headers=headers
        )
        
        if response.status_code == 200:
            devices = response.json()
            return {"devices": devices}
        else:
            return {
                "error": f"Failed to fetch devices: {response.status_code}",
                "message": response.text
            }

# Start the server when the script is run directly
if __name__ == "__main__":
    mcp.run(transport='stdio')