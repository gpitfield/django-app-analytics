import sys
import datetime
import random
from celery import shared_task
from django.utils import timezone
from analytics.models import Analytic, Cohort, CohortSlice 
from analytics.models import AnalyticsDevice, AggregateDevice
from analytics.models import ContentSlice
from django.conf import settings


def log_analytic(device_id='', event=None, platform=None, app_version=None, device_model=None, request_meta=None):
    if request_meta:
        device_id = request_meta.get('HTTP_DEVICE_ID', device_id)  
        platform = request_meta.get('platform', platform)
        app_version = request_meta.get('app_version', app_version)
        device_model = request_meta.get('device_model', device_model)
    if settings.IS_PRODUCTION:
        log.apply_async((device_id, event, platform, app_version, device_model),
            retry=True, 
            retry_policy={
                'max_retries': 10,
                'interval_start': 5.0,
                'interval_step': 5.0,
                'interval_max': 60.0,
            }
        )
    else:
        log(device_id, event, platform, app_version, device_model)

@shared_task
def log(device_id=None, event=None, platform=None, app_version=None, device_model=None, request_meta=None):
    if event is None:
        return
    analytic = Analytic()
    if device_id:
        analytic.device_id = device_id
    if event:
        analytic.event = event
    if platform:
        analytic.platform = platform
    if app_version:
        analytic.app_version = app_version
    if device_model:
        analytic.device_model = device_model
    analytic.save()

@shared_task
def summarize_slices():
    sys.stdout.write('update_counts\n')
    Cohort.update_counts()
    sys.stdout.write('aggregating slices\n')
    # for cohort_slice in CohortSlice.objects.all():
    for cohort_slice in CohortSlice.objects.filter(complete=False):
        cohort_slice.aggregate()

@shared_task
def setup_analytics():
    sys.stdout.write('create_contentslices\n')
    ContentSlice.create_slices()
    sys.stdout.write('create_cohorts\n')
    Cohort.create_cohorts()
    sys.stdout.write('create_slices\n')
    Cohort.create_slices()
    sys.stdout.write('create_devices\n')
    AnalyticsDevice.create_devices()
    sys.stdout.write('processing devices\n')
    for device_id in AnalyticsDevice.objects.values_list('device_id', flat=True):
        if settings.IS_PRODUCTION or settings.IS_CANNON:
            process_device_analytics.apply_async((device_id,), retry=True,
                retry_policy={
                    'max_retries': 10,
                    'interval_start': 5.0,
                    'interval_step': 5.0,
                    'interval_max': 60.0,
                }
            )
        else:
            process_device_analytics(device_id)
    sys.stdout.write('processing content\n')
    # for content_slice in ContentSlice.objects.all():
    for content_slice in ContentSlice.objects.filter(complete=False):
        if settings.IS_PRODUCTION:
            aggregate_content_analytics.apply_async((content_slice,), retry=True,
                retry_policy={
                    'max_retries': 10,
                    'interval_start': 5.0,
                    'interval_step': 5.0,
                    'interval_max': 60.0,
                }
            )
        else:
            aggregate_content_analytics(content_slice)

@shared_task
def aggregate_content_analytics(content_slice):
    content_slice.aggregate()

@shared_task
def process_device_analytics(device_id):
    device, created = AnalyticsDevice.objects.get_or_create(device_id=device_id)
    slices = CohortSlice.objects.filter(
            cohort__in=device.cohorts.all()
        ).order_by('index_date').distinct()
    for slice in slices:
        if AggregateDevice.objects.filter(
            cohort_slice=slice, device_id=device_id, complete=True):
            continue
        agg_device, created = AggregateDevice.objects.get_or_create(
                cohort_slice=slice,
                device_id=device_id,
                platform=device.platform,
            )
        agg_device.aggregate()