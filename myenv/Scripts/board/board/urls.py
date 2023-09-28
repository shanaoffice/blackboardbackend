"""
URL configuration for board project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

import  users.views as views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
import payroll.views as payrollViews

urlpatterns = [
    path('attendance/<int:user_id>/<str:start_date>', views.AttendanceView.as_view()),
    path('attendance/<int:user_id>/<str:start_date>/<str:end_date>', views.AttendanceView.as_view()),
    path('admin/', admin.site.urls),
    path('register', views.UserRegisterView.as_view()),
    path('login', views.UserLoginView.as_view()),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<str:resource_path>/<int:pk>', views.MyView.as_view(), name='myview'),
    path("employee", views.MyView.as_view(), name='myview1'),
    path("shift", views.ShiftView.as_view(), name='ShiftView'),
    path('holidays', payrollViews.HolidayListCreateView.as_view(), name='holiday-list-create'),
    path('holidays/<int:pk>', payrollViews.HolidayDetailView.as_view(), name='holiday-detail'),
    # path('emp_attendance/<int:pk>', views.EmployeeDailyAttendanceView.as_view()),
    # path('emp_attendance', views.EmployeeDailyAttendanceView.as_view()),
    path('password_reset', views.PasswordResetView.as_view(), name='password_reset'),
    path('workinf/<int:pk>', views.WorkInfUpdateAPIView.as_view(), name='workinf-update'),
    path('password-reset/confirm/<str:token>/<str:uid>', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('generate-salary/<int:employee_id>/<str:month>/<str:financial_year>', payrollViews.GenerateSalaryAPIView.as_view(), name='generate-salary'),
    path('view_payslip/<int:employee_id>/<str:month>/<str:financial_year>', payrollViews.PayslipAPIView.as_view(), name='view-salary_slip'),
    path("esslattendance/<int:user_id>/<str:start_date>/<str:end_date>", views.EsslAttendanceView.as_view()),
    path("esslattendance/<int:user_id>/<str:start_date>", views.EsslAttendanceView.as_view()),
    path('employees', views.EmployeeList.as_view(), name='employee-list'),
    path('shift_details',views.ShiftDetails.as_view()),
    path('update_shift/<str:type>/<str:method>',views.ShiftDetails.as_view()),
    path('update_shift/<str:type>',views.ShiftDetails.as_view()),
    path('teams', views.TeamListCreateView.as_view(), name='team-list-create'),
    path('teams/<int:pk>', views.TeamListCreateRetrieveUpdateDeleteView.as_view(), name='team-list-update'),
    path('apply_leave/<int:pk>', payrollViews.LeaveRequestView.as_view()),
    path('apply_leave', payrollViews.LeaveRequestView.as_view()),
    path('processed_payroll', payrollViews.ProcessedPayrollListView.as_view(), name='processed-payroll-list'),
    path('leave_balance/<int:user_id>', payrollViews.LeaveBalanceAPIView.as_view(), name='leave_balance'),
    # path('start_task/', payrollViews.start_hello_world_task, name='start_hello_world_task'),
    path('task', payrollViews.task),
    path('notification/<int:id>', views.NotificationsView.as_view()),
    path('attendance', views.EmployeeShiftView.as_view()),
    path('attendance/<int:pk>', views.EmployeeShiftView.as_view()),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)