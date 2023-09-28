from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import LeaveBalance, LeaveRequest
from django.db.models import F

@receiver(post_save, sender=CustomUser)
def create_leave_balance(sender, instance, created, **kwargs):
    if created:
        LeaveBalance.objects.create(user=instance, financial_year="2023-2024")


@receiver(post_save, sender=LeaveRequest)
def update_lop_count(sender, instance, **kwargs):
    if instance.leave_type == 'Paid leave' and instance.status == 'Approved':
        user = instance.user
        LeaveBalance.objects.filter(user=user).update(paid_leave_balance=F('paid_leave_balance') - 1)
        # print(LeaveBalance.objects.filter(user))
    elif instance.leave_type == 'Sick leave' and instance.status == 'Approved':
        user = instance.user
        user.sick_leave_balance -= 1
        user.save()