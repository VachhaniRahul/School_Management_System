from rest_framework import serializers
from .models import CustomUser, GroupChatMessage
from student.models import Attendance, Student,AssignmentSubmission, Notification
from teacher.models import Class, Subject, Teacher, Assignment

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = CustomUser
        fields = ('username' ,'email', 'first_name', 'last_name', 
                  'password', 'is_student', 'is_teacher')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_student': {'write_only': True},
            'is_teacher' : {'write_only': True}
        }
    
    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.
        """
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            is_student=validated_data.get('is_student', False),
            is_teacher=validated_data.get('is_teacher', False),
            # password = validated_data['password']
            
        )
        user.set_password(validated_data['password'])  # Set password securely
        user.save()
    
        
        return user
    
class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    

    class Meta:
        model = Student
        exclude = ['user','class_name']

    def create(self, validated_data):
        # Extract user-related data
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        is_student = True

        enrollment_number = validated_data.pop('enrollment_number', None)
        if not enrollment_number:
            raise serializers.ValidationError({"enrollment_number": "This field is required."})

       
        # Create the User instance
        user = CustomUser.objects.create_user(username=username, email=email, password=password , first_name = first_name , last_name=last_name, is_student= is_student)

        # Create the Student instance linked to the User
        student = Student.objects.create(user=user, email = email, enrollment_number=enrollment_number, **validated_data)
        return student


class TeacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    class Meta:
        model = Teacher
        exclude = ['user']


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'section']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']


class AssignmentSerializer(serializers.ModelSerializer):
    # subject = SubjectSerializer()
    # class_model = ClassSerializer()
    # teacher = TeacherSerializer()
    subject = SubjectSerializer(read_only=True)
    class_model = ClassSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)

    # Accept IDs for write operations
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), write_only=True)
    class_model_id = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all(), write_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), write_only=True)


    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'subject', 'class_model', 'teacher','subject_id', 'class_model_id', 'teacher_id','file']
        
    def create(self, validated_data):
        # Extract IDs for writable fields
        subject = validated_data.pop('subject_id')
        class_model = validated_data.pop('class_model_id')
        teacher = validated_data.pop('teacher_id')

        # Create the assignment
        return Assignment.objects.create(
            subject=subject,
            class_model=class_model,
            teacher=teacher,
            **validated_data
        )


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'  # Include all fields from the model
        read_only_fields = ['submitted_at', 'status','student','assignment']  # Fields set automatically

    
    def create(self, validated_data):
        validated_data['status'] = 'submitted'  
        return super().create(validated_data)
    
    
class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    class_name = ClassSerializer()
    class Meta:
        model = Attendance
        fields = '__all__' 
        read_only_fields = ['id']

class GroupChatMessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)

    class Meta:
        model = GroupChatMessage
        fields = ['id','sender', 'message', 'created_at']
        

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','message','read']