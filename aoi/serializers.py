from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Aoi, EncroachmentDetection


class AoiSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Aoi
        geo_field = "geometry"
        fields = [
            "id",
            "name",
            "geometry",
            "monitoring_type",
            "status",
            "created_at",
            "updated_at",
            "start_date",
            "end_date",
            "is_paid",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "start_date",
            "end_date",
            "is_paid",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class EncroachmentDetectionSerializer(GeoFeatureModelSerializer):
    aoi_name = serializers.CharField(source="aoi.name", read_only=True)

    class Meta:
        model = EncroachmentDetection
        geo_field = "affected_area"
        fields = [
            "id",
            "aoi",
            "aoi_name",
            "detected_at",
            "severity",
            "affected_area",
            "confidence_score",
            "description",
            "satellite_image_url",
            "is_confirmed",
            "confirmed_at",
        ]
        read_only_fields = ["id", "detected_at", "confirmed_at"]
