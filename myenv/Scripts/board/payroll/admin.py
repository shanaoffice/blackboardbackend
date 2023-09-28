from django.contrib import admin
from .models import *

admin.site.register([
    SalaryStructure,
    CustomPayDeduction,
    ManualPayDeduction,
    CustomPayAllowance,
    ManualPayAllowance,
    SalaryHistory,
    SalaryHistoryDeduction,
    SalaryHistoryAllowance,
])









