"""HTTP客户端模块，提供API请求功能."""

from __future__ import annotations

import json
from typing import Any
from typing import Dict
from typing import Optional

import httpx
from nicegui import ui


class ApiResponse:
    """API响应包装器."""

    def __init__(self, response: httpx.Response) -> None:
        """初始化API响应.

        Args:
            response: httpx响应对象
        """
        self._response = response
        self.status_code = response.status_code
        self.headers = response.headers

    async def json(self) -> Dict[str, Any]:
        """获取响应的JSON内容.

        Returns:
            Dict[str, Any]: JSON数据

        Raises:
            json.JSONDecodeError: 响应解析失败
        """
        try:
            return self._response.json()
        except json.JSONDecodeError as e:
            ui.notify(f"响应解析失败: {e!s}", type="negative")
            raise

    async def text(self) -> str:
        """获取响应的文本内容.

        Returns:
            str: 文本内容
        """
        return self._response.text

    def is_success(self) -> bool:
        """检查响应是否成功.

        Returns:
            bool: 响应是否成功
        """
        return httpx.codes.OK <= self.status_code < httpx.codes.MULTIPLE_CHOICES


class HttpClient:
    """HTTP客户端, 封装了常用的API请求方法."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """初始化HTTP客户端.

        Args:
            base_url: API基础URL
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        """发送HTTP请求.

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            endpoint: API端点路径
            params: URL查询参数
            data: 请求体数据
            headers: 请求头

        Returns:
            ApiResponse: API响应包装器

        Raises:
            httpx.RequestError: 请求失败
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = headers or {}
        headers.update({"Content-Type": "application/json"})

        try:
            response = await self.client.request(
                method=method.upper(),
                url=url,
                params=params,
                json=data,
                headers=headers,
            )
            return ApiResponse(response)
        except httpx.RequestError as e:
            ui.notify(f"请求失败: {e!s}", type="negative")
            raise

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        """发送GET请求.

        Args:
            endpoint: API端点路径
            params: URL查询参数
            headers: 请求头

        Returns:
            ApiResponse: API响应包装器
        """
        return await self.request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        """发送POST请求.

        Args:
            endpoint: API端点路径
            data: 请求体数据
            params: URL查询参数
            headers: 请求头

        Returns:
            ApiResponse: API响应包装器
        """
        return await self.request("POST", endpoint, params=params, data=data, headers=headers)

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        """发送PUT请求.

        Args:
            endpoint: API端点路径
            data: 请求体数据
            params: URL查询参数
            headers: 请求头

        Returns:
            ApiResponse: API响应包装器
        """
        return await self.request("PUT", endpoint, params=params, data=data, headers=headers)

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ApiResponse:
        """发送DELETE请求.

        Args:
            endpoint: API端点路径
            params: URL查询参数
            headers: 请求头

        Returns:
            ApiResponse: API响应包装器
        """
        return await self.request("DELETE", endpoint, params=params, headers=headers)

    async def close(self) -> None:
        """关闭HTTP客户端."""
        await self.client.aclose()


# 创建默认HTTP客户端实例
default_client = HttpClient()


async def fetch(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> ApiResponse:
    """发送HTTP请求的便捷函数.

    Args:
        endpoint: API端点路径
        method: HTTP方法 (默认为GET)
        data: 请求体数据
        params: URL查询参数
        headers: 请求头

    Returns:
        ApiResponse: API响应包装器
    """
    return await default_client.request(method, endpoint, params=params, data=data, headers=headers)
