from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MonitoringJob, SatelliteImage
from .serializers import MonitoringJobSerializer, SatelliteImageSerializer
from .tasks import monitor_aoi_task


class MonitoringJobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MonitoringJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "aoi"]

    def get_queryset(self):
        return MonitoringJob.objects.filter(aoi__user=self.request.user)

    @action(detail=False, methods=["post"])
    def trigger_monitoring(self, request):
        """Manually trigger monitoring for user's AOIs"""
        aoi_id = request.data.get("aoi_id")

        if not aoi_id:
            return Response(
                {"error": "aoi_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify user owns the AOI
            aoi = request.user.aois.get(id=aoi_id, status="active", is_paid=True)

            # Check for existing running job
            existing_job = aoi.monitoring_jobs.filter(
                status__in=["pending", "running"]
            ).exists()

            if existing_job:
                return Response(
                    {"error": "Monitoring job already running for this AOI"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Trigger monitoring task
            task = monitor_aoi_task.delay(str(aoi.id))

            return Response({"message": "Monitoring job started", "task_id": task.id})

        except Aoi.DoesNotExist:
            return Response(
                {"error": "AOI not found or not eligible for monitoring"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SatelliteImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SatelliteImage.objects.all()
    serializer_class = SatelliteImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["satellite"]
