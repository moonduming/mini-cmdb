from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import City, Host, IDC
from .serializers import CitySerializer, HostSerializer, IDCSerializer



class CityViewSet(viewsets.ModelViewSet):
    """城市：增删改查。"""

    queryset = City.objects.all().order_by("id")
    serializer_class = CitySerializer

    # 轻量的检索/排序能力（不依赖 django-filter）
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["id", "name", "code", "created_at", "updated_at"]
    ordering = ["id"]


class IDCViewSet(viewsets.ModelViewSet):
    """机房：增删改查。"""

    queryset = IDC.objects.select_related("city").all().order_by("id")
    serializer_class = IDCSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "address", "remark", "city__name", "city__code"]
    ordering_fields = ["id", "name", "city", "created_at", "updated_at"]
    ordering = ["id"]


class HostViewSet(viewsets.ModelViewSet):
    """主机：增删改查。"""

    queryset = Host.objects.select_related("city", "idc").all().order_by("id")
    serializer_class = HostSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "hostname",
        "ip",
        "remark",
        "city__name",
        "city__code",
        "idc__name",
    ]
    ordering_fields = [
        "id",
        "hostname",
        "ip",
        "city",
        "idc",
        "is_active",
        "last_ping_ok",
        "last_ping_at",
        "created_at",
        "updated_at",
    ]
    ordering = ["id"]

    def get_queryset(self):
        """支持简单 query params 过滤：city_id / idc_id / is_active。"""
        qs = super().get_queryset()

        city_id = self.request.query_params.get("city_id")
        if city_id:
            qs = qs.filter(city_id=city_id)

        idc_id = self.request.query_params.get("idc_id")
        if idc_id:
            qs = qs.filter(idc_id=idc_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None and is_active != "":
            # 允许: true/false/1/0
            v = str(is_active).strip().lower()
            if v in {"1", "true", "yes", "y"}:
                qs = qs.filter(is_active=True)
            elif v in {"0", "false", "no", "n"}:
                qs = qs.filter(is_active=False)

        return qs
