import logging
import time
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class CountDataPagination(PageNumberPagination):
    """
    统一分页返回格式:
    {
      "count": <总数>,
      "data": [ ... ]
    }
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "data": data,
        })


class MessageDataJSONRenderer(JSONRenderer):
    """
    统一响应格式：
    - 分页：{count, data}
    - 其他成功：{message: "ok", data: ...}
    - 错误：{message: "error", data: 原错误结构}
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = getattr(response, "status_code", 200)

        # DRF 原生分页结构
        if isinstance(data, dict) and {"count", "results"}.issubset(data.keys()):
            data = {"count": data.get("count", 0), "data": data.get("results", [])}
            return super().render(data, accepted_media_type, renderer_context)

        if status_code >= 400:
            wrapped = {"message": "error", "data": data}
            return super().render(wrapped, accepted_media_type, renderer_context)

        # 非分页成功响应统一
        wrapped = {"message": "ok", "data": data}
        return super().render(wrapped, accepted_media_type, renderer_context)


class RequestTimingMiddleware:
    """
    统计每个请求耗时并写入日志。
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("request.timing")

    def __call__(self, request):
        start = time.perf_counter()
        response = None
        try:
            response = self.get_response(request)
            return response
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status_code = getattr(response, "status_code", None)
            self.logger.info(
                "request_timing method=%s path=%s status=%s cost_ms=%.2f",
                request.method,
                request.get_full_path(),
                status_code,
                elapsed_ms,
            )
