from datetime import date,datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import authenticate

from rest_framework import generics

from school.models import GroupChatMessage
from .serializers import AssignmentSerializer, AttendanceSerializer, ClassSerializer, CustomUserSerializer, GroupChatMessageSerializer, StudentSerializer, SubjectSerializer, TeacherSerializer,AssignmentSubmissionSerializer,NotificationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from student.models import Student, AssignmentSubmission,Attendance, Notification
from teacher.models import Assignment, Teacher, Class, Subject
import pandas as pd
import csv
from django.http import HttpResponse
from django.db.models import Q
# Create your views here.


class Register(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print('data : ',request.data)
            if request.data.get('is_student',False):
                student = Student.objects.create(
                    user=user,
                    first_name =request.data['first_name'],
                    last_name = request.data['last_name'],
                    email = request.data['email']
                )
                student.save()
            elif request.data.get('is_teacher',False):
                teacher = Teacher.objects.create(
                    user=user,
                    first_name =request.data['first_name'],
                    last_name = request.data['last_name'],
                    email = request.data['email']
                )
                teacher.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class Login(APIView):
    
    def post(self, request):
        # Get the username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')
        print("username :", username)
        print("password", password)
     
        user = authenticate(username=username, password = password)
        print("User : ",user)
        if user is not None: 
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                return Response({
                    'refresh': str(refresh),
                    'access': access_token,
                }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class TokenRefreshView(APIView):

     def post(self, request):
        refresh_token = request.data.get('refresh')
        print('refresh : ', refresh_token)
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
           
            token = RefreshToken(refresh_token)
            access_token = token.access_token

            return Response({
                'access': str(access_token),
                'refresh': str(token),
            }, status=status.HTTP_200_OK)

        except TokenError as e:
           
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except InvalidToken as e:
            
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class UserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        print("user", user)
        print("st : ",user.is_student)
        if user and user.is_student:
            serializer = StudentSerializer(instance = user.student_profile)
            return Response({"data":serializer.data, "role" : "student"} , status=status.HTTP_200_OK)
        elif user and user.is_teacher:
            serializer = TeacherSerializer(instance = user.teacher_profile)
            return Response({"data":serializer.data, "role" : "teacher"} , status=status.HTTP_200_OK)
        return Response({"Invalid": "These user is not student and teacher"}, status=status.HTTP_400_BAD_REQUEST)



class AllStudentDetails(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class SingleStudentDetails(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)  # Use PATCH if partial update is needed
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def perform_update(self, serializer):
        serializer.save()

class RemoveStudent(generics.DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class AllSubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class ClassCreateView(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

class ClassRemoveView(generics.DestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

class AllTeacherListView(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class getStudentClasses(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        student_id = request.GET.get('student_id')
        print(student_id)
        if not student_id:
            return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not student.class_name:
            return Response({"error": "Student is not assigned to any class"}, status=status.HTTP_404_NOT_FOUND)
        
        student_class = student.class_name
        subjects = Subject.objects.filter(assignments__class_model=student_class).distinct()
        
        # Serialize the classes and subjects
        class_data = ClassSerializer(student_class, many=False)
        subject_data = SubjectSerializer(subjects, many=True)
        
        return Response({
            "student": {
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
            },
            "classes": class_data.data,
            "subjects": subject_data.data
        },status=status.HTTP_200_OK)





class ClassAllStudentSubject(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self,request):
        class_id = request.GET.get('class_id')
        if not class_id:
            return Response({"error": "Class ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "class not found"}, status=status.HTTP_404_NOT_FOUND)
        
        students = class_obj.students.all()
        # subjects = class_obj.class_name.all()
        subjects = Subject.objects.filter(assignments__class_model=class_obj).distinct()


        student_data = StudentSerializer(students, many= True)
        subject_data = SubjectSerializer(subjects, many= True)

        return Response({
            "students": {
                "data":student_data.data
            },
            
            "subjects": {
                "data":subject_data.data
            }
        },status=status.HTTP_200_OK)



class GetStudentAssignments(APIView):
    def get(self, request):
        student_id = request.GET.get('student_id')
        if not student_id:
            return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

       
        student_classes = student.class_name

        
        assignments = Assignment.objects.filter(class_model=student_classes,due_date__gt=datetime.now())
        old_assignments = Assignment.objects.filter(class_model=student_classes,due_date__lt=datetime.now())
       
        assignment_data = AssignmentSerializer(assignments, many=True)
        old_assignments_data = AssignmentSerializer(old_assignments,many=True)

        return Response({
            "assignments": assignment_data.data,
            'old_assignment': old_assignments_data.data
        }, status=status.HTTP_200_OK)


class StudentAssignmentSubmission(APIView): 
    def get(self,request):
        student_id = request.GET.get('student_id')
        assignment_id = request.GET.get('assignment_id')
        student = Student.objects.get(id= student_id)
        assignment_id = Assignment.objects.get(id= assignment_id)
        if AssignmentSubmission.objects.filter(student = student , assignment = assignment_id).exists():
            allData = AssignmentSubmission.objects.get(student = student , assignment = assignment_id)
            return Response({"assignment_status" : allData.status, "feedback":allData.feedback, "grade":allData.grade},status=status.HTTP_200_OK)
        else:
           return Response({"assignment_status" : "Pending"},status=status.HTTP_200_OK)
        
    def post(self, request):
        student_id = request.GET.get('student_id')
        assignment_id = request.GET.get('assignment_id')
        print('student:',student_id)
        if not student_id:
            return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not assignment_id:
            return Response({"error": "Assignment ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate student
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate assignment
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure student is part of the assignment's class
        if assignment.class_model != student.class_name:
            return Response({"error": "Student is not enrolled in the class for this assignment"},
                            status=status.HTTP_403_FORBIDDEN)
    
        # Validate and save submission
        serializer = AssignmentSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            # Pass the student and assignment fields here
            serializer.save(student=student, assignment=assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AssignmentSubmissionFeedback(APIView):
     def post(self,request):
        print('data :',request.data)
        student_id = request.data['student_id']
        print('student_id:',student_id)
        assignment_id = request.GET.get('assignment_id')
        student = Student.objects.get(id= student_id)
        assignment_id = Assignment.objects.get(id= assignment_id)
        Asd = AssignmentSubmission.objects.get(student = student , assignment = assignment_id)
        Asd.feedback = request.data['feedback']
        Asd.grade = request.data['grade']
        Asd.status = "graded"
        Asd.save()
        return Response({"data":"successfully add"})

class TeacherAssignmentCreate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class getClassAssignment(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, class_id):
        # Filter assignments by class ID
        subject_id = request.GET.get('subject_id')
        print('sbid :',subject_id)
        if subject_id:
            assignments = Assignment.objects.filter(class_model_id=class_id , subject_id=subject_id)
            print('ass :',assignments)
        else:
            assignments = Assignment.objects.filter(class_model_id=class_id)

        if not assignments.exists():
            return Response({"message": "No assignments found for this class."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the assignments
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignmentSubmissionDetails(APIView):
    def get(self, request, *args, **kwargs):
        assignment_id = kwargs.get('assignment_id')

        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

        submissions = AssignmentSubmission.objects.filter(assignment=assignment)
        submitted_students = submissions.filter(Q(status ='submitted')| Q(status='graded'))
        remaining_students = Student.objects.filter(class_name=assignment.class_model).exclude(id__in=submitted_students.values('student'))

        data = {
            "id":assignment.id,
            "title":assignment.title,
            "submitted_count": submitted_students.count(),
            "remaining_count": remaining_students.count(),
            "submitted_students": [
                {
                    "student_id": submission.student.id,
                    "student_name": f"{submission.student.first_name} {submission.student.last_name}",
                    "feedback" : submission.feedback,
                    "file":submission.submission_file.url,
                    
                }
                for submission in submitted_students
            ],
            "remaining_students": [
                {
                    "student_id": student.id,
                    "student_name": f"{student.first_name} {student.last_name}"
                }
                for student in remaining_students
            ]
        }
        return Response(data, status=status.HTTP_200_OK)
    

class ClassAttendance(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        class_id = data.get('class_id')
        attendance_data = data.get('attendance')  
      
        if not class_id or not attendance_data:
            return Response({"error": "Class ID and attendance data are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Invalid Class ID."}, status=status.HTTP_404_NOT_FOUND)

        successful_count = 0
        failed_count = 0

       
        for item in attendance_data:
            student_id = item.get('student_id')
            status_name = item.get('status')

            if not student_id or status_name not in ['present', 'absent']:
                failed_count += 1
                continue

            try:
                student = Student.objects.get(id=student_id, class_name=class_instance)
                
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    class_name=class_instance,
                    date=date.today(),
                    defaults={'status': status_name}
                )
                if created:
                    successful_count += 1
                else:
                    failed_count += 1 

            except Student.DoesNotExist:
                failed_count += 1

        return Response({
            "message": f"Attendance submitted successfully! {successful_count} records added, {failed_count} updated."
        }, status=status.HTTP_200_OK)



class ShowAttendance(APIView):
    def get(self,request):
        student_id = request.GET.get('student_id')
        student = Student.objects.get(id = student_id)

        from_date = request.GET.get('from')
        to_date = request.GET.get('to')

        record = Attendance.objects.filter(student = student)
        if from_date and to_date:
            # from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            # to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            print('f :',from_date)
            record = record.filter(date__range=(from_date, to_date))

        # print('record :',record)
        serializer = AttendanceSerializer(record,many=True)       
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupChatView(generics.ListCreateAPIView):
    queryset = GroupChatMessage.objects.all().order_by('created_at')
    serializer_class = GroupChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupChatMessage.objects.all().order_by('created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data, "currentUser": self.request.user.username}, status=status.HTTP_200_OK)

    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user,message=self.request.data['message'])


class GetAllStudentWithoutClass(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    def get_queryset(self):
        return Student.objects.filter(class_name__isnull=True)
    
    def list(self,request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        student_id = request.data.get('student_id')  # Get the student_id from request data
        class_id = request.data.get('class_id')  # Get the class_id from request data
        print('studentID :',student_id)
        if not student_id or not class_id:
            return Response({"error": "student_id and class_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
            classes = Class.objects.get(id=class_id)
            student.class_name = classes
            student.save()
            return Response({"message": "Successfully added to class"}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Class.DoesNotExist:
            return Response({"error": "Class not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RemoveStudentFromClass(generics.CreateAPIView):
    def create(self,request, *args, **kwargs):
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(id = student_id)
            student.class_name = None
            student.save()
            return Response({"message": "Successfully remove from class"}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





def download_grades_csv(request, class_id):
    # Fetch all submissions for a given class
    submissions = AssignmentSubmission.objects.filter(assignment__class_model=class_id)

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="grades_class_{class_id}.csv"'

    writer = csv.writer(response)
    # Write header
    writer.writerow(['Student Name', "Assignment Name", "Subject", 'Grade', 'Feedback'])
    
    # Write data from each submission
    for submission in submissions:
        writer.writerow([submission.student.first_name,submission.assignment.title, submission.assignment.subject.name ,submission.grade, submission.feedback])

    return response

def download_grades_excel(request, class_id):
    submissions = AssignmentSubmission.objects.filter(assignment__class_model=class_id)
    data = [{
        'Student Name': submission.student.first_name,
        "Assignment Name":submission.assignment.title,
        "Subject":submission.assignment.subject.name ,
        'Grade': submission.grade,
        'Feedback': submission.feedback
    } for submission in submissions]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="grades_class_{class_id}.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Grades')

    return response



class NotificationView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def list(self, request, *args, **kwargs):
        
        student_id = kwargs.get('student_id')
        print('stu:',student_id)
        if not student_id:
            return Response({"message":"student id is required"},status=status.HTTP_400_BAD_REQUEST)
        
        student = Student.objects.get(id=student_id)
        queryset = Notification.objects.filter(user = student)
        unreadCount = queryset.filter(read=False).count()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"notification":serializer.data,"unReadCount":unreadCount}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        if not student_id:
            return Response({"message":"student id is required"},status=status.HTTP_400_BAD_REQUEST)
        
        student = Student.objects.get(id=student_id)
        queryset = Notification.objects.filter(user = student)
        for i in queryset:
            i.read = True
            i.save()
        
        return Response({'message':'successfully reads notifications'},status=status.HTTP_200_OK)
    
    
    

class Announcements(generics.CreateAPIView):
     serializer_class = NotificationSerializer

     def create(self, request, *args, **kwargs):
        class_id = kwargs.get('class_id')
        message = request.data.get('message')
        if not message:
             return Response({'message':"message field is required"},status=status.HTTP_400_BAD_REQUEST)
        if not class_id:
             return Response({'message':"class ID is required"},status=status.HTTP_400_BAD_REQUEST)
        classes = Class.objects.get(id = class_id)
        students = classes.students.all()
        print('stuAll :',students)
        for student in students:
            notification = Notification.objects.create(
                user= student,
                message = message
            )
            notification.save()
        return Response({'message':'succesfully Announcements Done'})
         
