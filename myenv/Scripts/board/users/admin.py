from django.contrib import admin
from . models import CustomUser, EmployeeDailyAttendance, DeviceLogProcessed, Team, EmployeeShift

# Register your models here.


admin.site.register(CustomUser)

admin.site.register(EmployeeDailyAttendance)

admin.site.register(DeviceLogProcessed)

admin.site.register(Team)

admin.site.register(EmployeeShift)
