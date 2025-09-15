from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from .models import Aoi, EncroachmentDetection
from .serializers import AoiSerializer, EncroachmentDetectionSerializer
from .filters import AoiFilter, EncroachmentDetectionFilter


class AoiViewSet(viewsets.ModelViewSet):
    serializer_class = AoiSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AoiFilter
    
    def get_queryset(self):
        return Aoi.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def cart(self):
        """Get AOIs in cart (unpaid AOIs)"""
        unpaid_aois = self.get_queryset().filter(is_paid=False)
        serializer = self.get_serializer(unpaid_aois, many=True)
        return Response({
            'count': unpaid_aois.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate monitoring for a paid AOI"""
        aoi = self.get_object()
        if not aoi.is_paid:
            return Response(
                {'error': 'AOI must be paid before activation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        aoi.activate_monitoring()
        serializer = self.get_serializer(aoi)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find AOIs near a given point"""
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        radius = request.query_params.get('radius', 1000)  # meters
        
        if not lat or not lon:
            return Response(
                {'error': 'lat and lon parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            point = Point(float(lon), float(lat), srid=4326)
            nearby_aois = self.get_queryset().filter(
                geometry__distance_lte=(point, D(m=float(radius)))
            )
            serializer = self.get_serializer(nearby_aois, many=True)
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinates or radius'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EncroachmentDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EncroachmentDetectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EncroachmentDetectionFilter
    
    def get_queryset(self):
        return EncroachmentDetection.objects.filter(aoi__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an encroachment detection"""
        encroachment = self.get_object()
        encroachment.is_confirmed = True
        encroachment.confirmed_at = timezone.now()
        encroachment.save()
        
        serializer = self.get_serializer(encroachment)
        return Response(serializer.data)