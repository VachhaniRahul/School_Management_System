# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
# from .models import CustomUser


# # Custom UserAdmin with conditional logic for superusers and staff
# class CustomUserAdmin(DefaultUserAdmin):
#     # Customize which fields are displayed in the admin form
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),  # Login details
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),  # Personal details
#         ('Roles', {'fields': ('is_student', 'is_teacher')}),  # Role fields
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_authorised',  # Add is_authorized here
#                                     'groups', 'user_permissions')}),  # Admin permissions
#     )

#     # Customize fields in the user creation form (when creating a new user)
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'password1', 'password2', 'is_authorised', 'is_student', 'is_teacher')}
#          ),
#     )

#     # Customize what fields are displayed in the list view
#     list_display = (
#         'username', 'email', 'first_name', 'last_name', 'is_authorised',
#         'is_student', 'is_teacher', 'is_staff', 'is_superuser'
#     )

#     # Filter users based on role and authorization
#     list_filter = ('is_student', 'is_teacher', 'is_authorised', 'is_staff', 'is_superuser')

#     # Customize queryset to separate superusers and staff in the admin list view
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         if request.user.is_superuser:
#             return queryset  # Superusers see all users
#         return queryset.filter(is_superuser=False)  # Non-superuser staff won't see superusers

# # Register the CustomUser model with the custom admin
# admin.site.register(CustomUser, CustomUserAdmin)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,GroupChatMessage

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Customize fieldsets for the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_authorised', 'is_student', 'is_teacher', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'is_student', 'is_teacher', 'is_authorised')
    readonly_fields = ('date_joined', 'last_login')
    
    # Specify the fields to be included in the add form (for creating new users)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_authorised', 'is_student', 'is_teacher'),
        }),
    )

admin.site.register(GroupChatMessage)


