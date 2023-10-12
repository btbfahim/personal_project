from rest_framework.response import Response
from enum import Enum

class ResponseCodes(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
def create_response(status: int, code, success: bool, data: any, error_code, error: any):
    response = {
        "status": status,
        "response_code": code,
        "success": success,
        "data": data,
        "error_code": error_code,
        "error": error
    }

    return Response(response, status=status, headers={'Access-Control-Allow-Origin': '*'})