from rest_framework import serializers
from .models import *

class AttendenceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendenceStatus
        fields = ['id', 'name', 'acronym', 'deleted']


class AttendenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendence
        fields = '__all__'
