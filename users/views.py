import collections
from django.shortcuts import render
from .models import UserDetail
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.views import APIView
from pagination import OnOffPagination
from .serializers import (
    ListCreateUserSerializer
    , LoginUserSerializer
    , ChangePasswordSerializer
    , ForgotPasswordSerializer
)
from users.base_views import (
    BaseCreateView
    , BaseListCreateAPIView
    , BaseRetrieveAPIView
    , BaseRetrieveUpdateAPIView
    , BaseListAPIView
)
from rest_framework.permissions import (
    IsAuthenticated
    , IsAdminUser
    , IsAuthenticatedOrReadOnly
    , AllowAny
)
from django.db import transaction
from django.conf import settings
from rest_framework.exceptions import APIException


from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

# class CreateUserView(generics.ListCreateAPIView):
#     queryset = UserDetail.objects.filter(is_deleted=False)
#     pagination_class = OnOffPagination
#     serializer_class = ListCreateUserSerializer


class ListCreateUserView(BaseListCreateAPIView):
    queryset = UserDetail.objects.filter(is_deleted=False)
    # pagination_class = OnOffPagination
    serializer_class = ListCreateUserSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            # queryset = self.get_queryset()
            # serializer = self.get_serializer(queryset, many=True)
            # return Response({'request_status': 1, 'msg': "Success", 'data': serializer.data}, status=status.HTTP_200_OK)

            response = super().get(request, *args, **kwargs)
            return Response({'request_status': 1, 'msg': "Success", 'data': response.data}, status=status.HTTP_200_OK)

        except Exception as e:
            raise e


class LoginUserView(TokenObtainPairView):
    serializer_class = LoginUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        if user:
            odict = self.getUserDetails(user, request)
            return Response(odict)

    def getUserDetails(self, user, request):
        user_details = UserDetail.objects.get(id=user['user_details']['id'])
        profile_pic = request.build_absolute_uri(user_details.profile_img.url) if user_details.profile_img else ''
        odict = collections.OrderedDict()
        odict['user_id'] = user['user_details']['id']
        odict['refresh_token'] = user['refresh']
        odict['access_token'] = user['access']
        odict['username'] = user['user_details']['username']
        odict['first_name'] = user['user_details']['first_name']
        odict['last_name'] = user['user_details']['last_name']
        odict['profile_pic'] = profile_pic
        odict['request_status'] = 1
        odict['msg'] = "Logged in successfully..."

        browser, ip, os = self.detectBrowser()
        # log = LoginLogoutLoggedTable.objects.create(
        #     user=user, token=odict['token'], ip_address=ip, browser_name=browser, os_name=os)

        return odict

    def detectBrowser(self):
        import httpagentparser
        user_ip = self.request.META.get('REMOTE_ADDR')
        agent = self.request.META.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        browser_name = agent.split('/')[0] if not "browser" in browser.keys() else browser['browser']['name']
        os = "" if not "os" in browser.keys() else browser['os']['name']
        return browser_name, user_ip, os


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            print('Refresh Token -------->', request.data)
            token = RefreshToken(request.data.get('refresh_token'))
            token.blacklist()
            return Response({'request_status': 1, 'msg': "Successfully logged out..."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'request_status': 0, 'msg': "Invalid token or failed to logout..."}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    model = UserDetail

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                self.object = self.get_object()
                #print('self.object.id----',self.object.id)
                serializer = self.get_serializer(data=request.data)

                if serializer.is_valid():
                    user_data = self.request.user.username
                    if not self.object.check_password(serializer.data.get("old_password")):
                        return Response({'request_status': 1, 'msg': "Wrong password..."}, status=status.HTTP_400_BAD_REQUEST)
                    self.object.set_password(serializer.data.get("new_password"))
                    self.object.save()
                    #get_pass = SftbtUser.objects.filter(username=user_data, u_change_pass=True).values('username','u_change_pass')
                    #print('get_pass-->',get_pass)
                    # new_pass= SftbtUser.objects.filter(username=user_data, u_change_pass=True).update(        # Commented by Ashfaque Alam
                    new_pass= UserDetail.objects.filter(username=user_data).update(                              # Added by Ashfaque Alam
                        u_change_pass=False, u_password_to_know = serializer.data.get("new_password"))
                    #print('new_pass----', new_pass)
                    # self.object.save()
                    return Response({'request_status': 0, 'msg': "New Password Save Success..."}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e


class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    # model = UserDetail

    def post(self, request, format=None):
        try:
            with transaction.atomic():
                serializer = ForgotPasswordSerializer(data=request.data)
                if serializer.is_valid():
                    email = serializer.data.get("email")
                    #u_phone_no = serializer.data.get("u_phone_no")
                    password = settings.NEW_USER_DEFAULT_PASSWORD  # default password
                    if email:
                        user_details_exist = UserDetail.objects.filter(email=email)
                    #if u_phone_no:
                        #user_details_exist = SftbtUser.objects.filter(u_phone_no=u_phone_no)
                    #print("user_details_exiest",user_details_exiest)
                    if user_details_exist:
                        for user_data in user_details_exist:
                            # user_data.u_change_pass = True
                            user_data.password_to_know = password
                            first_name = user_data.first_name
                            last_name = user_data.last_name
                            send_mail_to = user_data.email
                            username=user_data.username
                            #send_sms_to = user_data.u_phone_no if user_data.u_phone_no else ""
                            user_data.set_password(password)  # set password...
                            user_data.save()
                            #user_data.save()
                            #print('user_data',user_data.cu_user.password)
                        # ============= Mail Send ==============#
                        if email:
                            mail_data = {
                                        # "name": user_data.first_name+ '' + user_data.last_name,
                                        "name": first_name + ' ' + last_name,
                                        "user": username,
                                        "pass": password
                                }
                            subject='Here is your password'
                            # ? send_mail('FP100', user_email=send_mail_to, mail_data=mail_data, subject=subject)
                            #mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                            #mail_thread.start()

                        return Response({'request_status': 1, 'msg': "Success! Password reset to default & mail sent to given email id.", 'data':mail_data}, status=status.HTTP_200_OK)
                    else:
                        raise APIException({'request_status': 1, 'msg': "Given email does not match with any user."})

                return Response({'request_status': 0, 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e


class CeleryBgTaskTestView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        from users.tasks import print_sum_till_input_num_celery_task
        _sum = print_sum_till_input_num_celery_task.delay(100000000)

        print('Celery Task ID --->', _sum.id)
        print('Celery Task Status --->', _sum.status)    # ? If 'PENDING' then `_sum.result` will return None. And if `SUCCESS` then `_sum.result` will return the result of the task.
        print('Celery Task Result --->', _sum.result)    # ? This will not block the execution. It will return the result if the task is completed. And if the task is not completed then it will return `None`.
        print('Celery Task Result --->', _sum.get())    # ? This will block the execution until the task is completed.

        return Response({'request_status': 1, 'msg': "Celery Background Task Started..."}, status=status.HTTP_200_OK)

