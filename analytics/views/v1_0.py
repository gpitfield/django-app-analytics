from django.conf import settings
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from analytics.tasks import Analytic, log_analytic

class AnalyticsViewSet(viewsets.ViewSet):
    """
    Record analytics event.\n
    ---
    create:
        omit_serializer: true
        parameters_strategy: replace
        parameters:
            - name: Device-ID
              type: text
              required: false
              paramType: header
            - name: event
              type: text
              required: true
            - name: platform
              type: text
              required: false
              description: iOS, Android
            - name: device_model
              type: text
              required: false
            - name: app_version
              type: text
              required: false
    """
    queryset = Analytic.objects.none()
    authentication_classes = ()

    def create(self, request, format=None):
        device_id = request.META.get('HTTP_DEVICE_ID', '')
        event = request.data.get('event', None)
        platform = request.data.get('platform', None)
        app_version = request.data.get('app_version', None)
        device_model = request.data.get('device_model', None)
        log_analytic(device_id, event, platform, app_version, device_model)
        return Response(status=status.HTTP_202_ACCEPTED)