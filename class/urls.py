from os import name
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'class'

urlpatterns = [
    path('', views.index, name='index'),
    path('enroll/', views.enroll, name='enroll'),
    path('check_enrollement_submissions/', views.check_enrollement_submissions, name='check_enrollement_submissions'),
    path('enroll/<str:class_name>', views.enroll_class, name='enroll_class'),
    path('<str:class_name>/', views.class_info, name='class_info'),
    path('<str:class_name>/Assignment/<int:class_assignment_id>', views.class_assignment, name='class_assignment'),
    path('add/new', views.add_new_mat, name="add_new_mat"),
    path('getdetails', views.getdetails, name="getdetails"),
    path('add/new_chapter', views.new_chapter, name="new_chapter"),
    path('add/new_module', views.new_module, name="new_module"),
    path('<str:class_name>/add/new_assignment', views.new_assignment, name="new_assignment"),
    path('<str:class_name>/submitted_assignments', views.view_all_submitted_assignment, name="view_all_submitted_assignment"),
    path('<str:class_name>/submitted_assignments/<int:assignment>', views.view_submitted_assignment, name="view_submitted_assignment"),
    path('<str:class_name>/add/new_quiz', views.new_quiz, name="new_quiz"),
    path('<str:class_name>/quiz/<int:quiz_id>', views.quiz, name="quiz"),
    path('<str:class_name>/quiz/submitted_quizes', views.submitted_quizes, name="submitted_quizes"),
    path('<str:class_name>/quiz/submitted_quizes/<int:quiz_id>', views.view_submitted_quiz, name="view_submitted_quiz"),
    path('<str:class_name>/grades', views.class_grades, name="class_grades"),
    path('<str:class_name>/grades/<str:student_name>', views.student_grade, name="student_grade"),
    # path('add/new_for_class/', views.new_for_class, name='new_for_class'),
    # path('add/<str:classe>/new_for_chapter/', views.new_for_chapter, name='new_for_chapter'),
    # path('add/<str:chapter>/new_for_module/', views.new_for_module, name='new_for_module'),
    # path('adding_materials/<str:class_name>/<str:chapter_name>/<str:module_name>/', views.adding_materials, name='adding_materials'),
]

