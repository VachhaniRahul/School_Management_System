from django.db import models
from django.forms import ValidationError
from school.models import CustomUser


# Create your models here.

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="teacher_profile")
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    qualifications = models.CharField(max_length=255, blank=True, null=True)
    # subjects = models.ManyToManyField('Subject', related_name='teachers')
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.email}"
    


class Class(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} {self.section}'
    
    class Meta:
        unique_together = ('name', 'section')
 

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return f'{self.name} {self.code}'


class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    class_model = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
   
    class Meta:
        unique_together = ('subject', 'class_model')  # Prevent duplicate assignments
        ordering = ["class_model"]

    def __str__(self):
        return f"{self.teacher.first_name} teaches {self.subject.name} in {self.class_model.name}"
    
    

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='ass')
    class_model = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='ass')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='ass')
    file = models.FileField(upload_to='file/', null=True, blank=True)

    def __str__(self):
        return f"Assignment: {self.title} for {self.class_model.name} ({self.subject.name})"

    class Meta:
        unique_together = ('class_model', 'subject', 'title')  
    
    def clean(self):
        # Check if the teacher is assigned to the subject in the class
        is_valid_assignment = TeachingAssignment.objects.filter(
            teacher=self.teacher,
            subject=self.subject,
            class_model=self.class_model
        ).exists()

        if not is_valid_assignment:
            raise ValidationError(
                f"Invalid assignment: {self.teacher} does not teach {self.subject} in {self.class_model}."
            )



