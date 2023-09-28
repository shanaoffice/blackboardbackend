from rest_framework import serializers
from .models import *
import os
import json
from typing import Any
from django.contrib.contenttypes.models import ContentType

class PayrollProcessedSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollProcessed
        fields = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
 
class SalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = '__all__' 

    def __init__(self,emp_id, **kwargs):
        super().__init__(**kwargs)
        self.emp_id= emp_id
        self.file_path= os.path.join(os.path.dirname(__file__), 'config.json')
        with open(self.file_path) as config_file:
            self.config_data = json.load(config_file) 

    def to_representation(self, instance):
        data = super().to_representation(instance)
        updated_data = {}

        for key, value in data.items():
            if value == "custom":
                if key in self.config_data:
                    custom_config = self.config_data[key]
                    model_name = custom_config[value]["model"]
                    modal = globals()[model_name]
                    serializer = custom_config[value]["serializer"]
                    serializer = globals()[serializer]
                    instance = modal.objects.all()
                    serializer = serializer(instance=instance, many=True)
                    updated_data[model_name]=serializer.data
            elif value == "manual":
                if key in self.config_data:
                    custom_config = self.config_data[key]
                    model_name = custom_config[value]["model"]
                    modal = globals()[model_name]
                    serializer = custom_config[value]["serializer"]
                    serializer = globals()[serializer]
                    instance = modal.objects.filter(employee=self.emp_id)
                    serializer = serializer(instance=instance, many=True)
                    updated_data[model_name]=serializer.data
        data.update(updated_data)
        return data

class CustomPayDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPayDeduction
        fields = '__all__'  
        

class CustomPayAllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPayAllowance
        fields = '__all__' 

class ManualPayDeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualPayDeduction
        fields = '__all__'  
        

class ManualPayAllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualPayAllowance
        fields = '__all__' 

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__' 

class SalaryHistoryAllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryHistoryAllowance
        fields = '__all__'

    def to_internal_value(self, data):
        amount= round((self.context.get("basic")* float(data["allowance_percentage"]) / 100))
        model_name= self.context.get("model")
        model_name = globals()[model_name]
        content_type = ContentType.objects.get_for_model(model_name)
        internal_data= {
            "salary_history":int(self.context.get("id")),
            "content_type": content_type.id,
            "object_id" : int(data["id"]),
            "amount": amount
        }
        print(internal_data)
        return super().to_internal_value(internal_data)

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        
class SalaryHistoryDeductionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryHistoryDeduction
        fields = '__all__'

    def to_internal_value(self, data):
        amount= round((self.context.get("basic")* float(data["deduction_percentage"]) / 100),2)
        model_name= self.context.get("model")
        model_name = globals()[model_name]
        content_type = ContentType.objects.get_for_model(model_name)
        internal_data= {
            "salary_history":int(self.context.get("id")),
            "content_type": content_type.id,
            "object_id" : int(data["id"]),
            "amount": amount
        }
        return super().to_internal_value(internal_data)

class SalaryHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SalaryHistory
        fields = '__all__'

    def to_internal_value(self, data):
        internal_data= {
            "employee":data["employee"],
            "salary_month": self.context.get('month'),
            "financial_year": self.context.get('year'),
            "worked_days": self.context.get('salary')[1],
            "basic_pay": data["basic_pay"],
            "net_salary": self.context.get('salary')[0],
                    }
        return super().to_internal_value(internal_data)
    
    def to_representation(self, instance):
        data= super().to_representation(instance)
        return data

