from django.conf.urls import patterns, url

urlpatterns = patterns('',
    (r'^reports/cohorts','analytics.views.reports.cohorts'),
    (r'^reports/content','analytics.views.reports.content'),
    (r'^reports/subscriptions','analytics.views.reports.subscriptions'),
    (r'^reports/company_tokens','analytics.views.reports.company_tokens'),
    (r'^reports','analytics.views.reports.index'),
)