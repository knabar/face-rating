from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site, RequestSite
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.shortcuts import render_to_response
from django.conf import settings
from django import forms
from django.forms import ModelForm, ChoiceField, CharField 
from django.forms.models import ModelMultipleChoiceField
from django.forms.formsets import formset_factory
from django.forms.widgets import CheckboxSelectMultiple
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
import os
import random
from models import *
from datetime import datetime

class MyAuthenticationForm(AuthenticationForm):
    code = CharField()
    
    def clean_code(self):
        data = self.cleaned_data['code']
        if not AccessCode.objects.filter(code=data, valid_until__gt=datetime.now()):
            raise forms.ValidationError("Invalid access code")
        return data

def login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    "Displays the login form and handles the login action."
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = MyAuthenticationForm(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        form = MyAuthenticationForm(request)
    request.session.set_test_cookie()
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))
login = never_cache(login)


def intro(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            request.session['email'] = email
            return HttpResponseRedirect(reverse("instructions"))

    return render_to_response("main.html")



@login_required
def part3(request):
       
    class InformationForm(ModelForm):
        q3 = ModelMultipleChoiceField(queryset=FeaturesCriteria.objects.all(), widget=CheckboxSelectMultiple,
                                      label=Information._meta.get_field('q3').verbose_name)
        class Meta:
            model = Information
            exclude = ('submission',)

    submission_id = request.session.get('submission', 0)
    if submission_id:
        submission = Submission.objects.get(id=submission_id)
        if submission.progress >= 3:
            return HttpResponseRedirect(reverse("part4"))
        if submission.progress < 2:
            return HttpResponseRedirect(reverse("part2"))
    else:
        submission = Submission.objects.create(user=request.user, progress=0)
        request.session['submission'] = submission.id
        return HttpResponseRedirect(request.path)       

    if request.method == 'POST': 
        form = InformationForm(request.POST)
        if form.is_valid():
            i = form.save(commit=False)
            i.submission = submission
            i.save()
            form.save_m2m()
            submission.progress = 3
            submission.save()
            return HttpResponseRedirect(reverse('part4')) 
    else:
        form = InformationForm()
    
    return render_to_response('part3.html',
                       {'form': form, },
                      )



@login_required
def part4(request):
       
    class DemographicsForm(ModelForm):
        
        sex = ChoiceField(choices=(('', ''), ('M', 'Male'), ('F', 'Female'), ('T', 'Transgender')))
        adopted = ChoiceField(choices=((False, 'No'), (True, 'Yes')))
        background = ModelMultipleChoiceField(queryset=RacialBackground.objects.all(), widget=CheckboxSelectMultiple,
                                      label=Demographics._meta.get_field('background').verbose_name)
#        religion_community = ChoiceField(choices=((False, 'No'), (True, 'Yes')))
        
        class Meta:
            model = Demographics
            exclude = ('submission',)

    submission_id = request.session.get('submission', 0)
    if submission_id:
        submission = Submission.objects.get(id=submission_id)
        if submission.progress >= 4:
            return HttpResponseRedirect(reverse("debrief"))
        if submission.progress < 3:
           return HttpResponseRedirect(reverse("part3"))
    else:
        submission = Submission.objects.create(user=request.user, progress=0)
        request.session['submission'] = submission.id
        return HttpResponseRedirect(request.path)       

    if request.method == 'POST': 
        form = DemographicsForm(request.POST)
        if form.is_valid():
            i = form.save(commit=False)
            i.submission = submission
            i.save()
            form.save_m2m()
            submission.progress = 4
            submission.save()            
            return HttpResponseRedirect(reverse('debrief')) 
    else:
        form = DemographicsForm()
    
    return render_to_response('part4.html',
                       {'form': form, },
                      )


@permission_required("rating.can_download")
def download_csvs(request):
    
    import StringIO
    import zipfile
    import csv
    
    users = dict(User.objects.all().values_list('id','username'))
    submissions = dict(map(lambda (i,u,e,d,p): (i, [users[u], e, str(d), p]),
                       Submission.objects.all().values_list('id','user','email','date','progress')))
    
    file = StringIO.StringIO()
    zipfile = zipfile.ZipFile(file, mode='w', compression=zipfile.ZIP_DEFLATED)
    
    def add_file(filename, headers, rows):
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        csvwriter.writerow(headers)
        for r in rows:
            csvwriter.writerow(r)    
        zipfile.writestr(filename, csvfile.getvalue())
    
    # submissions
    def submission_rows():
        for s in submissions:
            yield [s] + submissions[s]            
    add_file("participants.csv", "Submission User Email Date Progress".split(), submission_rows())
        
    # rating
    def rating_rows():
        for r in RatingResponse.objects.all():
#            yield [r.submission_id, submissions[r.submission_id][0], r.face,
#                   r.prototypicality_asam, r.attractiveness, r.prototypicality_as, r.prototypicality_am]
            yield [r.submission_id, submissions[r.submission_id][0], r.face,
                   r.prototypicality_asam]
    #add_file("ratings.csv", "Submission User Face Prot_AsAm Attr Prot_As Prot_Am".split(), rating_rows())
    add_file("ratings.csv", "Submission User Face Prot_AsAm".split(), rating_rows())
    
    # similarity
    def similarity_rows():
        for s in SimilarityResponse.objects.all():
            yield [s.submission_id, submissions[s.submission_id][0], s.face1, s.face2, s.similarity]
    add_file("similarity.csv", "Submission User Face1 Face2 Similarity".split(), similarity_rows())
        
    # information
    fc = FeaturesCriteria.objects.all().order_by('id').values_list('id', 'criteria')
    fcdict = dict(fc)
    def information_rows():
        for i in Information.objects.select_related().all():
            r = [i.submission_id, submissions[i.submission_id][0], i.q1, i.q2]
            q3 = i.q3.all().values_list('id', flat=True)
            r = r + map(lambda i: i[0] in q3 and i[1], fc)
            r = r + [i.q3other, i.q4a.criteria, i.q4b.criteria, i.q4c.criteria, i.q4d.criteria, i.q4e.criteria]
            r = r + [i.q5]
            yield r
    add_file("information.csv",
             "Submission User FaceCharacteristics BackgroundCharacteristics".split() +
             map(lambda i: i[1], fc) +
             "Other First Second Third Fourth Fifth Comments".split(), information_rows())
    
    # demographics
    rb = RacialBackground.objects.all().order_by('id').values_list('id', 'background')
    def demographics_rows():
        for d in Demographics.objects.select_related().all():
            r = [d.submission_id, submissions[d.submission_id][0], d.age, d.sex, d.birthplace, d.lived_in_us,
                 d.adopted]
            background = d.background.all().values_list('id', flat=True)
            r = r + map(lambda i: i[0] in background and i[1], rb)
            r = r + [d.background_other, d.background_mother, d.background_father, d.generation_status,
                     d.locations, d.hometown_street, d.hometown_city_state, 
                     d.hometown_not_us, d.religion,
                     d.friends, d.friends_asian, d.friends_black, d.friends_white, d.friends_latino,
                     d.friends_native_american, d.friends_bi_asian, d.friends_bi_nonasian, d.partners,
                     d.partners_asian, d.partners_black, d.partners_white, d.partners_latino,
                     d.partners_native_american, d.partners_bi_asian, d.partners_bi_nonasian,
                     d.courses]
            #r = r + [d.background_other, d.background_mother, d.background_father, d.generation_status,
            #         d.locations, d.hometown_street, d.hometown_city_state, d.hometown_zip_code,
            #         d.hometown_not_us, d.religion, d.religion_community, d.religion_community_ethnic,
            #         d.friends, d.friends_asian, d.friends_black, d.friends_white, d.friends_latino,
            #         d.friends_native_american, d.friends_bi_asian, d.friends_bi_nonasian, d.partners,
            #         d.partners_asian, d.partners_black, d.partners_white, d.partners_latino,
            #         d.partners_native_american, d.partners_bi_asian, d.partners_bi_nonasian,
            #         d.courses, d.courses_identity]
            yield r
    add_file("demographics.csv",
             "Submission User Age Sex Birthplace LivedInUS Adopted".split() +
             map(lambda i: i[1], rb) +
             "Other Mother Father Generation Locations Street CityState NotUS \
             Religion Friends FriendsAsian FriendsBlack FriendsWhite FriendsLatino \
             FriendsNativeAmerican FriendsBiAsian FriendsBiNonAsian Partners PartnersAsian \
             PartnersBlack PartnersWhite PartnersLatino PartnersNativeAmerican PartnersBiAsian \
             PartnersBiNonAsian Courses".split(),
             demographics_rows())
    #add_file("demographics.csv",
    #         "Submission User Age Sex Birthplace LivedInUS Adopted".split() +
    #         map(lambda i: i[1], rb) +
    #         "Other Mother Father Generation Locations Street CityState ZIP NotUS \
    #         Religion Community EthnicGroup Friends FriendsAsian FriendsBlack FriendsWhite FriendsLatino \
    #         FriendsNativeAmerican FriendsBiAsian FriendsBiNonAsian Partners PartnersAsian \
    #         PartnersBlack PartnersWhite PartnersLatino PartnersNativeAmerican PartnersBiAsian \
    #         PartnersBiNonAsian Courses IdentityCourses".split(),
    #         demographics_rows())
    
    zipfile.close()    
    response = HttpResponse(file.getvalue(), mimetype="application/zip")
    response['Content-Disposition'] = 'attachment; filename=faceratings.zip'
    return response
