from django.contrib import admin
from analytics.models import Analytic, Cohort, CohortSlice
from analytics.models import AnalyticsDevice, AggregateDevice
from analytics.models import ContentSlice

class AnalyticsAdmin(admin.ModelAdmin):
	list_display = ['event', 'timestamp', 'device_model', 
		'platform', 'app_version', 'device_id',
	]
	list_filter = ['event', 'platform', 'app_version']
	change_form_template = 'admin/analytics_change_form.html'

class CohortAdmin(admin.ModelAdmin):
	list_display = ['size', 'index_date', 'count', 'locked']
	list_filter = ['size',]
	change_form_template = 'admin/cohort_change_form.html'

class CohortSliceAdmin(admin.ModelAdmin):
	list_display = ['cohort', 'index_date', 'count', 'analytics']
	list_filter = ['cohort',]
	change_form_template = 'admin/cohortslice_change_form.html'

class AnalyticsDeviceAdmin(admin.ModelAdmin):
	list_display = ['device_id', 'first_seen', 'beta_device']
	list_filter = ['beta_device']
	change_form_template = 'admin/analyticsdevice_change_form.html'

class AggregateDeviceAdmin(admin.ModelAdmin):
	list_display = ['cohort_slice', 'device_id', 'active', 'platform', 'complete', 'analytics']
	list_filter = ['complete', 'platform']
	raw_id_fields = ['cohort_slice']
	change_form_template = 'admin/aggregatedevice_change_form.html'

class ContentSliceAdmin(admin.ModelAdmin):
	list_display = ['size', 'index_date', 'analytics', 'complete']

admin.site.register(Analytic, AnalyticsAdmin)
admin.site.register(Cohort, CohortAdmin)
admin.site.register(CohortSlice, CohortSliceAdmin)
admin.site.register(AnalyticsDevice, AnalyticsDeviceAdmin)
admin.site.register(AggregateDevice, AggregateDeviceAdmin)
admin.site.register(ContentSlice, ContentSliceAdmin)
