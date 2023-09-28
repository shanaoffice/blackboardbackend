from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True,blank=True)
#     is_staff = models.BooleanField(default=False,blank=True)
#     is_active = models.BooleanField(default=True,blank=True)
#     role = models.CharField(max_length=100,blank=True)
#     team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
#     profile_pic = models.CharField(max_length=200,blank=True,default="https://e7.pngegg.com/pngimages/114/356/png-clipart-time-student-recruitment-learning-professional-others-service-vector-icons-thumbnail.png")
#     device_id = models.CharField(max_length=100,blank=True)
#     employee_id = models.CharField(max_length=100,blank=True)

#     USERNAME_FIELD = 'email'
#     EMAIL_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name','last_name','role','username',"device_id"]

#     def __str__(self):
#         return self.email
    

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True,blank=True)
    is_staff = models.BooleanField(default=False,blank=True)
    is_active = models.BooleanField(default=True,blank=True)
    role = models.CharField(max_length=100,blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name","role"]

    def __str__(self):
        return self.username
    
class WorkInf(models.Model):
    employee_work= models.OneToOneField(CustomUser, on_delete=models.CASCADE,blank=True)
    employee_id = models.CharField(max_length=100,blank=True)
    device_id = models.CharField(max_length=100,blank=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    hr_partner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='hr_partner_for',blank=True,null=True)
    # hr_parter = models.
                
    def __str__(self):
        return self.employee_id


    
from datetime import datetime, timedelta

class Team(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)
    team_lead = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='led_teams')


    # default_shift = models.CharField(max_length=100)

    # def save(self, *args, **kwargs):
    #     is_new = self._state.adding
    #     super(Team, self).save(*args, **kwargs)
        
    #     if is_new:
    #         from_date = datetime.now().date()
    #         to_date = from_date + timedelta(days=365 * 2)
    #         TeamShift.objects.create(team=self, from_date=from_date, to_date=to_date, shift=self.default_shift)

    def __str__(self):
        return self.name
    
    from django.db import models

class Shift(models.Model):
    ShiftName = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.ShiftName


    
    
# class EmpWorkInf(models.Model):
#     employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True)
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     # team_lead = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='team_lead_for')


class TeamShift(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date = models.DateField(blank=False)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    
class EmployeeShift(models.Model):
    date = models.DateField()
    employee_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    attendance_status = models.CharField(max_length=100,blank=True, null=True )
    
    def __str__(self):
        return f"{self.employee.username} - {self.date}"

class EmployeeDailyAttendance(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True)
    attendance_date = models.DateField(blank=True)
    check_in_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    remarks = models.CharField(max_length=255,null=True, blank=True)


class DeviceLogProcessed(models.Model):
    DeviceLogId = models.BigAutoField(primary_key=True)
    DownloadDate = models.DateTimeField(null=True, blank=True)
    DeviceId = models.IntegerField(null=True, blank=True)
    UserId = models.CharField(max_length=50, null=True, blank=True)
    LogDate = models.DateTimeField(null=True, blank=True)
    Direction = models.CharField(max_length=255, null=True, blank=True)
    AttDirection = models.CharField(max_length=255, null=True, blank=True)
    C1 = models.CharField(max_length=255, null=True, blank=True)
    C2 = models.CharField(max_length=255, null=True, blank=True)
    C3 = models.CharField(max_length=255, null=True, blank=True)
    C4 = models.CharField(max_length=255, null=True, blank=True)
    C5 = models.CharField(max_length=255, null=True, blank=True)
    C6 = models.CharField(max_length=255, null=True, blank=True)
    C7 = models.CharField(max_length=255, null=True, blank=True)
    WorkCode = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False  
        app_label = 'users'
        db_table = 'devicelogs_processed'

    
# class Students(models.Model):
#     profile_pic = models.CharField(max_length=200,blank=True,default="https://e7.pngegg.com/pngimages/114/356/png-clipart-time-student-recruitment-learning-professional-others-service-vector-icons-thumbnail.png")
#     name = models.CharField(max_length=100,null=False,blank=True)
#     grade = models.CharField(max_length=200,blank=True)
#     section = models.CharField(max_length=200,blank=True)

#     def __str__(self):
#         return self.name
    
class EmployeeGeneric(models.Model):
    employee_s = models.OneToOneField(CustomUser, on_delete=models.CASCADE,blank=True)
    achievements = models.CharField(max_length=100,blank=True)
    remarks = models.CharField(max_length=100,blank=True)
    contact_number = models.CharField(max_length=20,blank=True)
    
class EmployeeAddress(models.Model):
    employee_a = models.OneToOneField(CustomUser, on_delete=models.CASCADE,blank=True)
    address = models.CharField(max_length=200,null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.employee_a.username

class EmployeePersonalDetails(models.Model):
    employee_p = models.OneToOneField(CustomUser, on_delete=models.CASCADE,blank=True)
    profile_pic = models.CharField(max_length=200,blank=True,default="https://e7.pngegg.com/pngimages/114/356/png-clipart-time-student-recruitment-learning-professional-others-service-vector-icons-thumbnail.png")
    gender = models.CharField(max_length=20,blank=True)
    dob = models.DateField(blank=True, default=None, null=True)
    age = models.PositiveIntegerField(blank=True,null=True)
    emg_cont_number = models.CharField(max_length=20,blank=True)
    mother_tongue = models.CharField(max_length=100,blank=True)
    father_name = models.CharField(max_length=100,blank=True)
    mother_name = models.CharField(max_length=100,blank=True)

    def __str__(self):
        return self.employee_p.username
    
class Notification(models.Model):
    title = models.CharField(max_length=255,blank=True)
    content = models.TextField(blank=True)
    to = models.ForeignKey(CustomUser, on_delete=models.CASCADE,blank=True)  
    modal_opened = models.BooleanField(default=False,blank=True)
    read = models.BooleanField(default=False,blank=True)  
    action_link = models.URLField(max_length=255, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True,blank=True)  

    def __str__(self):
        return self.title


   
    