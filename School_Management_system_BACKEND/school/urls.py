from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name = 'home'),
    
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),

    # AUTHENTICATION
    path('register/', views.Register.as_view(), name= 'register'),
    path('login/', views.Login.as_view(), name = 'login'),

    # USER DETAILS
    path('user/info/', views.UserInfo.as_view(), name = 'userinfo'),

    # STUDENTS DETAILS
    path('all/students/', views.AllStudentDetails.as_view() , name = 'all_students'),
    path('single/student/<str:pk>/', views.SingleStudentDetails.as_view() , name = 'single_students'),
    path('all/students/<str:pk>/', views.RemoveStudent.as_view() , name = 'remove_student'),
    path('student/classes-subjects/', views.getStudentClasses.as_view(), name='student_classes_subjects'),


    # CLASS DETAILS
    path('school/class/', views.ClassCreateView.as_view(), name = 'class_create_list'),
    # path('school/class/remove/<str:pk>/', views.ClassRemoveView.as_view(), name= 'class_remove'),
    path('class/subjects-students/', views.ClassAllStudentSubject.as_view(), name='class_subjects_students'),

    # ASSIGNMENT DETAILS
    path('class/assignment/', views.GetStudentAssignments.as_view(), name='student_Assignments'),
    path('class/assignment/submission/', views.StudentAssignmentSubmission.as_view(), name='student_Assignments_submission'),
    path('class/assignement/<str:class_id>/',views.getClassAssignment.as_view() ),
    path('class/assignment/submission/details/<str:assignment_id>/', views.AssignmentSubmissionDetails.as_view(), name = 'class_assignment_details'),
    path('class/assignment/submission/feedback/',views.AssignmentSubmissionFeedback.as_view()),

    # SUBJECTS DETAILS
    path('school/subjects/', views.AllSubjectListView.as_view(), name='all_subjects_list'),
    path('school/student/without/class/', views.GetAllStudentWithoutClass.as_view()),
    path('school/student/remove/class/', views.RemoveStudentFromClass.as_view()),


    # TEACHER DETAILS
    path('school/teachers/', views.AllTeacherListView.as_view(), name='all_teacher_list'),
    path('assignments/create/', views.TeacherAssignmentCreate.as_view(), name='teacher_assignment_create'),


    # ATTENDANCE DETAILS
    path('school/class/attendance/', views.ClassAttendance.as_view(),name= 'class_attendance'),
    path('school/class/show/attendance/',views.ShowAttendance.as_view()),


    # CHAT ROOM
    path('school/chatroom/',views.GroupChatView.as_view()),
    path('grades/csv/<str:class_id>/', views.download_grades_csv, name='download_grades_csv'),
    path('grades/excel/<str:class_id>/',views.download_grades_excel),

    path('school/notification/<str:student_id>/',views.NotificationView.as_view()),
    path('school/class/announcement/<str:class_id>/',views.Announcements.as_view())

]

