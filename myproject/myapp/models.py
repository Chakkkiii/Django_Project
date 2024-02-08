from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.db.models import Avg, Count

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
    discount = models.IntegerField(default=0)
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
    video_title =models.TextField(max_length=50, default='')
    course = models.ForeignKey(course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.course_name} - Week {self.week} - Video {self.video_number}"


class Assessment(models.Model):
    week   = models.IntegerField(choices=course.WEEK_CHOICES)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    option5 = models.CharField(max_length=255)
    answers = models.CharField(max_length=255, help_text="Enter the correct answer(s) separated by commas")
    status  = models.BooleanField(default=True)
    

    def __str__(self):
        return f"{self.course.course_name} - Week {self.week} - Assessment"


class UserAssessment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    week = models.IntegerField(choices=course.WEEK_CHOICES)
    marks = models.FloatField(default=0.0)
    taken = models.BooleanField(default=False)
    course = models.ForeignKey(course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} - {self.assessment.course.course_name} - Week {self.week} - Assessment"


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.FloatField(blank=True,null=True)
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    product = models.ForeignKey(course, on_delete=models.CASCADE,default=0) 


    def __str__(self):
        return str(self.user)
    


class Grand_Quiz(models.Model):
    coursename = models.ForeignKey(course, on_delete=models.CASCADE)
    questions = models.JSONField()
    status  = models.BooleanField(default=True)
    

    def save(self, *args, **kwargs):
        # Convert all answers to lowercase before saving
        for question in self.questions:
            question['answer'] = question['answer'].lower()
        super().save(*args, **kwargs)

    

class Certificate(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    percentage = models.FloatField()
    result = models.CharField(max_length=20)  # 'Beginner', 'Intermediate', 'Expert'




class ReviewRating(models.Model):
    product = models.ForeignKey(course, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    headline = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.headline)
    

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count