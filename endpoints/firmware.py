from typing import Any, Dict
from helpers.api_helpers import make_api_request

async def call_function(device_id: str, function_name: str, argument: str = "") -> Dict[str, Any]:
    """
    Call a function on a device.
    
    Args:
        device_id: The ID of the device
        function_name: The name of the function to call
        argument: Argument to pass to the function (optional)
    """
    return await make_api_request("post", f"/v1/devices/{device_id}/{function_name}", 
                                 json_data={"arg": argument})