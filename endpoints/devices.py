from typing import Any, Dict, List, Union
import re

from helpers.api_helpers import make_api_request


async def list_devices() -> Dict[str, Any]:
    """List all Particle devices in your account."""
    return await make_api_request("get", "/v1/devices")


async def list_product_devices(
    product_id: str, page: int = 1, per_page: int = 25
) -> Dict[str, Any]:
    """
    List devices in a specific product.

    Args:
        product_id: The ID of the product
        page: Page number for paginated results (default: 1)
        per_page: Number of devices per page (default: 25)
    """
    params = {"page": page, "per_page": per_page}
    return await make_api_request(
        "get", f"/v1/products/{product_id}/devices", params=params
    )


async def rename_device(device_id: str, name: str) -> Dict[str, Any]:
    """
    Rename a device.

    Args:
        device_id: The ID of the device to rename
        name: The new name for the device
    """
    return await make_api_request(
        "put", f"/v1/devices/{device_id}", json_data={"name": name}
    )


async def add_device_notes(device_id: str, notes: str) -> Dict[str, Any]:
    """
    Add notes to a device.

    Args:
        device_id: The ID of the device
        notes: The notes to add to the device
    """
    return await make_api_request(
        "put", f"/v1/devices/{device_id}", json_data={"notes": notes}
    )


async def ping_device(device_id: str) -> Dict[str, Any]:
    """
    Ping a device to check if it's online.

    Args:
        device_id: The ID of the device to ping
    """
    return await make_api_request("put", f"/v1/devices/{device_id}/ping")


async def call_function(
    device_id: str, function_name: str, argument: str = ""
) -> Dict[str, Any]:
    """
    Call a function on a device.

    Args:
        device_id: The ID of the device
        function_name: The name of the function to call
        argument: Argument to pass to the function (optional)
    """
    return await make_api_request(
        "post", f"/v1/devices/{device_id}/{function_name}", json_data={"arg": argument}
    )


def _fuzzy_match_score(search_terms: str, device_name: str) -> float:
    """
    Calculate a fuzzy match score between search terms and device name.
    
    Args:
        search_terms: The search string (e.g., "device 47 in lccmr project")
        device_name: The actual device name (e.g., "LCCMR_47")
        
    Returns:
        Float score between 0-1, where 1 is perfect match
    """
    search_lower = search_terms.lower()
    name_lower = device_name.lower()
    
    # Extract words from search terms, filtering out common words
    common_words = {'device', 'in', 'project', 'the', 'a', 'an', 'and', 'or', 'of', 'for', 'with'}
    search_words = [word for word in re.findall(r'\w+', search_lower) if word not in common_words]
    
    if not search_words:
        return 0.0
    
    score = 0.0
    max_possible_score = len(search_words)
    
    for word in search_words:
        # Exact word match in device name
        if word in name_lower:
            score += 1.0
        # Partial match (word contains search term or vice versa)
        elif any(word in part or part in word for part in name_lower.split('_')):
            score += 0.7
        # Check if search word is a number and exists in device name
        elif word.isdigit() and word in re.findall(r'\d+', name_lower):
            score += 0.9
    
    # Bonus for exact match
    if search_lower == name_lower:
        score = max_possible_score
    
    # Normalize score
    return min(score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0


async def find_device_by_name(device_name: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Find device(s) by name using fuzzy matching and return their node_ids without fetching all devices.
    
    This function searches for device(s) using fuzzy matching to handle cases like:
    - "device 47 in lccmr project" matches "LCCMR_47"
    - "guadalupe" matches "Guadalupe_Station_01"
    - "lccmr 23" matches "LCCMR_Irrigation_23"
    
    It searches in a paginated way to avoid loading the entire device list into memory.

    Args:
        device_name: The name/description of the device to search for, or a list of device names
        
    Returns:
        Dict containing device information if found, or error if not found.
        For multiple devices, returns a list of results under 'devices' key.
    """
    # Handle both single device name and list of device names
    if isinstance(device_name, str):
        device_names = [device_name]
        return_single = True
    else:
        device_names = device_name
        return_single = False
    
    # Track results for each device name being searched
    search_results = {}
    for name in device_names:
        search_results[name] = {
            "best_match": None,
            "best_score": 0.0,
            "found": False
        }
    
    page = 1
    per_page = 100  # Use larger page size for efficiency
    min_score_threshold = 0.3  # Minimum score to consider a match
    
    while True:
        # Get a page of devices
        params = {"page": page, "per_page": per_page}
        response = await make_api_request("get", "/v1/devices", params=params)
        
        if "error" in response:
            return response
            
        devices = response.get("devices", [])
        
        # If no devices returned, we've reached the end
        if not devices:
            break
            
        # Search for devices in this page using fuzzy matching
        for device in devices:
            device_actual_name = device.get("name", "")
            
            for search_name in device_names:
                # Skip if we already found an exact match for this search name
                if search_results[search_name]["found"] and search_results[search_name]["best_score"] == 1.0:
                    continue
                
                # Try exact match first (case insensitive)
                if device_actual_name.lower() == search_name.lower():
                    search_results[search_name] = {
                        "best_match": device,
                        "best_score": 1.0,
                        "found": True
                    }
                    continue
                
                # Calculate fuzzy match score
                score = _fuzzy_match_score(search_name, device_actual_name)
                
                if score > search_results[search_name]["best_score"] and score >= min_score_threshold:
                    search_results[search_name]["best_score"] = score
                    search_results[search_name]["best_match"] = device
                    search_results[search_name]["found"] = True
        
        # Move to next page
        page += 1
        
        # Safety check to prevent infinite loops
        if page > 1000:  # Arbitrary large number
            break
    
    # Process results
    if return_single:
        # Single device search - return original format
        search_name = device_names[0]
        result = search_results[search_name]
        
        if result["found"] and result["best_score"] >= min_score_threshold:
            return {
                "success": True,
                "device": result["best_match"],
                "node_id": result["best_match"].get("id"),
                "name": result["best_match"].get("name"),
                "online": result["best_match"].get("online"),
                "last_heard": result["best_match"].get("last_heard"),
                "match_score": result["best_score"],
                "match_type": "exact" if result["best_score"] == 1.0 else "fuzzy"
            }
        
        return {
            "error": f"No device found matching '{search_name}' (searched {page - 1} pages)",
            "searched_pages": page - 1,
            "best_score": result["best_score"]
        }
    else:
        # Multiple device search - return list format
        devices_found = []
        devices_not_found = []
        
        for search_name in device_names:
            result = search_results[search_name]
            
            if result["found"] and result["best_score"] >= min_score_threshold:
                devices_found.append({
                    "search_name": search_name,
                    "success": True,
                    "device": result["best_match"],
                    "node_id": result["best_match"].get("id"),
                    "name": result["best_match"].get("name"),
                    "online": result["best_match"].get("online"),
                    "last_heard": result["best_match"].get("last_heard"),
                    "match_score": result["best_score"],
                    "match_type": "exact" if result["best_score"] == 1.0 else "fuzzy"
                })
            else:
                devices_not_found.append({
                    "search_name": search_name,
                    "success": False,
                    "error": f"No device found matching '{search_name}'",
                    "best_score": result["best_score"]
                })
        
        return {
            "success": len(devices_found) > 0,
            "total_searched": len(device_names),
            "found_count": len(devices_found),
            "not_found_count": len(devices_not_found),
            "searched_pages": page - 1,
            "devices": devices_found + devices_not_found
        }
