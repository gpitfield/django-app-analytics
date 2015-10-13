#!/usr/bin/pythonv

import sys,os
import datetime, time, subprocess
import random
import string
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from analytics.models import Analytic, Cohort, CohortSlice, AnalyticsDevice
from analytics.tasks import process_device_analytics
from analytics.tasks import setup_analytics, summarize_slices

class Command(BaseCommand):
	args = '<summarize>'
	help = 'Run some basic analytics'


	def handle(self, *args, **options):
		if len(args) == 0:
			setup_analytics()
		elif args[0] == 'summarize':
			summarize_slices()