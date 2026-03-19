from django.urls import path
from . import views

app_name = 'phded_app'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create-user/', views.create_user_view, name='create_user'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:user_id>/delete/', views.delete_user_view, name='delete_user'),
    # Admin: courses
    path('courses/', views.admin_course_list_view, name='admin_course_list'),
    path('courses/create/', views.admin_course_create_view, name='admin_course_create'),
    # Professor
    path('professor/', views.professor_dashboard_view, name='professor_dashboard'),
    path('professor/course/<int:course_id>/', views.professor_course_detail_view, name='professor_course_detail'),
    path('professor/course/<int:course_id>/upload-content/', views.professor_upload_content_view, name='professor_upload_content'),
    path('professor/course/<int:course_id>/assignment/create/', views.professor_assignment_create_view, name='professor_assignment_create'),
    path('professor/course/<int:course_id>/assignment/<int:assignment_id>/', views.professor_assignment_detail_view, name='professor_assignment_detail'),
    path('professor/course/<int:course_id>/assignment/<int:assignment_id>/launch/', views.professor_assignment_launch_view, name='professor_assignment_launch'),
    path('professor/course/<int:course_id>/assignment/<int:assignment_id>/summary/', views.professor_assignment_summary_view, name='professor_assignment_summary'),
    path('professor/course/<int:course_id>/assignment/<int:assignment_id>/summary/student/<int:student_id>/', views.professor_assignment_student_response_view, name='professor_assignment_student_response'),
    path('professor/course/<int:course_id>/assignment/<int:assignment_id>/summary/export/', views.professor_assignment_summary_export_view, name='professor_assignment_summary_export'),
    # Student
    path('student/', views.student_dashboard_view, name='student_dashboard'),
    path('student/course/<int:course_id>/', views.student_course_detail_view, name='student_course_detail'),
    path('student/assignment/<int:assignment_id>/take/', views.student_assignment_take_view, name='student_assignment_take'),
    path('student/assignment/<int:assignment_id>/result/', views.student_assignment_result_view, name='student_assignment_result'),
]
