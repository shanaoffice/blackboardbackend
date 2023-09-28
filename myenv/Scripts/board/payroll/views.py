from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
import calendar, datetime, requests, os, json
from django.http import JsonResponse
from rest_framework import generics, status
from django.db.models import Q
from users.models import DeviceLogProcessed, EmployeeShift, Shift, Notification
from django.utils import timezone
from django.http import HttpResponse



def task(request):
    employees = CustomUser.objects.all()
    for employee in employees:
        employee_shift = EmployeeShift.objects.filter(employee_id=employee, date=datetime.date.today()).first()
        if employee_shift:
            shift_timing = employee_shift.shift
            shift_start_time = shift_timing.start_time
            shift_end_time = shift_timing.end_time
            punch_log = DeviceLogProcessed.objects.filter(LogDate__date=datetime.date.today(), UserId=employee.device_id).order_by('LogDate')
            # last_punch_log = DeviceLog.objects.filter(LogDate__date=datetime.date.today(), UserId=employee.device_id).order_by('-LogDate').first()
            if len(punch_log)>=2:
                in_time_difference = punch_log[0].LogDate - datetime.datetime.combine(datetime.date.today(), shift_start_time)
                total_time_difference = punch_log[(len(punch_log)-1)].LogDate - datetime.datetime.combine(datetime.date.today(), shift_start_time)
                if in_time_difference.total_seconds() <= (10 * 60):
                    if total_time_difference.total_seconds() >= (410 * 60):
                        employee_shift.attendance_status = "Present"
                    elif (150 * 60) <= total_time_difference.total_seconds() < (410 * 60):
                        employee_shift.attendance_status = "Halfday"
                    else:
                        employee_shift.attendance_status = "Absent"
                elif (10 * 60) < in_time_difference.total_seconds() <= (60 * 60):
                    current_date = datetime.datetime.now()
                    current_month = current_date.month
                    current_year = current_date.year
                    leave_requests_filtered = LeaveRequest.objects.filter(
                        Q(leave_type="Permission") &
                        Q(start_date__month=current_month, start_date__year=current_year) &
                        Q(end_date__month=current_month, end_date__year=current_year) &
                        Q(user=employee))
                    if (len(leave_requests_filtered)<2) and (total_time_difference.total_seconds() >= (360 * 60)):
                        LeaveRequest.objects.create(user=employee,start_date=datetime.date.today(),end_date=datetime.date.today(),reason=f"Late coming of {in_time_difference}",leave_type="Permission")
                        Notification.objects.create(title="Permission Request",content=f"You have arrived late to work by {in_time_difference}. A leave request for this delay has been submitted.",to=employee)
                        employee_shift.attendance_status = "Present"
                    elif total_time_difference.total_seconds() >= (150 * 60):
                        employee_shift.attendance_status = "Halfday"
                    else:
                        employee_shift.attendance_status = "Absent"
                else:
                    employee_shift.attendance_status = "Absent"

            else:
                if not employee_shift.attendance_status:
                    employee_shift.attendance_status = "Absent"
                    Notification.objects.create(title="Missing Time Punch",content="It appears that you forgot to clock in today. This will be marked as an absence unless you apply for leave.",to=employee)
            employee_shift.save()
    return HttpResponse("html")

class PayrollProcessedCreateView(generics.CreateAPIView):
    serializer_class = PayrollProcessedSerializer

class ProcessedPayrollListView(generics.ListAPIView):
    queryset = PayrollProcessed.objects.all() #filter(month=datetime.datetime.now().date())  # Example: Display payroll for the current month
    serializer_class = PayrollProcessedSerializer

    def get(self, request,  *args, **kwargs):
        month = request.GET.get('month')
        queryset = PayrollProcessed.objects.filter(month=month)
        serializer = PayrollProcessedSerializer(queryset, many=True)
        return Response(serializer.data)

class LeaveRequestView(APIView):
    def get(self, request, *args, **kwargs):
        user_id= request.query_params.get('id')
        if user_id:
            user = CustomUser.objects.get(pk=user_id)
            leave_requests = LeaveRequest.objects.filter(user=user).order_by('-start_date')
        else:
            leave_requests = LeaveRequest.objects.all().order_by('-start_date')
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        employee = request.data.get('user')
        overlapping_requests = LeaveRequest.objects.filter(
            Q(user=employee), Q(start_date__lte=start_date, end_date__gte=start_date) |
            Q(start_date__lte=end_date, end_date__gte=end_date) |
            Q(start_date__gte=start_date, end_date__lte=end_date) , Q(status__in=['Approved', 'Pending']) 
        )
        if overlapping_requests.exists():
            return Response({"message": "Overlapping with other leave requests."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LeaveRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        success_message = "Leave request submitted successfully."
        return Response({"message": success_message}, status=201)
    


    # def put(self, request, *args, **kwargs):
        # start_date = request.data.get('start_date')
        # end_date = request.data.get('end_date')
        # employee = request.data.get('employee')
        # if start_date and end_date:
        #     overlapping_requests = LeaveRequest.objects.filter(
        #         Q(user=employee), Q(start_date__lte=start_date, end_date__gte=start_date) |
        #         Q(start_date__lte=end_date, end_date__gte=end_date) |
        #         Q(start_date__gte=start_date, end_date__lte=end_date) , Q(status__in=['Approved', 'Pending']) 
        #     ).exclude(id=pk)  
        #     if overlapping_requests.exists():
        #         return Response({"message": "overlapping"}, status=status.HTTP_400_BAD_REQUEST)
        # queryset= LeaveRequest.objects.get(pk=pk)
        # serializer = LeaveRequestSerializer(instance=queryset,data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # success_message = "Leave request updated successfully."
        # return Response({"message": success_message}, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        try:
            leave_request = LeaveRequest.objects.get(id=request.data.get('id'))
            leave_request.status =request.data.get('status')
            leave_request.save()
            return JsonResponse({'message': 'updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # def delete(self, request, pk=None):
    #     try:
    #         ids_to_delete = request.data.get('ids', [])
    #         if not ids_to_delete:
    #             return Response({"message": "No IDs provided for bulk delete"}, status=status.HTTP_400_BAD_REQUEST)
    #         LeaveRequest.objects.filter(pk__in=ids_to_delete).delete()
    #         return Response({"message": "Requests deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    #     except Exception as e:
    #         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


file_path= os.path.join(os.path.dirname(__file__), 'config.json')
with open(file_path) as config_file:
        config_data = json.load(config_file)

def total_worked_days(emp_id,start_date,end_date):
    api_url = f"http://127.0.0.1:8001/attendance/{emp_id}/{start_date}/{end_date}"
    params = {
        "from": start_date,
        "to": end_date
    }
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        total_worked_days = 0

        for date, entry in data.items():
            total_in_time = entry["Total In Time"]

            # hours, minutes, seconds = map(int, total_in_time.split(":"))
            total_minutes = float(total_in_time)/60

            if total_minutes > 480:  
                total_worked_days += 1
            elif 240 < total_minutes <= 480:  
                total_worked_days += 0.5
            elif 120 < total_minutes <= 240:
                total_worked_days += 0.25
        return total_worked_days
    
def salary_calculator(data,emp_id,month_name,financial_year):
    financial_year_parts = financial_year.split("-")
    start_year = int(financial_year_parts[0])
    end_year = int(financial_year_parts[1])
    financial_year = f"{start_year}-{end_year}"
    month_number = list(calendar.month_name).index(month_name.capitalize())
    num_days = calendar.monthrange(start_year if month_number >= 4 else end_year, month_number)[1]
    start_date = datetime.datetime(start_year if month_number >= 4 else end_year, month_number, 1).strftime("%Y-%m-%d")
    end_date = datetime.datetime(start_year if month_number >= 4 else end_year, month_number, num_days).strftime("%Y-%m-%d")
    worked_days = total_worked_days(emp_id,start_date,end_date)
    Deduction = config_data["Deduction"]
    Allowance = config_data["Allowance"]
    basic_pay= float(data[config_data["Basic Pay"]])
    basic_pay_this_month= (basic_pay/num_days)*worked_days
    Deduction_amount = 0
    Allowance_amount = 0
    for key, value in data.items():
        if isinstance(value, list):
        # if isinstance(value, list) and any(item for item in value if any(k in item for k in calculation)):
            for item in value:
                if Deduction in item:
                    percentage = float(item[Deduction])
                    Deduction_amount += (basic_pay_this_month * percentage / 100)
                if Allowance in item:
                    percentage = float(item[Allowance])
                    Allowance_amount += (basic_pay_this_month* percentage / 100)
    Net_salary = basic_pay_this_month+Allowance_amount-Deduction_amount
    return round(Net_salary, 2)
    

class GenerateSalaryAPIView(APIView):
    def get(self, request, employee_id,month,financial_year):
        try:
            salary_structure = SalaryStructure.objects.get(employee_id=employee_id)
            structure_serializer = SalaryStructureSerializer(instance=salary_structure, emp_id = employee_id)
            salary= salary_calculator(structure_serializer.data,employee_id,month,financial_year)
            structure_data = structure_serializer.data
            structure_data['salary'] = salary

            return Response(structure_data, status=status.HTTP_200_OK)
            # print(salary)
            # structure_serializer.data[salary]=
            # context= {
            #     "salary":salary[0],
            #     "month":month,
            #     "year":financial_year
            # }
            # history_serializer= SalaryHistorySerializer(data=structure_serializer.data, context=context)
            # if history_serializer.is_valid():
            #     instance = history_serializer.save()
            #     history_pk = instance.pk
            # for keys, values in structure_serializer.data.items():
            #     if isinstance(values, list):
            #         serializer_class_name = config_data[keys]
            #         serializer_class = globals()[serializer_class_name]
            #         for value in values:
            #             context={
            #                 "id": history_pk,
            #                 "model": keys,
            #                 "basic": salary[2]}
            #             addtional_serializer = serializer_class(data=value,context=context)

            #             if addtional_serializer.is_valid():
            #                 addtional_serializer.save()
            #             else:
            #                 obj_to_delete = SalaryHistory.objects.get(salary_month=month, financial_year=financial_year)
            #                 obj_to_delete.delete()
            # return Response(structure_serializer.data)
        
        except Exception as e:
            print(e)
            return Response({"error": "Salary details not found for this employee."}, status=404)


# class PayslipAPIView(APIView):
#      def get(self, request, employee_id,month,financial_year):
#          try:
#              filtered_objects = SalaryHistory.objects.get(employee=employee_id, salary_month= month, financial_year= financial_year)
#              serialized_data = SalaryHistorySerializer(instance=filtered_objects)
#              allowance_object = SalaryHistoryAllowance.objects.filter(salary_history=filtered_objects.pk)
#              allowance_serialized_data = SalaryHistoryAllowanceSerializer(instance=allowance_object,many=True)
#              deduction_object = SalaryHistoryDeduction.objects.filter(salary_history=filtered_objects.pk)
#              deduction_serialized_data = SalaryHistoryDeductionSerializer(instance=deduction_object,many=True)
#              serialized_data.data["allowances"]= allowance_serialized_data.data
#              serialized_data.data["deductions"]= deduction_serialized_data.data
#              return JsonResponse(serialized_data.data, status=200)
#          except SalaryHistory.DoesNotExist:
#             return Response('Invalid Request', status=404)

class PayslipAPIView(APIView):
    def get(self, request, employee_id, month, financial_year):
        try:
            filtered_objects = SalaryHistory.objects.get(employee=employee_id, salary_month=month, financial_year=financial_year)
            serialized_data = SalaryHistorySerializer(instance=filtered_objects).data
            allowance_objects = SalaryHistoryAllowance.objects.filter(salary_history=filtered_objects.pk)
            deduction_objects = SalaryHistoryDeduction.objects.filter(salary_history=filtered_objects.pk)
            if allowance_objects.exists():
                allowance_serialized_data = SalaryHistoryAllowanceSerializer(instance=allowance_objects, many=True)
                serialized_data["allowances"] = allowance_serialized_data.data
            if deduction_objects.exists():
                deduction_serialized_data = SalaryHistoryDeductionSerializer(instance=deduction_objects, many=True)
                serialized_data["deductions"] = deduction_serialized_data.data
            return JsonResponse(serialized_data, status=200)

        except SalaryHistory.DoesNotExist:
            return Response('Payslip not found', status=404)
        

class LeaveBalanceAPIView(APIView):
    def get(self, request, user_id):
        try:
            leave_balance = LeaveBalance.objects.get(user_id=user_id)
            serializer = LeaveBalanceSerializer(leave_balance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LeaveBalance.DoesNotExist:
            return Response({"message": "Leave balance not found"}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework import generics
from .models import Holiday
from .serializers import HolidaySerializer

class HolidayListCreateView(generics.ListCreateAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer

class HolidayDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer




def scheduletask(request):
    try:
        employees = CustomUser.objects.all()
        for employee in employees:
            employee_shift = EmployeeShift.objects.filter(employee_id=employee, date=datetime.date.today()).first()
            if employee_shift:
                shift_timing = Shift.objects.get(pk=employee_shift.shift)
                shift_start_time = shift_timing.start_time
                shift_end_time = shift_timing.end_time
                first_punch_log = DeviceLogProcessed.objects.filter(LogDate__date=datetime.date.today(), UserId=employee.device_id).order_by('LogDate').first()
                last_punch_log = DeviceLogProcessed.objects.filter(LogDate__date=datetime.date.today(), UserId=employee.device_id).order_by('-LogDate').first()
                if first_punch_log and last_punch_log:
                    in_time_difference = first_punch_log.LogDate - datetime.datetime.combine(datetime.date.today(), shift_start_time)
                    out_time_difference = datetime.datetime.combine(datetime.date.today(), shift_end_time) - last_punch_log.LogDate
                    if in_time_difference.total_seconds() <= 3600 and out_time_difference.total_seconds() <= 300:
                        employee_shift.attendance = "Present"
                        employee_shift.save()
        return JsonResponse(list(employees.values()), safe=False)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    except DeviceLogProcessed.DoesNotExist:
        return JsonResponse({'message': 'No records found for the given date.'}, status=404)


