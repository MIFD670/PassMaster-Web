from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class Read_PassSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='pass_type')

    class Meta:
        model = Pass
        fields = ('approved',
                    'date',
                    'startTimeRequested',
                    'endTimeRequested',
                    'timeLeftOrigin',
                    'timeArrivedDestination',
                    'student',
                    'originTeacher',
                    'description',
                    'type')

class StudentCreate_LocationPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationPass
        fields = ('date',
                    'startTimeRequested',
                    'endTimeRequested',
                    'student',
                    'originTeacher',
                    'description',
                    'location')

class StudentCreate_SRTPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SRTPass
        fields = ('date',
                    'startTimeRequested',
                    'endTimeRequested',
                    'student',
                    'originTeacher',
                    'description',
                    'session',
                    'destinationTeacher')

class StudentCreate_TeacherPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPass
        fields = ('date',
                    'startTimeRequested',
                    'endTimeRequested',
                    'student',
                    'originTeacher',
                    'description',
                    'destinationTeacher')

