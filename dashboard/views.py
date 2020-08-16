from django.http import JsonResponse
from django.template import loader
import json
from .metrics.metrics import Metrics
from django.shortcuts import render
from lockdown.decorators import lockdown
@lockdown()
def index(request):
    met = Metrics()
    charts = met.pipeline()
    
    return render(request, 'dashboard/dash.html',context = {'charts':charts})
