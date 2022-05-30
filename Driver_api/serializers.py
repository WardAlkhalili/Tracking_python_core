from rest_framework import serializers
from Driver_api import models

class ManagerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Manager
        fields = '__all__'
