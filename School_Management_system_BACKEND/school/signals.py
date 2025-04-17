from django.db.models.signals import post_save
from django.dispatch import receiver
from student.models import Student
from .models import CustomUser
from teacher.models import Teacher


# @receiver(post_save, sender=CustomUser)
# def create_user(sender, instance, created, **a):
    
#     if created:
#         if instance.is_student:
#             if not hasattr(instance, 'student_profile'):
#                 s1 = Student.objects.create(user=instance)
#                 s1.first_name = instance.first_name
#                 s1.last_name = instance.last_name
#                 s1.save()

#         elif instance.is_teacher:
#             t1 = Teacher.objects.create(user = instance)
#             t1.first_name = instance.first_name
#             t1.last_name = instance.last_name
#             t1.email = instance.email
#             t1.save()

# @receiver(post_save, sender=CustomUser)
# def create_user(sender, instance, created, **kwargs):
#     if created:
#         if  instance.is_student:
#             print('yes')
#             s1 = Student.objects.create(user=instance)
#             s1.first_name = instance.first_name
#             s1.last_name = instance.last_name
#             s1.enrollment_number = 
#             s1.save()

#         elif instance.is_teacher:
#             t1 = Teacher.objects.create(user=instance)
#             t1.first_name = instance.first_name
#             t1.last_name = instance.last_name
#             t1.email = instance.email
#             t1.save()

