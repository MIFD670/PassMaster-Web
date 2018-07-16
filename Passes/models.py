from django.db import models
from datetime import datetime

from Student.models import Student
from Teacher.models import Teacher
from django.utils.timezone import now


# Create your models here.
class Pass(models.Model):
    objects = models.Manager()

    approved = models.BooleanField(default=False) #"""always needed, will be approved by destination teacher if its a teacher pass, or the origin teacher if its an other pass"""

    startTimeRequested = models.DateTimeField() #"""always needed"""
    endTimeRequested = models.DateTimeField() #"""always needed"""

    timeLeftOrigin = models.DateTimeField(null=True, blank=True) #"""always needed"""
    timeArrivedDestination = models.DateTimeField(null=True, blank=True) # needed only for pass type #1
    #timeDepartedDestination = models.DateTimeField(null=True) # needed only for pass type #1
    #timeReturnedOrigin = models.DateTimeField(null=True) # needed only for session 1 SRT passes and other passes


    #"""A teacher pass is where a teacher is at the destination to record the student's arrival (also applicable to things like the nurse's office)
    #An 'other' pass is where there is no one to sign student's in, such as the restroom"""
    PASS_TYPE_CHOICES = (('1', "Teacher Pass"), ('2', "Other Pass"),)# (3, "Destination Pass"))
    type = models.CharField(max_length=48, choices=PASS_TYPE_CHOICES)

    #SESSION_CHOICES = ((1, "Session 1"),(2, "Session 2"),(3, "Both Sessions"))
    #session = models.CharField(max_length=48, choices=SESSION_CHOICES, null=True)

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="pass_student"
    )

    originTeacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="pass_origin_teacher"
    )

    #""" Basically the location and destinationTeacher are interchangeable. There will only be one or the other --
    #a location if the pass is an other pass and a destinationTeacher if the pass is a teacher pass"""

    location = models.CharField(max_length=12, null=True, blank=True)

    destinationTeacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="destinationTeacher"
    )

    #""" The String description of the reason for the pass. This is mainly just for the destination teacher to know what the
    #student will need from them. """
    description = models.CharField(max_length=960, null=True)

    def __str__(self):
        return self.description


    def approve(self):
        self.approved = True
        self.save()

    def leave(self):
        self.timeLeftOrigin = datetime.now()
        self.save()

    def arrive(self):
        if (self.type == '1'):
            self.timeArrivedDestination = datetime.now()
            self.save()
    #def return(self):
    #    self.timeReturned = datetime.now()

    def has_left(self):
        return self.timeLeft != None

    def has_arrived(self):
        return self.timeArrived != None

    #def has_returned(self):
        #return self.timeReturned != None

    def get_students_active_passes(user):
        profile = user.profile
        if profile.is_student:
            student = profile.student
            return Pass.objects.filter(student=student, approved=True, timeArrivedDestination=None)
        else:
            return None

    def get_students_pending_passes(user):
        profile = user.profile
        if profile.is_student:
            student = profile.student
            return Pass.objects.filter(student=student, approved=False, timeArrivedDestination=None)
        else:
            return None

    def get_students_old_passes(user):
        profile = user.profile
        if profile.is_student:
            student = profile.student
            return Pass.objects.filter(student=student, approved=True).exclude(timeArrivedDestination=None)
        else:
            return None

    def get_teachers_incoming_student_passes(user):
        profile = user.profile
        if profile.is_teacher:
            teacher = profile.teacher
            return Pass.objects.filter(approved=True, timeArrivedDestination=None, destinationTeacher=teacher)
        else:
            return None

    def get_teachers_outgoing_student_passes(user):
        profile = user.profile
        if profile.is_teacher:
            teacher = profile.teacher
            return Pass.objects.filter(approved=True, timeArrivedDestination=None, originTeacher=teacher)
        else:
            return None


    def get_teachers_unapproved_passes(user):
        profile = user.profile
        if profile.is_teacher:
            teacher = profile.teacher
            teacher_passes = Pass.objects.filter(type='1', approved=False, timeLeftOrigin=None, timeArrivedDestination=None, destinationTeacher=teacher)
            other_passes = Pass.objects.filter(type='2', approved=False, timeLeftOrigin=None, timeArrivedDestination=None, originTeacher=teacher)

            passes = teacher_passes | other_passes
            return passes
        else:
            return None

    def get_teachers_old_passes(user):
        profile = user.profile
        if profile.is_teacher:
            teacher = profile.teacher
            passes = Pass.objects.filter(approved=True, destinationTeacher=teacher).exclude(timeArrivedDestination=None) | Pass.objects.filter(approved=True, originTeacher=teacher).exclude(timeArrivedDestination=None)
            return passes
        else:
            return None
