from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Import all endpoint modules
from endpoints import devices, diagnostics, organizations, product_firmware

# Initialize FastMCP server
mcp = FastMCP("particle")


# -----------------
# DEVICE ENDPOINTS
# -----------------
@mcp.tool("list_devices")
async def list_devices() -> Dict[str, Any]:
    """List all Particle devices in your account.

    This function will return a comphrehensive list of every device within
    the Particle organization. This should be used near the begining of an interaction
    especially when a user is asking about an unknown name. Each device has a name and a node_id
    which can be accessed with this tool, and other tools require the node_id to be used rather
    than the name.

    """
    return await devices.list_devices()


@mcp.tool("list_product_devices")
async def list_product_devices(
    product_id: str, page: int = 1, per_page: int = 25
) -> Dict[str, Any]:
    """
    List devices in a specific product. A product in the particle ecosystem
    corresponds to a specific project within the organization, and will usually match a project
    within a database for the data the device provides.

    Args:
        product_id: The ID of the product
        page: Page number for paginated results (default: 1)
        per_page: Number of devices per page (default: 25)
    """
    return await devices.list_product_devices(product_id, page, per_page)


@mcp.tool("rename_device")
async def rename_device(device_id: str, name: str) -> Dict[str, Any]:
    """Rename a device.
    This only affects the name and not the node-id. This should only be used if explicilty asked for
    """
    return await devices.rename_device(device_id, name)


@mcp.tool("add_device_notes")
async def add_device_notes(device_id: str, notes: str) -> Dict[str, Any]:
    """Add notes to a device."""
    return await devices.add_device_notes(device_id, notes)


@mcp.tool("ping_device")
async def ping_device(device_id: str) -> Dict[str, Any]:
    """Ping a device to check if it's online. This sould only ever be called if specifically asked for."""
    return await diagnostics.ping_device(device_id)


@mcp.tool("call_function")
async def call_function(
    device_id: str, function_name: str, argument: str = ""
) -> Dict[str, Any]:
    """
    Call a function on a device. This should only be used when a specific function needs to be called and explicitly asked for,
    otherwise it should never be used as it may be dangerous.

    Args:
        device_id: The ID of the device
        function_name: The name of the function to call
        argument: Argument to pass to the function (optional)
    """
    return await devices.call_function(device_id, function_name, argument)


@mcp.tool("find_device_by_name")
async def find_device_by_name(device_name: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Find device(s) by name using fuzzy matching and return their node_ids without fetching all devices.
    
    This function efficiently searches for device(s) using fuzzy matching to handle natural language
    queries like "device 47 in lccmr project" → "LCCMR_47" or "guadalupe" → "Guadalupe_Station_01".
    Uses pagination to avoid loading the entire device list into memory. Use this instead of
    list_devices when you need to find specific device node_ids.

    Args:
        device_name: The name/description of the device to search for, or a list of device names (supports fuzzy matching)
        
    Returns:
        Dict containing device information including node_id, match_score, and match_type if found.
        For multiple devices, returns a list of results under 'devices' key.
    """
    return await devices.find_device_by_name(device_name)


# -----------------
# DIAGNOSTIC ENDPOINTS
# -----------------


@mcp.tool("get_device_vitals")
async def get_device_vitals(device_id: str) -> Dict[str, Any]:
    """Get the last known vitals for a device.
    This doesn't connect to the device and should be used in place of ping device most of the time
    """
    return await diagnostics.get_device_vitals(device_id)


# -----------------
# ORGANIZATION ENDPOINTS
# -----------------
@mcp.tool("list_organizations")
async def list_organizations() -> Dict[str, Any]:
    """List all organizations the user has access to."""
    return await organizations.list_organizations()


@mcp.tool("list_organization_products")
async def list_organization_products(org_id: str) -> Dict[str, Any]:
    """List products within an organization.
    Products in the Particle ecosystem are projects, and usually correspond to a project in a database
    where the data from devices is located."""
    return await organizations.list_organization_products(org_id)


# -----------------
# PRODUCT FIRMWARE ENDPOINTS
# -----------------
@mcp.tool("list_product_firmware")
async def list_product_firmware(
    product_id: str, page: int = 1, per_page: int = 25
) -> Dict[str, Any]:
    """
    List all firmware versions for a specific product.

    Args:
        product_id: The ID of the product
        page: Page number for paginated results (default: 1)
        per_page: Number of firmware versions per page (default: 25)
    """
    return await product_firmware.list_product_firmware(product_id, page, per_page)


# Start the server when the script is run directly
if __name__ == "__main__":
    mcp.run(transport="stdio")
