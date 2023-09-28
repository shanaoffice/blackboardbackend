from django.db import models
from users.models import CustomUser

class Holiday(models.Model):
    occasion = models.CharField(max_length=255)
    date = models.DateField(unique=True)
    reason = models.TextField()

    def __str__(self):
        return self.occasion

class PayrollProcessed(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.CharField(max_length=25)
    workingdays = models.CharField(max_length=25)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employee.name} - {self.month}"


class LeaveRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    reason = models.TextField(blank=True)
    leave_type = models.CharField(max_length=25,blank=True)
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.user.name} - {self.start_date} to {self.end_date}"

class LeaveBalance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    sick_leave_balance = models.PositiveIntegerField(default=0)
    paid_leave_balance = models.PositiveIntegerField(default=0)
    financial_year = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.name}'s Leave Balance"

CHOICES = [
    ('custom', 'Custom'),
    ('manual', 'Manual'),
]

class SalaryStructure(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    deduction_type = models.CharField(max_length=10, choices=CHOICES, default='custom')
    allowance_type = models.CharField(max_length=10, choices=CHOICES, default='custom')

class CustomPayDeduction(models.Model):
    deduction_type = models.CharField(max_length=100)
    deduction_percentage = models.DecimalField(max_digits=10, decimal_places=2)

class ManualPayDeduction(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    deduction_type = models.CharField(max_length=100)
    deduction_percentage = models.DecimalField(max_digits=10, decimal_places=2)

class CustomPayAllowance(models.Model):
    allowance_type = models.CharField(max_length=100)
    allowance_percentage = models.DecimalField(max_digits=10, decimal_places=2)

class ManualPayAllowance(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    allowance_type = models.CharField(max_length=100)
    allowance_percentage = models.DecimalField(max_digits=10, decimal_places=2)

class SalaryHistory(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    salary_month = models.CharField(max_length=100)
    financial_year = models.CharField(max_length=100)
    worked_days = models.PositiveIntegerField()
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=100,default="nil")
    due = models.CharField(max_length=100,default="nil")

    def __str__(self):
        return f"{self.employee} - {self.salary_month}- {self.financial_year}"
    
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class SalaryHistoryAllowance(models.Model):
    salary_history = models.ForeignKey(SalaryHistory, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    allowance = GenericForeignKey('content_type', 'object_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class SalaryHistoryDeduction(models.Model):
    salary_history = models.ForeignKey(SalaryHistory, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    deduction = GenericForeignKey('content_type', 'object_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)


