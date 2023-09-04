from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import *
from users.forms import CustomUserCreationForm

# Register your models here.

class CustomUserAdmin(UserAdmin):
	model = UserDetail
	add_form = CustomUserCreationForm

	fieldsets = (
		*UserAdmin.fieldsets,
		(
			'Common Details',
			{
				'fields':(
					'middle_name',
                    'gender',
                    'profile_img',
				)
			},
		),
        (
            'Official Details',
            {
                 'fields':(
                     'user_type',
                     'user_code',
                     'class_teacher',
                     'session',
                     'semester',
                     'stream',
                     'course',
                     'college',
                    #  'department',
                    #  'sub_department',
                 )
            }
        ),
        (
        'Personal Details',
            {
                'fields':(
                    'phone_no',
                    'dob',
                    'nationality',
                    'address',
                    'password_to_know',
                )
            }
        ),
        (
        'Status',
            {
                'fields':(
                    'is_deleted',
                    # 'registered_on',    # Cannot add this in Django Admin, as this is a non-editable field.
                    'registered_by',
                    'updated_at',
                    'updated_by',
                    'deleted_at',
                    'deleted_by',
                )
            }
        ),
	)


@admin.register(UserDetail)
# class UserDetail(admin.ModelAdmin):
class UserDetail(CustomUserAdmin):
    list_display = [field.name for field in UserDetail._meta.fields]
    # search_fields = ('id', 'email', 'user_code', 'username', 'user_type', 'phone_no', 'college__name', 'department__name', 'sub_department__name', 'is_deleted')
    search_fields = ('id', 'email', 'user_code', 'username', 'user_type', 'phone_no')


@admin.register(UserAPIHitLog)
class UserAPIHitLog(admin.ModelAdmin):
    list_display = [field.name for field in UserAPIHitLog._meta.fields]
    readonly_fields = [field.name for field in UserAPIHitLog._meta.fields]    # Read-only fields
    search_fields = ('user', 'user__email', 'user__username', 'user__first_name', 'user__last_name', 'api_name')
