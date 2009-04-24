from django.db import models
from django.contrib.auth.models import User

class AccessCode(models.Model):
    code = models.CharField(max_length=20)
    valid_until = models.DateTimeField()
    
    def __unicode__(self):
        return "Code '%s' valid until %s" % (self.code, self.valid_until)

class Submission(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True)
    progress = models.PositiveSmallIntegerField()
    email = models.TextField(max_length=100)

    def __unicode__(self):
        return "ID %s Step %s - %s" % (self.id, self.progress, self.date)
    
    class Meta:
        permissions = (
            ("can_download", "Can download"),
        )


class SimilarityResponse(models.Model):
    submission = models.ForeignKey(Submission)
    face1 = models.CharField(max_length=50)
    face2 = models.CharField(max_length=50)
    similarity = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return "Sub %s Faces %s-%s Sim %s" % (self.submission_id, self.face1, self.face2, self.similarity)

    
class RatingResponse(models.Model):
    submission = models.ForeignKey(Submission)
    face = models.CharField(max_length=50)
    prototypicality_asam = models.PositiveSmallIntegerField()
#    attractiveness = models.PositiveSmallIntegerField()
#    prototypicality_as = models.PositiveSmallIntegerField()
#    prototypicality_am = models.PositiveSmallIntegerField()
    
    def __unicode__(self):
        return "Sub %s Face %s AsAm %s" % (self.submission_id, self.face, self.prototypicality_asam)
        #return "Sub %s Face %s AsAm %s Attr %s As %s Am %s" % (self.submission_id, self.face,
        #                                                       self.prototypicality_asam, self.attractiveness,
        #                                                       self.prototypicality_as, self.prototypicality_am)


class FeaturesCriteria(models.Model):
    criteria = models.CharField(max_length=100)
    group = models.CharField(max_length=1)
    
    def __unicode__(self):
        t = self._group_title()
        if t:
            return "%s: %s" % (t, self.criteria)
        else:
            return self.criteria
    
    def _group_title(self):
        return None
        #if self.group == 'f':
        #    return 'Facial features criteria'
        #elif self.group == 'o':
        #    return 'Other commonly used criteria'
        #else:
        #    return None;
            
    
    
class Information(models.Model):
    submission = models.ForeignKey(Submission)
    q1 = models.TextField(verbose_name='What specific characteristics in the faces you saw did you use to make your judgments?')
    q2 = models.TextField(verbose_name='What is your personal definition of "Asian American"? Where did you learn this definition?')
    q3 = models.ManyToManyField(FeaturesCriteria, verbose_name='Please select which characteristics from the following lists you actually used to make your judgments. Please do not change your responses to Question 1 or Question 2 for this part of the study.')
    q3other = models.TextField(verbose_name='Other criteria', blank=True)
    q4a = models.ForeignKey(FeaturesCriteria, related_name='information_set_q4a', verbose_name='First most often used criteria')
    q4b = models.ForeignKey(FeaturesCriteria, related_name='information_set_q4b', verbose_name='Second most often used criteria')
    q4c = models.ForeignKey(FeaturesCriteria, related_name='information_set_q4c', verbose_name='Third most often used criteria')
    q4d = models.ForeignKey(FeaturesCriteria, related_name='information_set_q4d', verbose_name='Fourth most often used criteria')
    q4e = models.ForeignKey(FeaturesCriteria, related_name='information_set_q4e', verbose_name='Fifth most often used criteria')
    q5 = models.TextField(verbose_name='Please tell us anything about your experience in this study that you think would be helpful to the research team.', blank=True)

    def __unicode__(self):
        return "Sub %s" % (self.submission_id)


class RacialBackground(models.Model):
    background = models.CharField(max_length=40)

    def __unicode__(self):
        return self.background
    
    
class Demographics(models.Model):
    
    GENERATION_CHOICES = (
        ('1st', '1st: you immigrated to US at or before age 12'),
        ('1.5', '1.5: you immigrated to US after age 12'),
        ('2nd', '2nd: you were born here; at least one of your parents immigrated to the US'),
        ('3rd', '3rd: you were born here; at least one of your grandparents immigrated to the US'),
        ('4th', '4th: you were born here; at least one of your great-grandparents immigrated to the US'),
        ('Other', 'Other (please specify)'),
    )
    
    RELIGION_CHOICES = (
        ('Buddhist', 'Buddhist'),
        ('Catholic', 'Catholic'),
        ('Hindu', 'Hindu'),
        ('Jewish', 'Jewish'),
        ('Muslim', 'Muslim'),
        ('Protestant', 'Protestant'),
        ('None - Atheist', 'None - Atheist'),
        ('None - Agnostic', 'None - Agnostic'),
        ('Other ', 'Other '),
    )
    
    submission = models.ForeignKey(Submission)
    age = models.SmallIntegerField(verbose_name='Age')
    sex = models.CharField(verbose_name='Sex', max_length=1)
    birthplace = models.CharField(verbose_name='Where were you born (city, state, country)?', max_length=100)
    lived_in_us = models.DecimalField(null=True, blank=True, decimal_places=1, max_digits=4, verbose_name='If you were not born in the U.S., how many years have you lived in the U.S.?')
    adopted = models.BooleanField(verbose_name='Are you adopted?')
    background = models.ManyToManyField(RacialBackground, verbose_name='Which of these groups best describes your background? (If multiracial, select all that apply.)')
    background_other = models.CharField(verbose_name='Other', max_length=100, blank=True)    
    background_mother = models.CharField(verbose_name='Mother', max_length=100)
    background_father = models.CharField(verbose_name='Father', max_length=100)
    generation_status = models.CharField(verbose_name='What is your generation status?', max_length=10, choices=GENERATION_CHOICES)
    generation_status_other = models.CharField(verbose_name='Other', max_length=100, blank=True)    
#    locations = models.TextField(verbose_name='Please list all the different locations you have lived in at different ages (not including travels):')
#    hometown_street = models.CharField(verbose_name='Street', max_length=100)
#    hometown_city_state = models.CharField(verbose_name='City/State', max_length=100)
#    hometown_zip_code = models.CharField(verbose_name='Zip Code', max_length=100)
#    hometown_not_us = models.CharField(verbose_name='If not US, please state home country', max_length=100, blank=True)
    religion = models.CharField(verbose_name='What is your religious background?', max_length=20, choices=RELIGION_CHOICES)
#    religion_community = models.BooleanField(verbose_name='Do you consider yourself part of a religious community (e.g., church, mosque, temple)?')
#    religion_community_ethnic = models.CharField(blank=True, max_length=100, verbose_name='If yes, what specific ethnic group does the community cater to?')
    friends = models.SmallIntegerField(verbose_name='How many close friends would you say you have (Use a WHOLE number, NOT a range)?')
    friends_asian = models.SmallIntegerField(verbose_name='% Asian/Asian American friends')
    friends_black = models.SmallIntegerField(verbose_name='% Black/African-American')
    friends_white = models.SmallIntegerField(verbose_name='% White/European American')
    friends_latino = models.SmallIntegerField(verbose_name='% Latino/a or Hispanic')
    friends_native_american = models.SmallIntegerField(verbose_name='% Native American')
    friends_bi_asian = models.SmallIntegerField(verbose_name='% Biracial/multiracial Asian friends')
    friends_bi_nonasian = models.SmallIntegerField(verbose_name='% Biracial/multiracial non-Asian friends')
    partners = models.SmallIntegerField(verbose_name='How many romantic partners would you say you have had (Use a WHOLE number, NOT a range)?')
    partners_asian = models.SmallIntegerField(verbose_name='% Asian/Asian American partners')
    partners_black = models.SmallIntegerField(verbose_name='% Black/African-American')
    partners_white = models.SmallIntegerField(verbose_name='% White/European American')
    partners_latino = models.SmallIntegerField(verbose_name='% Latino/a or Hispanic')
    partners_native_american = models.SmallIntegerField(verbose_name='% Native American')
    partners_bi_asian = models.SmallIntegerField(verbose_name='% Biracial/multiracial Asian partners')
    partners_bi_nonasian = models.SmallIntegerField(verbose_name='% Biracial/multiracial non-Asian partners')
    courses = models.SmallIntegerField(verbose_name='How many college courses have you taken on the topic of racial or ethnic diversity or racial or ethnic studies?')
#    courses_identity = models.SmallIntegerField(verbose_name='Besides Asian American Studies courses, how many college courses have you taken because you thought they would help you understand your racial identity?')
    
    def __unicode__(self):
        return "Sub %s" % (self.submission_id)
