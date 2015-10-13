import csv
from django.shortcuts import render, render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from analytics.models import Cohort, ContentSlice
from notifications.models import Subscription
from profiles.models import AnonProfile

@staff_member_required
def index(request):
	return cohorts(request)


@staff_member_required
def cohorts(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv'%'cohorts'
    writer = csv.writer(response)
    Cohort.create_report(writer)
    return response


@staff_member_required
def content(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv'%'content'
    writer = csv.writer(response)
    ContentSlice.create_report(writer)
    return response

@staff_member_required
def subscriptions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv'%'subscriptions'
    writer = csv.writer(response)
    Subscription.create_report(writer)
    return response

@staff_member_required
def company_tokens(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv'%'company_tokens'
    writer = csv.writer(response)
    AnonProfile.create_report(writer)
    return response