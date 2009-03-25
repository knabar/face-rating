from django import forms
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
import os
import random
import sys
from django.utils.safestring import mark_safe
from models import RatingResponse, Submission, SimilarityResponse

class FaceImageWidget(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        output = super(FaceImageWidget, self).render(name, value, attrs)
        if value is None: value = ''
        return mark_safe(output + u'\n<img src="%s" />' % reverse('static', args=[value]))


def ratingField(label):
    return forms.IntegerField(label=label, required=True,
                              widget=forms.RadioSelect(choices=list((x, x) for x in range(0, 10))))

 
class FaceRatingWizard(FormWizard):

    def _get_filelist(self):
        return filter(lambda f: f.endswith('.jpg'), os.listdir(os.path.join(settings.MEDIA_ROOT, 'faces')))

    def __call__(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login') + '?next=' + request.path)
        submission_id = request.session.get('submission', 0)
        if submission_id:
            submission = Submission.objects.get(id=submission_id)
            if submission.progress >= self.get_step():
                return HttpResponseRedirect(reverse("part%s" % (self.get_step() + 1)))
            if submission.progress < self.get_step() - 1:
                return HttpResponseRedirect(reverse("part%s" % (self.get_step() - 1)))
        else:
            if request.session.get('email'):
                submission = Submission.objects.create(user=request.user,
                                                       email=request.session.get('email'),
                                                       progress=0)
                request.session['submission'] = submission.id
                return HttpResponseRedirect(request.path)
            else:
                return HttpResponseRedirect(reverse("intro"))
        return super(FaceRatingWizard, self).__call__(request, *args, **kwargs)

    def get_step(self):
        raise Exception()


class Part1Wizard(FaceRatingWizard):

    class Part1RatingForm(forms.Form):
        p1 = ratingField('Asian American prototypicality')
#        a = ratingField('Attractiveness')
#        p2 = ratingField('Asian prototypicality')
#        p3 = ratingField('American prototypicality')
        i = forms.CharField(widget=FaceImageWidget())
    
    def __init__(self, count):
        forms = [Part1Wizard.Part1RatingForm] * min(count, len(self._get_filelist()))
        super(Part1Wizard, self).__init__(forms)
            
    def _get_images(self, request):
        images = request.session.get('part1images', None)
        if not images:
            images = self._get_filelist()
            images = map(lambda i: {'i': 'faces/' + i}, random.sample(images, min(len(images), len(self.form_list))))
            request.session['part1images'] = images
        return images
            
    def get_form(self, step, data=None):
        return self.form_list[step](data, prefix=self.prefix_for_step(step),
                                    initial=self._get_images(sys._getframe(1).f_locals.get('request'))[step])

    def done(self, request, form_list):
        submission = Submission.objects.get(id=request.session['submission'])
        for form in form_list:
            RatingResponse.objects.create(submission=submission,
                    prototypicality_asam=form.cleaned_data['p1'],
#                    attractiveness=form.cleaned_data['a'],
#                    prototypicality_as=form.cleaned_data['p2'],
#                    prototypicality_am=form.cleaned_data['p3'],
                    face=os.path.splitext(os.path.basename(form.cleaned_data['i']))[0])
        submission.progress = 1
        submission.save() 
        return HttpResponseRedirect(reverse("part2intro"))
    
    def get_template(self, step):
        return 'part1.html'

    def get_step(self):
        return 1


class Part2Wizard(FaceRatingWizard):

    class Part2RatingForm(forms.Form):
        s = ratingField('Similarity')
        i1 = forms.CharField(widget=FaceImageWidget())
        i2 = forms.CharField(widget=FaceImageWidget())

    def __init__(self, count):
        files = self._get_filelist()
        forms = [Part2Wizard.Part2RatingForm] * min(count, len(files) * (len(files) - 1))
        super(Part2Wizard, self).__init__(forms)
            
    def _get_pairs(self, request):
        pairs = request.session.get('part2pairs', None)
        if not pairs:
            images = self._get_filelist()
            def gen_pair():
                x = random.randint(0, len(images) - 1)
                return {'i1': 'faces/' + images[x],
                        'i2': 'faces/' + images[(x + random.randint(1, len(images) - 2)) % len(images)]}
            pairs = []
            while len(pairs) < len(self.form_list):
                p = gen_pair()
                if not p in pairs:
                    pairs.append(p)
            request.session['part2pairs'] = pairs
        return pairs
            
    def get_form(self, step, data=None):
        return self.form_list[step](data, prefix=self.prefix_for_step(step),
                                    initial=self._get_pairs(sys._getframe(1).f_locals.get('request'))[step])

    def done(self, request, form_list):
        submission = Submission.objects.get(id=request.session['submission'])
        for form in form_list:
            SimilarityResponse.objects.create(submission=submission,
                similarity=form.cleaned_data['s'],
                face1=os.path.splitext(os.path.basename(form.cleaned_data['i1']))[0],
                face2=os.path.splitext(os.path.basename(form.cleaned_data['i2']))[0])
        
        submission.progress = 2
        submission.save()                
        return HttpResponseRedirect(reverse("part3"))
    
    def get_template(self, step):
        return 'part2.html'

    def get_step(self):
        return 2

