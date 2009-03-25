from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from rating.views import *
from rating.forms import Part1Wizard, Part2Wizard
from django.contrib.auth.views import logout

urlpatterns = patterns('',
    (r'^facerating/', include('facerating.real_urls')),
)
