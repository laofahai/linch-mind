import json
from daemon.services.ipc_protocol import IPCResponse

# 测试成功响应
success_resp = IPCResponse.success_response(data={"test": "value"})
print("成功响应:", json.dumps(success_resp.to_dict(), indent=2))

# 测试错误响应
from daemon.services.ipc_protocol import IPCErrorCode
error_resp = IPCResponse.error_response(IPCErrorCode.AUTH_REQUIRED, "Test error")
print("错误响应:", json.dumps(error_resp.to_dict(), indent=2))

