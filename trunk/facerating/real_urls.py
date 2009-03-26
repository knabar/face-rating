from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from rating.views import *
from rating.forms import Part1Wizard, Part2Wizard
from django.contrib.auth.views import logout
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^facerating/', include('facerating.foo.urls')),

#    (r'^$', direct_to_template, {'template': 'main.html'}),
    url(r'^part1/intro/', direct_to_template, {'template': 'part1intro.html'}, name='part1intro'),
    url(r'^part2/intro/', direct_to_template, {'template': 'part2intro.html'}, name='part2intro'),
    
    url(r'^$', intro, name='intro'),
    url(r'^part1/', Part1Wizard(settings.PART1COUNT), name='part1'),  
    url(r'^part2/', Part2Wizard(settings.PART2COUNT), name='part2'),  
    url(r'^part3/', part3, name='part3'),
    url(r'^part4/', part4, name='part4'),
    url(r'^debrief/', direct_to_template, {'template': 'debrief.html'}, name='debrief'),
#    url(r'^purpose/', direct_to_template, {'template': 'purpose.html'}, name='purpose'),
    url(r'^instructions/', direct_to_template, {'template': 'instructions.html'}, name='instructions'),

    url(r'^downloadcsvs/', download_csvs, name='downloadcsvs'),

    url(r'^accounts/login/$', login, {'template_name': 'registration/login.html'}, name='login'), #, 'SSL': True
    (r'^accounts/logout/$', logout, {'template_name': 'registration/logout.html'}),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),# {'SSL': True}),
    
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'd:/dev/face-rating/static'}, name='static'),

)
