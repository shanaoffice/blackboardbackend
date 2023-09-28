from rest_framework import serializers, generics
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import *
import datetime
User = get_user_model()



class WorkInfSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkInf
        fields = ['employee_id', 'device_id', 'team', 'hr_partner']
    # Define custom update method to handle form data
    def update(self, instance, validated_data):
        instance.employee_id = validated_data.get('Employee ID', instance.employee_id)
        instance.device_id = validated_data.get('Device ID', instance.device_id)
        instance.team = validated_data.get('Team', instance.team)
        instance.hr_partner = validated_data.get('HR Admin', instance.hr_partner)
        instance.save()
        print(instance)
        return instance


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    # password = serializers.CharField( required=True, validators=[validate_password])
    # role = serializers.CharField( required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name','email',"role"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        email = validated_data['email']
        validated_data['username'] = email
        # validated_data['email'] = email
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError('User with this email already exists.')
        user = User.objects.create_user(**validated_data)
        return user
          
    
    
    # def update(self, instance, validated_data):
    #     # Check if 'username' and 'password' are provided
    #     if 'username' in validated_data:
    #         instance.username = validated_data['username']
    #     if 'password' in validated_data:
    #         instance.set_password(validated_data['password'])

    #     # Save the instance
    #     instance.save()
    #     return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = [ 'email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user:
                if user.check_password(password):
                    return user
                else:
                    raise serializers.ValidationError('Incorrect password')
            else:
                raise serializers.ValidationError('Email ID not registered')
        else:
            raise serializers.ValidationError('Both email and password are required.')

class CustomDateField(serializers.DateField):
    def to_representation(self, value):
        return value.strftime('%d-%m-%Y')
    def to_internal_value(self, value):
        try:
            formatted_date = datetime.datetime.strptime(value, "%d-%m-%Y").date()
            return super().to_internal_value(formatted_date)
        except ValueError:
            raise serializers.ValidationError("Date has wrong format. Use the format 'DD-MM-YYYY'.")
        
class EmployeeDailyAttendanceSerializer(serializers.ModelSerializer):
    attendance_date = CustomDateField(required=False)
    class Meta:
        model = EmployeeDailyAttendance
        fields = '__all__'


class CustomDateField1(serializers.DateField):
    def to_representation(self, value):
        value = value.strftime("%Y-%m-%d %H:%M:%S")
        return value
    
class DeviceLogProcessedSerializer(serializers.ModelSerializer):
    LogDate= CustomDateField1()
    
    class Meta:
        model = DeviceLogProcessed
        fields = ["LogDate"]


class TeamShiftSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    shift = serializers.CharField(source='shift.ShiftName', read_only=True)

    class Meta:
        model = TeamShift
        fields = ['id', 'team','team_name', 'date', 'shift']


class ShiftSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee_id.first_name', read_only=True)
    class Meta:
        model = EmployeeShift
        fields = ['id','employee_name', 'employee_id','date', 'shift']

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'   

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name','role', ]

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'



from rest_framework import serializers
from .models import *

from rest_framework.exceptions import ValidationError


class GenericSerializer(serializers.ModelSerializer):
    hr_partner= serializers.CharField(source='hr_partner.first_name', read_only=True)

    class Meta:
        model = None
        fields = '__all__'
        

    def __init__(self, model=None, fields=None,exclude=None, field_name_mapping=None,foreign_key=None,onetoone=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.model = model
        self.Meta.fields = fields
        self.exclude = exclude
        self.field_name_mapping= field_name_mapping
        self.foreign_key= foreign_key
        self.onetoone= onetoone
        print(model)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        transformed_data={}
        summary={}
        for field, value in data.items():
            print(field,value)
            if field in self.exclude:
                continue
            if field in self.foreign_key.keys() and value:
                # continue
                mod = self.foreign_key[field]
                mod = globals()[mod]
                value = str(mod.objects.get(pk=value))
            transformed_field = self.field_name_mapping.get(field, field)
            summary[transformed_field] = value

        transformed_data["Summary"]=summary
        for related_model in self.onetoone:
            model = globals()[related_model]
            related_instance = getattr(instance, related_model.lower(), None)
            if related_instance:
                serializer = GenericSerializer(
                    instance=related_instance,
                    model=model,
                    fields=self.Meta.fields,
                    field_name_mapping=self.field_name_mapping,
                    foreign_key=self.foreign_key,
                    onetoone=self.onetoone,
                    exclude= self.exclude
                )
                transformed_field = self.field_name_mapping.get(related_model, field)

                transformed_data[transformed_field] = serializer.data["Summary"]

        return transformed_data
    
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     transformed_data={}
    #     init={}
    #     for field, value in data.items():
    #         if field in self.foreign_key.keys():
    #             continue
    #             # mod = self.foreign_key[field]
    #             # mod = globals()[mod]
    #             # value = str(mod.objects.get(pk=value))
    #         transformed_field = self.field_name_mapping.get(field, field)
    #         init[transformed_field] = value
    #     initField = self.field_name_mapping.get(self.Meta.model.__name__)
    #     transformed_data[initField]=init
    #     for related_model in self.onetoone:
    #         model = globals()[related_model]
    #         related_instance = getattr(instance, related_model.lower(), None)
    #         if related_instance:
    #             serializer = GenericSerializer(
    #                 instance=related_instance,
    #                 model=model,
    #                 fields=self.Meta.fields,
    #                 field_name_mapping=self.field_name_mapping,
    #                 foreign_key=self.foreign_key,
    #                 onetoone=self.onetoone
    #             )
    #             transformed_field = self.field_name_mapping.get(related_model)
    #             transformed_data[transformed_field] = serializer.data[transformed_field]
    #     return transformed_data
   
    def to_internal_value(self, data):
        internal_data = {}

        for field, value in data.items():
            original_field = next((k for k, v in self.field_name_mapping.items() if v == field), None)
            if original_field is None:
                raise ValidationError( {"field":f"{field} not found"})
            if original_field in self.foreign_key.keys():
                mod = self.foreign_key[original_field]
                mod = globals()[mod]
                try:
                    obj = mod.objects.get(name=value)
                    value = obj.pk
                except mod.DoesNotExist:
                    raise serializers.ValidationError(f"Invalid {original_field}: {value}")
            internal_data[original_field] = value
        
        return super().to_internal_value(internal_data)
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
    

class EmployeeShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShift
        fields = '__all__'


    














        
