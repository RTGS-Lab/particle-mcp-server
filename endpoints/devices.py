from typing import Any, Dict
from helpers.api_helpers import make_api_request

async def list_devices() -> Dict[str, Any]:
    """List all Particle devices in your account."""
    return await make_api_request("get", "/v1/devices")

async def list_product_devices(product_id: str, page: int = 1, per_page: int = 25) -> Dict[str, Any]:
    """
    List devices in a specific product.
    
    Args:
        product_id: The ID of the product
        page: Page number for paginated results (default: 1)
        per_page: Number of devices per page (default: 25)
    """
    params = {
        "page": page,
        "per_page": per_page
    }
    return await make_api_request("get", f"/v1/products/{product_id}/devices", params=params)

async def rename_device(device_id: str, name: str) -> Dict[str, Any]:
    """
    Rename a device.
    
    Args:
        device_id: The ID of the device to rename
        name: The new name for the device
    """
    return await make_api_request("put", f"/v1/devices/{device_id}", json_data={"name": name})

async def add_device_notes(device_id: str, notes: str) -> Dict[str, Any]:
    """
    Add notes to a device.
    
    Args:
        device_id: The ID of the device
        notes: The notes to add to the device
    """
    return await make_api_request("put", f"/v1/devices/{device_id}", json_data={"notes": notes})

async def ping_device(device_id: str) -> Dict[str, Any]:
    """
    Ping a device to check if it's online.
    
    Args:
        device_id: The ID of the device to ping
    """
    return await make_api_request("put", f"/v1/devices/{device_id}/ping")
