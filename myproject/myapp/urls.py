from.import views
from django.urls import path
urlpatterns = [
    path('', views.index, name='index'),
    path('Homebase/', views.Homebase, name='Homebase'),
    path('basee/', views.basee, name='basee'),
    path('admin_base/', views.admin_base, name='admin_base'),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # path('changepassword/', views.changepassword, name='changepassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('Homee/', views.Homee, name='Homee'),
    path('admin/', views.admin, name='admin'),
    path('profile/', views.profile, name='profile'),
    path('add_course/', views.add_course, name='add_course'),
    path('admin_course_view/', views.admin_course_view, name='admin_course_view'),
    path('edit_course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete_course/<int:id>/', views.delete_course, name='delete_course'),
    path('searchbar/', views.searchbar, name='searchbar'),
    path('userdetails/', views.userdetails, name='userdetails'),
    path('adminprofile/', views.adminprofile, name='adminprofile'),
    path('module_add/', views.module_add, name='module_add'),
    path('module_edit/<int:week_id>/', views.module_edit, name='module_edit'),
    path('admin_module_view/', views.admin_module_view, name='admin_module_view'),
    path('admin_add_assesment_edit/<int:week_id>/<int:course_id>/', views.admin_add_assesment_edit, name='admin_add_assesment_edit'), 
    path('Course_User/', views.Course_User, name='Course_User'),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'), 
    path('enroll_course/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course_single/<int:course_id>/', views.course_single, name='course_single'),
    path('My_Course/', views.My_Course, name='My_Course'),

    path('course/<int:course_id>/assessment/<int:week>/', views.weekly_assessment, name='weekly_assessment'),
    path('course/<int:course_id>/assessment/<int:week>/submit/', views.submit_assessment, name='submit_assessment'),

    
]

 