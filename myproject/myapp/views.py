from django.conf import settings
from django.shortcuts import render
from .models import Account,course, Video, Assessment,Payment
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout, authenticate
from django.contrib import auth
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from .models import Video, Assessment, course
# Create your views here.




def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        if password==confirmpassword:
            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('signup')
            user = Account.objects.create_user(first_name=first_name,email=email, password=password)
            user.is_user = True
            user.save()
            messages.info(request, 'Thank you for registering with us. Please Login')
            messages.success(request, 'Please verify your email for login!')

            current_site = get_current_site(request)
            message = render_to_string('account_verification_email.html', {
                        'user': user,
                        'domain': current_site,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                    })

            send_mail(
                        'Please activate your account',
                        message,
                        'mycardshelp@gmail.com',
                        [email],
                        fail_silently=False,
                    )

            # return redirect('/login/?command=verification&email=' + email)

            return redirect('login')
        else:
            print('password is not matching')
            messages.info(request, '!!!Password and Confirm Password are not  match!!!')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('signup')        

    

def login(request):  
    if request.method == 'POST':
        email = request.POST.get('email')
        pswd = request.POST.get('pass')
        print(email, pswd)
        user = auth.authenticate(email=email, password=pswd)
        print(user)

        if user is not None:
            auth.login(request, user)
            # save email in session
            request.session['email'] = email
            if user.is_admin:
                return redirect('admin')
            else:
                return redirect('Homee')
          
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('index')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email


            current_site = get_current_site(request)
            message = render_to_string('ResetPassword_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_mail(
                'Please activate your account',
                message,
                'mycardshelp@gmail.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'Forgot_Password.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['pass']
        confirm_password = request.POST['repass']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.info(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'ResetPassword.html')

def Homebase(request):
    return render(request,'Homebase.html')

def basee(request):
    return render(request,'basee.html')

def admin_base(request):
    user=Account.objects.all()
    return render(request,'admin_base.html',{'user':user,})

def Homee(request):
     # Fetch courses from the database
    courses = course.objects.all()

    # Pass the courses to the template
    context = {'courses': courses}
    return render(request, 'Homee.html', context)
     

def about(request):
    return render(request,'about.html')

def index(request):
    # Fetch courses from the database
    courses = course.objects.all()

    # Pass the courses to the template
    context = {'courses': courses}
    return render(request,'index.html',context)


def admin(request):
    user   = Account.objects.filter(is_user=True).count
    courses = course.objects.all().count()
    return render(request,'admin.html',{'user':user,'courses':courses})


def searchbar(request):
    query = request.GET.get('q')
    # Search for courses and users based on the query
    courses = course.objects.filter(course_name__icontains=query) if query else []
    users = Account.objects.filter(first_name__icontains=query) if query else []
    context = {'courses': courses, 'users': users, 'query': query}
    return render(request, 'searchbar.html', context)

def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('fullName')
        user.contact = request.POST.get('phone')

        profile_image = request.FILES.get('profileImage')

        if profile_image:
            user.img = profile_image
            user.profile_updated = True

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'profile.html', {'user': request.user})


def add_course(request):
    week_choices = course.WEEK_CHOICES

    if request.method == 'POST':
        # Handle form submission and saving data to the database
        course_name = request.POST.get('course_name')
        title = request.POST.get('title')
        outcomes = request.POST.get('outcomes')
        desc = request.POST.get('desc')
        price = request.POST.get('price')
        week = request.POST.get('week')
        image = request.FILES.get('image')

        # Get the currently logged-in user
        user = request.user

        new_course = course.objects.create(
            user=user,
            course_name=course_name,
            title=title,
            outcomes=outcomes,
            desc=desc,
            price=price,
            course_week=week,
            image=image,
            # Add other fields as needed
        )

        return redirect('admin_course_view')  # Redirect to the appropriate view after successful form submission

    context = {
        'week_choices': week_choices,
    }

    return render(request, 'add_course.html', context)




def admin_course_view(request):
    # Retrieve all courses from the database
    courses = course.objects.all()
    return render(request, 'admin_course_view.html', {'courses': courses})


def edit_course(request, course_id):
    instance = get_object_or_404(course, course_id=course_id)

    if request.method == 'POST':
        # Handle form submission and update data in the database
        instance.course_name = request.POST.get('course_name')
        instance.title = request.POST.get('title')
        instance.outcomes = request.POST.get('outcomes')
        instance.desc = request.POST.get('desc')
        instance.price = request.POST.get('price')
        instance.course_week = request.POST.get('week')
        # Check if a new image is provided
        new_image = request.FILES.get('image')
        if new_image:
            instance.image = new_image

        # Save the changes
        instance.save()

        return redirect('admin_course_view')

    # Provide the course instance to the edit_course.html template
    context = {
        'course': instance,
    }

    return render(request, 'edit_course.html', context)



def delete_course(request, id):
    item = get_object_or_404(course, course_id=id)
    item.delete()
    return redirect('admin_course_view')


def userdetails(request):
    users = Account.objects.filter(is_user=True)
    return render(request, 'userdetails.html', {'users': users})



def adminprofile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('fullName', '')
        user.contact = request.POST.get('phone', '')

        # Check if 'profileImageInput' key exists in request.FILES
        if 'profileImageInput' in request.FILES:
            new_image = request.FILES['profileImageInput']
            user.img = new_image

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('adminprofile')

    return render(request, 'adminprofile.html')


def module_add(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        week = request.POST.get('week')

        if not course_name or not week:
            return HttpResponseBadRequest("Invalid course or week.")

        existing_videos = Video.objects.filter(course__course_name=course_name, week=week)
        if existing_videos.exists():
            return HttpResponseBadRequest("Videos for the selected week already exist. You can't add videos for the same week again.")

        for i in range(1, 6):
            video_file = request.FILES.get(f'video_{i}')
            if video_file:
                Video.objects.create(week=week, video_number=i, video_file=video_file, course=course.objects.get(course_name=course_name))

        assessment_file = request.FILES.get('assessment')
        if assessment_file:
            Assessment.objects.create(week=week, assessment_file=assessment_file, course=course.objects.get(course_name=course_name))

        return redirect('admin_module_view')

    return render(request, 'module_add.html', {'existing_courses': course.objects.all()})

def admin_module_view(request):
    courses = course.objects.all()
    return render(request, 'admin_module_view.html', {'courses': courses})


def Course_User(request):
    return render(request, 'Course_User.html')

def course_detail(request, course_id):
    course_instance = get_object_or_404(course, course_id=course_id)
    x = course_instance.outcomes.split("->")
    context = {'course_instance': course_instance, 'x': x}
    return render(request, 'course_detail.html', context)

@csrf_exempt
def enroll_course(request, course_id):
    if request.method == 'POST':
        course_instance = get_object_or_404(course, course_id=course_id)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not logged in'}, status=401)

        amount = course_instance.price * 100

        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'course_{course_instance.course_id}_{request.user.id}',
            'payment_capture': '1',
        }
        order = client.order.create(data=order_data)
        order_id = order['id']
        request.session['order_id'] = order_id
        order_status = order['status']

        # After successful payment, update course status and create Payment instance
        course_instance.course_status = True
        course_instance.save()

        payment = Payment.objects.create(
            user=request.user,
            amount=amount / 100,  # Convert back to the actual amount
            razorpay_order_id=order_id,
            razorpay_payment_status=order_status,
            product=course_instance
        )

        return JsonResponse({'order_id': order['id'], 'amount': amount, 'course_id': course_instance.course_id})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def course_single(request, course_id):
    course_instance = get_object_or_404(course, course_id=course_id)
    videos = Video.objects.filter(course=course_instance)
    context = {'course_instance': course_instance, 'videos': videos}
    return render(request, 'course_single.html', context)