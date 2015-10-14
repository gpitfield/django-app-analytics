import datetime
import json
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
from uuidfield import UUIDField


ANALYTICS_SETTINGS = getattr(settings, 'ANALYTICS_SETTINGS' , {})
ANALYTICS = ANALYTICS_SETTINGS.get('EARLIEST_CONTENT_DATE', datetime.date(2015,1,1))


EARLIEST_CONTENT_DATE = datetime.date(2014,9,29)
EARLIEST_CONTENT_DATE_30d = datetime.date(2014,10,2)
EARLIEST_COHORT_DATE = datetime.date(2014,12,1)
COHORT_SIZES = ANALYTICS_SETTINGS.get('COHORT_SIZES', [1,7,28])

class Analytic(models.Model):
    """Single timestamped event recorded  by a device."""
    event = models.CharField(max_length=100, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, db_index=True)
    device_id = models.CharField(max_length=100, db_index=True)
    device_uuid = UUIDField(blank=True, null=True, db_index=True)
    platform = models.CharField(max_length=20, default='iOS', db_index=True)
    device_model = models.CharField(max_length=100, null=True, blank=True)
    app_version = models.CharField(max_length=8, default='1.1', db_index=True)

    def save(self, *args, **kwargs):
        if self.platform == 'iOS' and not self.device_uuid:
            self.device_uuid = self.device_id
        super(Analytic, self).save(*args, **kwargs)

class Cohort(models.Model):
    """Time-bounded bucket for user/device aggregation"""
    size = models.IntegerField(default=1)
    count = models.IntegerField(default=0)
    locked = models.BooleanField(default=False, db_index=True)
    index_date = models.DateField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        index_together = [('timestamp', 'device_id'),]
        index_together = [('size', 'index_date'),]
        unique_together = [('size', 'index_date'),]

    def __unicode__(self):
        return '%sC%d'%(self.index_date.strftime('%Y%m%d'), self.size)

    def create_today_slice(self, date=None):
        date = date if date is not None else timezone.now().date()
        if not date >= self.index_date:
            return
        elif not (date - self.index_date).days % self.size:
            CohortSlice.objects.get_or_create(
                    cohort=self,
                    index_date=date,
                )


    @staticmethod
    def create_cohorts():
        for size in COHORT_SIZES:
            index_date = EARLIEST_COHORT_DATE # TODO: this should be inferred from analytics. Need to check for existing ones.
            if Cohort.objects.filter(size=size):
                index_date = Cohort.objects.filter(
                        size=size
                    ).order_by('-index_date')[0].index_date
            while index_date <= datetime.date.today():
                if not ((index_date - EARLIEST_COHORT_DATE).days % size):
                    Cohort.objects.get_or_create(
                            size=size,
                            index_date=index_date,
                        )
                index_date += datetime.timedelta(1)


    @staticmethod
    def create_slices():
        for c in Cohort.objects.all():
            if CohortSlice.objects.filter(cohort=c):
                latest_slice = CohortSlice.objects.filter(cohort=c).order_by('-index_date')[0]
                index_date = latest_slice.index_date
            else:
                index_date = EARLIEST_COHORT_DATE
            index_date = EARLIEST_COHORT_DATE
            while index_date <= datetime.date.today():
                if not ((index_date-c.index_date).days % c.size):
                    c.create_today_slice(index_date)
                index_date += datetime.timedelta(1)


    @staticmethod
    def update_counts():
        for c in Cohort.objects.filter(locked=False):
            c.count = AnalyticsDevice.objects.filter(
                    first_seen__gte=c.start_datetime,
                    first_seen__lt=c.end_datetime,
                ).count()
            if timezone.now() >= (c.end_datetime + datetime.timedelta(7)):
                c.locked = True
            c.save()


    @staticmethod
    def create_report(writer):
        field_names = [
            'cohort',
            'size',
            'count',
            'index_date',
            'uniques',
            'unique_didFinishLaunching',
            'unique_loginEmail',
            'unique_loginAttempted',
            'unique_badEmail',
            'unique_loginFailedIneligible',
            'unique_loginOKIneligible',
            'unique_Invalid email address',
            'unique_Ineligible domain',
            'unique_startLinkedIn',
            'unique_enteredPIN',
            'unique_createAccountSuccess',
            'unique_loadedFeed',
            'unique_loadedFeed-popular',
            'unique_loadedFeed-following',
            'unique_loadedFeed-myCompany',
            'unique_startLinkedInSafari',
            'unique_viewedInvite',
            'unique_viewedSettings',
            'viewedSettings',
            'startLinkedInSafari',
            'loginEmail',
            'startLinkedIn',
            'loginAttempted',
            'badEmail',
            'Invalid email address',
            'Ineligible domain',
            'unique_startLinkedInCreds',
            'createAccountSuccess',
            'startLinkedInCreds',
            'enteredPIN',
            'loadedFeed-myCompany',
            'loadedFeed',
            'didFinishLaunching',
            'loadedFeed-following',
            'viewedInvite',
            'loadedFeed-popular',
            'loginFailedIneligible',
            'loginOKIneligible',
        ]
        # write a first row with header information
        writer.writerow(field_names)
        for size in COHORT_SIZES:
            for c in Cohort.objects.filter(size=size).order_by('index_date'):
                slices = CohortSlice.objects.filter(cohort=c).values(
                        'analytics',
                        'index_date',
                    ).order_by('index_date')
                for slice in slices: # write data rows
                    if not slice['analytics']:
                        continue
                    row = [c, c.size, c.count, slice['index_date'].strftime('%Y-%m-%d')]
                    analytics = json.loads(slice['analytics'])
                    for k in field_names[4:]:
                        if k in analytics:
                            row.append(analytics[k])
                        else:
                            row.append(0)
                    writer.writerow(row)


    def save(self, *args, **kwargs):
        self.start_datetime = datetime.datetime.combine(self.index_date, datetime.time(0,0))
        self.end_datetime = self.start_datetime + datetime.timedelta(self.size)
        super(Cohort, self).save(*args, **kwargs)


class CohortSlice(models.Model):
    cohort = models.ForeignKey('Cohort')
    index_date = models.DateField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    count = models.IntegerField(default=0)
    analytics = models.CharField(max_length=5000, null=True, blank=True)
    complete = models.BooleanField(default=False, db_index=True)

    class Meta:
        index_together = [('cohort', 'index_date'),]
        unique_together = [('cohort', 'index_date'),]

    def __unicode__(self):
        return '%s - %s'%(self.cohort, self.index_date)

    def save(self, *args, **kwargs):
        self.start_datetime = datetime.datetime.combine(self.index_date, datetime.time(0,0))
        self.end_datetime = self.start_datetime + datetime.timedelta(self.cohort.size)
        if not (self.index_date - self.cohort.index_date).days % self.cohort.size:
            # ensure valid index_date given cohort bucket size and index date
            super(CohortSlice, self).save(*args, **kwargs)
        else:
            raise

    def aggregate(self):
        analytics = {'uniques':0}
        for agg_device in AggregateDevice.objects.filter(
                cohort_slice=self
            ).values(
                'analytics',
                'active',
            ):
                if agg_device['active']:
                    analytics['uniques'] += 1
                if not agg_device['analytics']:
                    continue
                for k, v in json.loads(agg_device['analytics']).items():
                    unique_k = 'unique_%s'%k
                    if not k in analytics:
                        analytics[k] = 0
                    if not unique_k in analytics:
                        analytics[unique_k] = 0
                    analytics[k] += v
                    if v > 0:
                        analytics[unique_k] += 1
        self.analytics = json.dumps(analytics)
        self.count = analytics['uniques']
        if timezone.now() > (self.end_datetime + datetime.timedelta(7)):
            self.complete = True        
        self.save()


class AnalyticsDevice(models.Model):
    device_id = models.CharField(max_length=60, db_index=True, unique=True)
    first_seen = models.DateTimeField()
    beta_device = models.BooleanField(default=False)
    platform = models.CharField(max_length=20, default='iOS', db_index=True)
    cohorts = models.ManyToManyField('Cohort')

    def save(self, *args, **kwargs):
        if not self.first_seen:
            my_analytics = Analytic.objects.filter(device_id=self.device_id)
            self.first_seen = Analytic.objects.filter(
                    device_id=self.device_id
                ).order_by('timestamp').values_list(
                    'timestamp',
                    flat=True
                )[0]
        super(AnalyticsDevice, self).save(*args, **kwargs)
        if not self.cohorts.all():
            self.cohorts.clear()
            cohorts = Cohort.objects.filter(
                    start_datetime__lte=self.first_seen,
                    end_datetime__gt=self.first_seen,
                )
            self.cohorts.add(*cohorts)


    @staticmethod
    def create_devices():
        new_device_ids = Analytic.objects.exclude(
                device_id__in=AnalyticsDevice.objects.distinct().values_list('device_id', flat=True)
            ).distinct().values_list(
                'device_id',
                flat=True
            )
        for device_id in new_device_ids:
            AnalyticsDevice.objects.get_or_create(
                    device_id=device_id,
                )


class AggregateDevice(models.Model):
    cohort_slice = models.ForeignKey('CohortSlice')
    device_id = models.CharField(max_length=60, db_index=True)
    platform = models.CharField(max_length=20, db_index=True, null=True)
    analytics = models.CharField(max_length=5000, null=True, blank=True)
    active = models.BooleanField(default=False)
    complete = models.BooleanField(default=False, db_index=True)

    class Meta:
        index_together = [('cohort_slice', 'device_id'),]
        unique_together = [('cohort_slice', 'device_id'),]


    def aggregate(self):
        start_datetime = self.cohort_slice.start_datetime
        end_datetime = self.cohort_slice.end_datetime
        analytics = {}
        login_attempt = ['startLinkedIn', 'loginEmail']
        bad_email = ['Ineligible domain', 'Invalid email address']
        self.active = True if Analytic.objects.filter(
                    device_id=self.device_id,
                    timestamp__gt=start_datetime,
                    timestamp__lte=end_datetime,
                ).count() > 0 else False
        my_analytics = Analytic.objects.filter(
                device_id=self.device_id,
                timestamp__gt=start_datetime,
                timestamp__lte=end_datetime,
            )
        for event in Analytic.objects.values_list('event', flat=True).distinct():
            # TODO: the events should be cached somewhere or just listed out
            value = my_analytics.filter(
                    event=event,
                ).count()
            analytics[event] = value
        analytics['loginAttempted'] = my_analytics.filter(event__in=login_attempt).count()
        analytics['badEmail'] = my_analytics.filter(event__in=bad_email).count()
        analytics['loginFailedIneligible'] = int(my_analytics.filter(event__in=bad_email).exists() and 
            not my_analytics.filter(event__in=['createAccountSuccess']).exists())
        analytics['loginOKIneligible'] = int(my_analytics.filter(event__in=bad_email).exists() and 
            my_analytics.filter(event__in=['createAccountSuccess']).exists())
        self.analytics = json.dumps(analytics)
        if timezone.now() > (end_datetime + datetime.timedelta(1)):
            self.complete = True
        self.save()

class ContentSlice(models.Model):
    size = models.IntegerField(default=1)
    index_date = models.DateField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    analytics = models.CharField(max_length=5000, null=True, blank=True)
    complete = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = [('size', 'index_date'),]

    def __unicode__(self):
        return '%sC%d'%(self.index_date.strftime('%Y%m%d'), self.size)

    def save(self, *args, **kwargs):
        self.start_datetime = datetime.datetime.combine(self.index_date, datetime.time(0,0))
        self.end_datetime = self.start_datetime + datetime.timedelta(self.size)
        super(ContentSlice, self).save(*args, **kwargs)


    def aggregate(self):
        self.analytics = json.dumps({
                'posts': Post.objects.filter(
                    timestamp__gt=self.start_datetime,
                    timestamp__lte=self.end_datetime
                ).count(),
                'comments': Comment.objects.filter(
                    timestamp__gt=self.start_datetime,
                    timestamp__lte=self.end_datetime
                ).count(),
                'likes': Like.objects.filter(
                    timestamp__gt=self.start_datetime,
                    timestamp__lte=self.end_datetime
                ).count(),
                'flags': Flag.objects.filter(
                    timestamp__gt=self.start_datetime,
                    timestamp__lte=self.end_datetime
                ).count(),
            })
        if timezone.now() > (self.end_datetime + datetime.timedelta(1)):
            self.complete = True
        self.save()

    @staticmethod
    def create_slices():
        for size in COHORT_SIZES:
            earliest_content_date = EARLIEST_CONTENT_DATE_30d if size == 30 else EARLIEST_CONTENT_DATE
            index_date = earliest_content_date
            if ContentSlice.objects.filter(size=size):
                index_date = Cohort.objects.filter(
                        size=size
                    ).order_by('-index_date')[0].index_date
            while index_date <= datetime.date.today():
                if not ((index_date - earliest_content_date).days % size):
                    ContentSlice.objects.get_or_create(
                            size=size,
                            index_date=index_date,
                        )
                index_date += datetime.timedelta(1)

    @staticmethod
    def create_report(writer):
        field_names = [
            'contentSlice',
            'size',
            'index_date',
            'posts',
            'comments',
            'likes',
            'flags',
        ]
        # write a first row with header information
        writer.writerow(field_names)
        for size in COHORT_SIZES:
            for slice in ContentSlice.objects.filter(size=size).order_by('index_date'):
                if not slice.analytics:
                    continue
                row = [slice, slice.size, slice.index_date.strftime('%Y-%m-%d')]
                analytics = json.loads(slice.analytics)
                for k in field_names[3:]:
                    if k in analytics:
                        row.append(analytics[k])
                    else:
                        row.append(0)
                writer.writerow(row)