from rest_framework import serializers
from .models import UserDetail
# from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.exceptions import APIException
from django.conf import settings
import datetime

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class ListCreateUserSerializer(serializers.ModelSerializer):
# 	created_by = serializers.CharField(default=serializers.CurrentUserDefault())

# 	class Meta:
# 		model = UserDetail
# 		fields = ('__all__')


class ListCreateUserSerializer(serializers.ModelSerializer):
    registered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    password = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = UserDetail
        fields = (
            'user_type'
            , 'middle_name'
            , 'email'
            , 'user_code'
            , 'gender'
            , 'phone_no'
            , 'profile_img'
            , 'class_teacher'
            , 'session'
            , 'semester'
            , 'stream'
            , 'course'
            , 'dob'
            , 'nationality'
            , 'address'
            , 'is_deleted'
            , 'registered_on'
            , 'registered_by'
            , 'updated_at'
            , 'updated_by'
            , 'deleted_at'
            , 'deleted_by'
            , 'password'    # ?
        )

    def create(self, validated_data):
        try:
            with transaction.atomic():
                login_user_id = self.context['request'].user.id
                # username = validated_data['username']
                username = validated_data.get('username', None)
                if not username:
                    raise APIException('Username is required')
                user_detail_count = UserDetail.objects.filter(username=username).count()
                if user_detail_count:
                    raise APIException('Username already exists')
            
                # password = User.objects.make_random_password()
                # password = settings.NEW_USER_DEFAULT_PASSWORD
                validated_data['password'] = settings.NEW_USER_DEFAULT_PASSWORD
                validated_data['password_to_know'] = settings.NEW_USER_DEFAULT_PASSWORD

                user_create = UserDetail.objects.create(**validated_data)
            return validated_data

        except Exception as ex:
            raise ex


class LoginUserSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user = dict(attrs)['username'] if 'username' in dict(attrs) else None
        is_user_exist = UserDetail.objects.filter(username=user).first()
        if is_user_exist:
            if is_user_exist.is_active:
                try:
                    data = super().validate(attrs)    # Generate Token
                    data['user_details'] = UserDetail.objects.filter(id=self.user.id).values().first()
                    # user_role = UserRoleModuleMapping.objects.filter(user_id=self.user.id).first().role.id if UserRoleModuleMapping.objects.filter(user_id=self.user.id).first() else None
                    # if user_role:
                    #     modules_under_role = list(RoleModuleMapping.objects.filter(role_id = user_role, is_deleted=False).values_list('module', flat=True))
                    # all_modules = list(UserRoleModuleMapping.objects.filter(is_deleted=False, user_id=self.user.id, module__isnull=False).values_list('module', flat=True).distinct())
                    # data['user_role'] = user_role
                    # data['modules_under_role'] = modules_under_role if user_role else None
                    # data['extra_accessible_modules'] = all_modules
                    data['request_status'] = 1
                    data['msg'] = 'Success'
                    return data
                except Exception as get_exception:                  
                    if get_exception == 'No active account found with the given credentials':    ## This exceltion is comming from JWT default_error_messages
                        raise APIException({'request_status':0, 'msg':'Please check the password!!'})  
                    else:
                        raise APIException({'request_status':0, 'msg':'Invalid credentials!!'})
            else:
                raise APIException({'request_status':0, 'msg':'User is Deactivated!!'})
        else:
            raise APIException({'request_status':0, 'msg':'User does not exist!!'})


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
