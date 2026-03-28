from rest_framework import serializers
from fireapp import models

class ManagerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Manager
        fields = '__all__'
