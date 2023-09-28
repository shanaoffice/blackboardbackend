from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
import jwt
from datetime import datetime, timedelta, date
import time
from .serializers import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from .models import *
from rest_framework import generics
from django.utils.crypto import get_random_string


# class WorkInfUpdateAPIView(APIView):

#     def put(self):
#         username = self.kwargs.get(self.lookup_field)
#         return WorkInf.objects.get(employee_work__username=username)


class WorkInfUpdateAPIView(generics.UpdateAPIView):
    queryset = WorkInf.objects.all()
    serializer_class = WorkInfSerializer
    lookup_field = 'pk'  # Use 'pk' to identify the object

    def get_object(self):
        # Retrieve the WorkInf object based on the primary key (pk) provided in the URL
        return WorkInf.objects.get(pk=self.kwargs.get('pk'))

    def update_shift_entry(self, user, team):
        team_shifts = TeamShift.objects.filter(Q(team_id=team) & Q(to_date__gte=date.today())).order_by('from_date')
        employee_instance = CustomUser.objects.get(id=user)
        for team_shift in team_shifts:
            start_date = max(team_shift.from_date, date.today())
            end_date = team_shift.to_date
            delta = timedelta(days=1)
            current_date = start_date
            while current_date <= end_date:
                EmployeeShift.objects.create(date=current_date, employee=employee_instance, shift=team_shift.shift)
                current_date += delta

                
class UserRegisterView(APIView):
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            generated_password = get_random_string(length=12)
            user.set_password(generated_password)
            user.save()
            EmployeeGeneric(employee_s=user).save()
            EmployeeAddress(employee_a=user).save()
            EmployeePersonalDetails(employee_p=user).save()
            WorkInf(employee_work=user).save()

            # team_id = request.data.get('team')
            # if team_id:
            #     self.update_shift_entry(user.pk,team_id)
            send_password_email(request, user,generated_password)
            return Response({'message': 'Registration successful', 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            role = user.role
            response_data = {
                'access_token': str(access_token),
                'refresh_token': str(refresh_token),
                'role': role,
            }
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def transform_data(data):
    transformed_data = {}
    for entry in data:
        date_str = entry["attendance_date"]
        in_time_str = entry["check_in_time"]
        out_time_str = entry["check_out_time"]
        if date_str not in transformed_data:
            transformed_data[date_str] = {
                "First In": in_time_str,
                "Last Out": out_time_str,
                "Total In Time": 0,
            }
        in_time = datetime.datetime.strptime(in_time_str, "%H:%M:%S")
        out_time = datetime.datetime.strptime(out_time_str, "%H:%M:%S") if out_time_str else datetime.datetime.strptime(f"1900-01-01 {datetime.datetime.now().strftime('%H:%M:%S')}", "%Y-%m-%d %H:%M:%S")
        time_difference = (out_time - in_time).total_seconds()
        transformed_data[date_str]["Total In Time"] += time_difference
        transformed_data[date_str]["Last Out"] = out_time_str if out_time_str else "N/A"
    for date in transformed_data:
        transformed_data[date]["Total In Time"] = convert(
            transformed_data[date]["Total In Time"]
        )
    return transformed_data

def transform_data1(data):
    converted_data = {}
    for date, entries in data.items():
        first_in = entries[0]["check-In"]
        last_out = entries[-1].get("check-out", "N/A")
        total_in_time = 0
        for entry in entries:
            check_in_time = datetime.strptime(entry["check-In"], "%H:%M:%S")
            check_out_time_str = entry.get("check-out")
            
            if check_out_time_str:
                check_out_time = datetime.strptime(check_out_time_str, "%H:%M:%S")
                in_time = check_out_time - check_in_time
                total_in_time += in_time.total_seconds()

        converted_data[date] = {
            "First In": first_in,
            "Last Out": last_out,
            "Total In Time": str(total_in_time)
        }
    return converted_data

from django.db.models import Q 
from django.utils import timezone

class EsslAttendanceView(APIView):
    def get(self, request,user_id,start_date,end_date=None):
        try:
            start_date= datetime.strptime(start_date, "%Y-%m-%d")
            start_time = datetime(start_date.year,start_date.month,start_date.day, 0, 0, 0)
            if end_date==None:
                end_time = datetime(start_date.year,start_date.month, start_date.day, 23, 59, 59)
            else:
                end_date= datetime.strptime(end_date, "%Y-%m-%d")
                end_time = datetime(end_date.year,end_date.month, end_date.day, 23, 59, 59)
            queryset = DeviceLogProcessed.objects.filter(UserId=user_id,LogDate__range=(start_time,end_time)).order_by('LogDate')
            serializer = DeviceLogProcessedSerializer(queryset, many=True)
            transformed_data = serializer.data
            return Response(transformed_data)
        except Exception as e:
            return Response('Invalid Request', status=404)


class ShiftView(generics.ListCreateAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer

from rest_framework import generics
from collections import defaultdict
       
class EmployeeList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class ShiftDetails(APIView):
    def get(self, request):
        type=request.GET.get("type")
        from_date = request.GET.get("from")
        to_date = request.GET.get("to")
        if type=="team":
            team_obj = TeamShift.objects.filter(Q(date__range=(from_date, to_date))).order_by('team')
            serializer= TeamShiftSerializer(team_obj, many=True)
            return Response(serializer.data)
        elif type=="employee":
            employee = CustomUser.objects.all()
            shifts = EmployeeShift.objects.filter(Q(employee_id__in=employee) & Q(date__range=(from_date, to_date))).order_by('date')
            serializer = ShiftSerializer(shifts, many=True)
            return Response(serializer.data)
    
    def post(self,request,type=None,method=None ):
            data = request.data
            if type == "team":
                for item in data:
                    team = item.get("team_id")
                    #  team = get_object_or_404(Team, name=team_name)
                    if method:
                        from_date = datetime.strptime(item.get("from_date"), "%Y-%m-%d").date()
                        to_date = datetime.strptime(item.get("to_date"), "%Y-%m-%d").date()
                        TeamShift.objects.filter(team_id=team,date__range=[from_date, to_date]).delete()
                        new_shifts = []
                        current_date = from_date
                        while current_date <= to_date:
                            shift_instance = Shift.objects.get(pk=item.get("shift"))
                            new_shift = TeamShift(date=current_date,team_id=team,shift= shift_instance)
                            new_shifts.append(new_shift)
                            current_date += timedelta(days=1)
                        TeamShift.objects.bulk_create(new_shifts)
                        # employees = CustomUser.objects.filter(team=team)
                        employees = CustomUser.objects.filter(workinf__team__name=team)
                        for employee in employees:
                            new_employee_shifts = []
                            for shift_date in new_shifts:
                                new_employee_shift = EmployeeShift(date=shift_date.date, employee_id=employee, shift=shift_instance)
                                new_employee_shifts.append(new_employee_shift)
                            EmployeeShift.objects.bulk_create(new_employee_shifts)
                    else:
                        date = datetime.strptime(item.get("date"), "%Y-%m-%d").date()
                        TeamShift.objects.filter(team_id=team,date=date).delete()
                        TeamShift.objects.create(date=date,team_id=team,shift= item.get("shift"))
                        employees = CustomUser.objects.filter(team=team)
                        for employee in employees:
                            EmployeeShift.objects.create(date=date, employee_id=employee, shift=item.get("shift"))
                return Response({'message': 'update successful'}, status=status.HTTP_201_CREATED)
            elif type == "employee":
                for item in data:
                     emp_id = item.get("emp_id")
                     from_date = datetime.strptime(item.get("from_date"), "%Y-%m-%d").date()
                     to_date = datetime.strptime(item.get("to_date"), "%Y-%m-%d").date()
                     EmployeeShift.objects.filter(employee_id=emp_id,date__range=[from_date, to_date]).delete()
                     new_shifts = []
                     current_date = from_date
                     while current_date <= to_date:
                        new_shift = EmployeeShift(date=current_date,employee_id=emp_id,shift= item.get("shift"))
                        new_shifts.append(new_shift)
                        current_date += timedelta(days=1)
                     EmployeeShift.objects.bulk_create(new_shifts)
                return Response({'message': 'update successful'}, status=status.HTTP_201_CREATED)
       
import requests

def transform_data99(data):
    transformed_data = {}
    current_date = None
    current_day_data = []
    check_in_time = None
    total_in_time = timedelta()


    for entry in data:
        log_date = datetime.strptime(entry["LogDate"], "%Y-%m-%d %H:%M:%S")
        day_key = log_date.strftime("%d-%m-%Y")
        if day_key != current_date:
            if current_date:
                transformed_data[current_date] = current_day_data
                # if check_in_time:
                #     transformed_data["check_in"] = True
            current_date = day_key
            current_day_data = []
            check_in_time = None
        time = log_date.strftime("%H:%M:%S")
        if not check_in_time:
            check_in_time = time
            current_day_data.append({"check-In": check_in_time})
        else:
            current_day_data.remove({"check-In": check_in_time})
            current_day_data.append({"check-In": check_in_time, "check-out": time})
            time= datetime.strptime(time, '%H:%M:%S')
            check_in_time = datetime.strptime(check_in_time, '%H:%M:%S')
            time_difference = time - check_in_time
            total_in_time+=time_difference
            check_in_time = None
    if current_date:
        transformed_data[current_date] = current_day_data
    transformed_data["Total In time"] = total_in_time
    return transformed_data

class AttendanceView(APIView):
    def get(self, request,user_id,start_date,end_date=None):
        try:
            if end_date==None:
                api_url = f"http://192.168.0.204:8001/esslattendance/{user_id}/{start_date}"
            else:
                api_url = f"http://192.168.0.204:8001/esslattendance/{user_id}/{start_date}/{end_date}"
            response = requests.get(api_url)
            transformed_data= transform_data99(response.json())
            # return Response(response.json())
            

            if end_date:
                del transformed_data["Total In time"]
                transformed_data=transform_data1(transformed_data)
                return Response(transformed_data)
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date = start_date.strftime('%d-%m-%Y')
            if "check-out" in transformed_data[start_date][-1]:
                Last_check = transformed_data[start_date][-1]["check-out"]
            else:
                Last_check = transformed_data[start_date][-1]["check-In"]
                transformed_data["check_in"] = True
            
            transformed_data["Last_check"] = Last_check
            return Response(transformed_data)
            
        except Exception as e:
            return Response('Invalid Request', status=404)
        
    
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(User, email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = reverse('password_reset_confirm', args=[uid, token])
            reset_url = request.build_absolute_uri(reset_link)
            subject = 'Password Reset'
            message = f'Click the following link to reset your password: {reset_url}'
            from_email = settings.PASSWORD_RESET_FROM_EMAIL,
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request, token, uidb64):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    new_password = serializer.validated_data['new_password']
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TeamListCreateView(generics.ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def post(self, request, *args, **kwargs):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
         
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.generics import  RetrieveUpdateDestroyAPIView

class  TeamListCreateRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Team updated successfully"}, status=status.HTTP_200_OK)

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.delete()
    #     return Response({"message": "Team deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


import logging

def your_attendance_view_function():
    logging.basicConfig(filename='D:/Varjinth/test3/Scripts/board/board/logfile.log', level=logging.INFO)
    logging.info('i am executed')
    print("i am executed")


# def send_password_reset_email(request, user, password):
#     token_generator = PasswordResetTokenGenerator()
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     token = token_generator.make_token(user)
#     password_reset_url = f'http://localhost:3000/passwordreset/{uid}/{token}/'
#     context = {
#         'protocol': request.scheme,
#         'domain': request.get_host(),
#         'uid': uid,
#         'token': token,
#         'reset_url': password_reset_url
#     }
#     password_reset_email_template = render_to_string('password_reset_email.html', context)

#     send_mail(
#         subject='Password Reset Request',
#         message='',
#         from_email=settings.PASSWORD_RESET_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=password_reset_email_template
#     )

def send_password_email(request, user, password):
    password_reset_email_template = render_to_string('password_reset_email.html', {'user':user, 'password': password})

    send_mail(
        subject='New Account Information',
        message='',
        from_email=settings.PASSWORD_RESET_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=password_reset_email_template
    )


# class EmployeeDailyAttendanceView(APIView):
#     # permission_classes = [IsAuthenticated]
#     def post(self, request,pk=None):
#         serializer = EmployeeDailyAttendanceSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
    
#     def get(self, request,pk=None):
#         query_params = request.GET.dict()
#         try:
#             if pk!=None:
#                 from_date_str = query_params.get('from')
#                 to_date_str = query_params.get('to')
#                 if from_date_str and to_date_str:
#                     from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d')
#                     to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d')
#                     queryset = EmployeeDailyAttendance.objects.filter(employee=pk,attendance_date__gte=from_date,attendance_date__lte=to_date)
#                     serializer = EmployeeDailyAttendanceSerializer(queryset, many=True)
#                     transformed_data = transform_data(serializer.data)
#                     return Response(transformed_data)
#                 else:
#                     queryset = EmployeeDailyAttendance.objects.filter(employee=pk,**query_params)
#                 serializer = EmployeeDailyAttendanceSerializer(queryset, many=True)
#                 total_in_time = timedelta()
#                 transformed_data = {"employee": pk,
#                                     "Daywise attendance details": {}}
#                 for item in serializer.data:
#                     date_key = item['attendance_date']
#                     del item['attendance_date']
                    
#                     if date_key not in transformed_data['Daywise attendance details']:
#                         transformed_data['Daywise attendance details'][date_key] = {
#                             "check_log": []
#                         }
#                     transformed_data['Daywise attendance details'][date_key]['check_log'].append(item)
#                     check_in_time = datetime.datetime.strptime(item['check_in_time'], '%H:%M:%S')
#                     if item['check_out_time']:
#                         check_out_time = datetime.datetime.strptime(item['check_out_time'], '%H:%M:%S')
#                     else:
#                         check_out_time = datetime.datetime.strptime(item['check_in_time'], '%H:%M:%S')
#                     time_difference = check_out_time - check_in_time
#                     total_in_time+=time_difference
#                 transformed_data['total_in_time'] = (total_in_time)
#                 if (serializer.data[-1]['check_out_time']):
#                     Last_check= serializer.data[-1]['check_out_time']
#                 else:
#                     Last_check= serializer.data[-1]['check_in_time']
#                     transformed_data["check_in"] = True
#                 transformed_data["Last_check"] = Last_check 
#             else:
#                 queryset = EmployeeDailyAttendance.objects.filter(**query_params)
#                 serializer = EmployeeDailyAttendanceSerializer(queryset, many=True)
#                 transformed_data = serializer.data
#             return Response(transformed_data)
#         except Exception as e:
#             return Response('Invalid Request', status=404)
    
#     def put(self, request,pk=None):
#         query_params = request.GET.dict()
#         try:
#             if pk!=None:
#                 queryset = EmployeeDailyAttendance.objects.filter(pk=pk,**query_params)
#             else:
#                 queryset = EmployeeDailyAttendance.objects.filter(**query_params)
#             instance = queryset.get()
#             serializer = EmployeeDailyAttendanceSerializer(instance,data=request.data)
#         except Exception as e:
#             return Response('Invalid Request', status=404)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Update successful'})
#         return Response(serializer.errors, status=400)

from typing import Any
import json
import os
from django.http import JsonResponse


def flatten_data(data_list):
    flattened_list=[]
    for data in data_list:
        flattened_data = {}
        for key,value in data.items():
            for  key1,value1 in value.items():
                if key1 not in flattened_data:
                    flattened_data[key1]=value1
        flattened_list.append(flattened_data)
    return(flattened_list)


class MyView(APIView):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.file_path= os.path.join(os.path.dirname(__file__), 'config.json')
        with open(self.file_path) as config_file:
            self.config_data = json.load(config_file)

    def get(self, request, resource_path,pk=None):
        for entry in self.config_data:
            if entry['ResourcePath'] == resource_path:
                model= entry['ObjectToReturn']
                fields= entry['fields']
                field_name_mapping = entry['field_name_mapping']
                foreign_key= entry['foreign_key']
                onetoone = entry['one_to_one']
                exclude = entry["exclude"]
                break
        else:
            return Response('Invalid Request', status=404)
        try:
            model_class = globals()[model]
            query_params = request.GET.dict()
            if pk is not None:
                filtered_objects = model_class.objects.filter(pk=pk, **query_params)
                serialized_data = GenericSerializer(instance=filtered_objects,model=model_class,fields=fields,field_name_mapping=field_name_mapping,foreign_key=foreign_key,onetoone=onetoone, exclude= exclude, many=True).data[0]
                data = serialized_data
            else:
                filtered_objects = model_class.objects.filter(**query_params)
                serialized_data = GenericSerializer(instance=filtered_objects,model=model_class,fields=fields,field_name_mapping=field_name_mapping,foreign_key=foreign_key,onetoone=onetoone, many=True).data
                serialized_data= flatten_data(serialized_data)
                data = { 'Total_count' : len(serialized_data),'content':serialized_data}
            return JsonResponse(data, status=200)
            
        except:
            return Response('Invalid Request', status=404)
    
    def post(self, request, resource_path):
        for entry in self.config_data:
            if entry['ResourcePath'] == resource_path:
                model = entry['ObjectToReturn']
                fields = entry['fields']
                field_name_mapping = entry['field_name_mapping']
                break
        else:
            return Response({'message': 'Invalid Request'}, status=status.HTTP_404_NOT_FOUND)

        model_class = globals()[model]
        serializer = GenericSerializer(model=model_class, data=request.data, fields=fields, field_name_mapping=field_name_mapping)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Created successfully'}, status=status.HTTP_201_CREATED)
        else:
            errors = json.dumps(serializer.errors)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self,request,resource_path, pk=None):
        for entry in self.config_data:
            if entry['ResourcePath'] == resource_path:
                model= entry['ObjectToReturn']
                fields= entry['fields']
                field_name_mapping = entry['field_name_mapping']
                foreign_key= entry['foreign_key']
                break
        else:
            return Response('Invalid Request', status=404)
        try:
            model_class = globals()[model]
            query_params = request.GET.dict()
            if pk is not None:
                filtered_objects = model_class.objects.filter(pk=pk, **query_params)
            else:
                filtered_objects = model_class.objects.filter(**query_params)
            instance = filtered_objects.get()
        except:
            return Response('Invalid Request', status=404)
        serializer = GenericSerializer(instance=instance,model=model_class,data=request.data,fields=fields,field_name_mapping=field_name_mapping,foreign_key=foreign_key)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Update successful'})
        else:
            return Response(serializer.errors, status=400)
    
    def post(self,request,resource_path, pk=None):
        for entry in self.config_data:
            if entry['ResourcePath'] == resource_path:
                model= entry['ObjectToReturn']
                fields= entry['fields']
                field_name_mapping = entry['field_name_mapping']
                foreign_key= entry['foreign_key']
                break
        else:
            return Response('Invalid Request', status=404)
        model_class = globals()[model]
        serializer = GenericSerializer(model=model_class,data=request.data,fields=fields,field_name_mapping=field_name_mapping,foreign_key=foreign_key)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Created successfully'})
        else:
            return Response(serializer.errors, status=400)
        

    def delete(self, request, resource_path, pk=None):
        for entry in self.config_data:
            if entry['ResourcePath'] == resource_path:
                model= entry['ObjectToReturn']
                break
        else:
            return Response('Invalid Request', status=404)
        model_class = globals()[model]
        query_params = request.GET.dict()
        filtered_objects = model_class.objects.filter(**query_params)
        filtered_objects.delete()
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)



class NotificationsView(APIView):
    def get(self, request, id):
        try:
            emp_id = int(id)  # Ensure recipient_id is an integer
            notifications = Notification.objects.filter(to=emp_id, read=False)  # Customize filter criteria as needed
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid recipient_id'}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Notification created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id):
        try:
            notification = Notification.objects.get(pk=id)
        except Notification.DoesNotExist:
            return Response({'message': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(notification, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Notification updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeShiftView(APIView):

    def get(self, request):
        employee_shifts = EmployeeShift.objects.all()
        serializer = EmployeeShiftSerializer(employee_shifts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = EmployeeShiftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        employee_shift = self.get_object(pk)
        serializer = EmployeeShiftSerializer(employee_shift, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


