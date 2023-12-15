from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin

# Create your models here.
class MyAccount(BaseUserManager):
    def create_user(self, first_name, email, password=None, last_name='', contact=None, img=None):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            contact=contact or 0,
            img=img 
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

       

    
   



class Account(AbstractBaseUser,PermissionsMixin):
    id              = models.AutoField(primary_key=True)
    first_name      = models.CharField(max_length=50, default='')
    last_name       = models.CharField(max_length=50, default='')
    email           = models.EmailField(max_length=100, unique=True)
    contact         = models.BigIntegerField(null=True, blank=True)
    img             = models.ImageField(upload_to='pics', default=None, null=True, blank=True)
    profile_updated = models.BooleanField(default=False)
    
    # required
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    is_user         = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    is_superadmin   = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    # REQUIRED_FIELDS = ['password']

    


    objects = MyAccount()
    
    

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.img and isinstance(self.img, str):  
            pass
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
    


class course(models.Model):
    WEEK_CHOICES = [
        (1, 'Week 1'),
        (2, 'Week 2'),
        (3, 'Week 3'),
        (4, 'Week 4'),
        (5, 'Week 5'),
        (6, 'Week 6'),
        (7, 'Week 7'),
        (8, 'Week 8'),
        # Add more weeks as needed
    ]
    course_id = models.AutoField(primary_key=True)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    course_name = models.CharField(max_length=200,unique=True)
    title = models.CharField(max_length=200, default='')
    image=models.ImageField(upload_to='pics')
    desc = models.TextField(blank=True)
    course_week = models.IntegerField(choices=WEEK_CHOICES)
    price = models.IntegerField(default='')
    outcomes = models.TextField()
    course_status=models.BooleanField(default=False)


    def get_video_numbers(self):
        return Video.objects.filter(course=self).values_list('video_number', flat=True).distinct()

    def get_video_by_number(self, video_number):
        return Video.objects.filter(course=self, video_number=video_number).first()
    

    def __str__(self):
        return self.course_name
    

class Video(models.Model):
    week = models.IntegerField(choices=course.WEEK_CHOICES)
    video_number = models.IntegerField()
    video_file = models.FileField(upload_to='course_videos')
    course = models.ForeignKey(course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.course_name} - Week {self.week} - Video {self.video_number}"


class Assessment(models.Model):
    week = models.IntegerField(choices=course.WEEK_CHOICES)
    assessment_file = models.FileField(upload_to='assessments')
    course = models.ForeignKey(course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.course_name} - Week {self.week} - Assessment"
