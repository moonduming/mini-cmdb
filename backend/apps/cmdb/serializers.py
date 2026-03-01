from rest_framework import serializers
from .models import City, Host, IDC


class CitySerializer(serializers.ModelSerializer):
    """城市序列化器。"""

    class Meta:
        model = City
        fields = [
            "id", "name", "code", "created_at", "updated_at",
        ]


class IDCSerializer(serializers.ModelSerializer):
    """机房序列化器。"""

    # 读时返回城市的基本信息，写时通过 city_id 传入
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source="city",
    )
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = IDC
        fields = [
            "id", "name", "city_id", "city_name", "address",
            "remark", "created_at", "updated_at",
        ]


class HostSerializer(serializers.ModelSerializer):
    """主机序列化器。"""

    city_id = serializers.CharField(source="city.id", read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)

    idc_id = serializers.PrimaryKeyRelatedField(
        queryset=IDC.objects.all(),
        source="idc",
    )
    idc_name = serializers.CharField(source="idc.name", read_only=True)

    class Meta:
        model = Host
        fields = [
            "id", "hostname", "ip", "os_type", "env",
            "is_active", "city_id", "city_name", "idc_id",
            "idc_name", "last_ping_ok", "last_ping_at",
            "remark", "created_at", "updated_at",
        ]
    def validate(self, attrs):
        incoming_city = attrs.get("city")
        incoming_idc = attrs.get("idc")

        effective_idc = incoming_idc or (self.instance.idc if self.instance else None)
        if effective_idc is None:
            return attrs

        if incoming_city is not None and effective_idc.city_id != incoming_city.id:
            raise serializers.ValidationError({"city_id": "city 必须与 idc 所属城市一致"})

        return attrs

    def create(self, validated_data):
        idc = validated_data["idc"]
        validated_data["city"] = idc.city
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 若更新了 idc，则 city 强制同步为新 idc.city
        if "idc" in validated_data and validated_data["idc"] is not None:
            validated_data["city"] = validated_data["idc"].city
        return super().update(instance, validated_data)