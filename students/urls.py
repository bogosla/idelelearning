from django.urls import path 
from django.contrib.auth import views as auth_views 
from courses.forms import LoginForm

from . import views
urlpatterns = [
    path('register/', views.StudentRegistrationView.as_view(), name='student_registration'),
    path('login/', auth_views.LoginView.as_view(template_name='students/student/login.html', authentication_form=LoginForm), name='student_login'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='students/student/change.html'), name='student_password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='students/student/done.html'), name='student_password_done'),

    path('courses/', views.StudentCourseListView.as_view(), name='student_course_list'),
    path('course/<pk>/', views.StudentCourseDetailView.as_view(), name='student_course_detail'),
    path('course/<pk>/<module_id>/', views.StudentCourseDetailView.as_view(), name='student_course_detail_module'),
    # path('course/<pk>/read/', views.StudentCourseDetailView.as_view(), name='student_course_detail_module'),

    path('enroll-course/', views.StudentEnrollCourseView.as_view(), name='student_enroll_course'),
    path('quiz/<quiz_id>/<course_id>/', views.quiz, name='quiz'),
    path('pass/<int:module_id>/<int:course_id>/', views.pass_module, name='pass'),

]