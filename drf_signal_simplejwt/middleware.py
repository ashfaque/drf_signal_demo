
# ? Register this middleware under the MIDDLEWARE list in settings.py.

from users import models as user_models
from master.models import CollegePlanMapping
from users.models import UserAPIHitLog

from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import AccessToken
from django_user_agents.utils import get_user_agent

from ipware import get_client_ip

from pprint import pprint
from datetime import date
import fnmatch
import socket



def is_excluded_path(path: str, excluded_paths: list) -> bool:
    for pattern in excluded_paths:
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def SubscriptionMiddleware(get_response):
    def middleware(request):
        # print('requst.path---------------->', request.path)
        EXCLUDED_PATHS = ['/users/login/', '/users/logout/', '/admin', '/admin/*', '/static/*', '/media/*']    # ? Add those endpoints that you don't want to check for subscription expiry.
        # Check if the request is for an API endpoint (you can customize this check based on your API URLs)
        # if request.path.startswith('/api/'):
        # if request.path not in EXCLUDED_PATHS:
        if not is_excluded_path(request.path, EXCLUDED_PATHS) and not request.user.is_superuser:    # ? Subscription will only be checked if the request is not for an excluded path. And user is not superuser.
            # # pprint(request.__dict__)
            # print('request.user.is_authenticated---------------->', request.user.is_authenticated)
            # print('user---------------->', request.user)

            # if not isinstance(request.user, AnonymousUser):
            # if str(request.user) != 'AnonymousUser':
            jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
            if jwt_token:
                jwt_token = jwt_token.split(' ')[1]
                # try:
                access_token = AccessToken(jwt_token)
                user = access_token.payload.get('user_id')    # int
                print('User ID from AccessToken for SubscriptionMiddleware ----------> ', user)

                user_obj = user_models.UserDetail.objects.get(id=user)
                user_college_obj = user_obj.college if user_obj.college else None
                college_plan_mapping_obj = CollegePlanMapping.objects.get(college=user_college_obj) if user_college_obj else None
                if not college_plan_mapping_obj:
                    response_data = {
                        'error': f'College is not assigned to user with id: {user}.'
                    }
                    return JsonResponse(response_data, status=403)
                # print('is_active::: ', not college_plan_mapping_obj.is_active)
                # print('valid date expired::: ', college_plan_mapping_obj.plan_valid_until and (college_plan_mapping_obj.plan_valid_until.date() < date.today()))
                # print('trial date expired::: ', college_plan_mapping_obj.is_trial and college_plan_mapping_obj.trial_end_date and (college_plan_mapping_obj.trial_end_date.date() < date.today()))
                # print('is_cancelled::: ', college_plan_mapping_obj.is_cancelled)
                # Check if the subscription has expired
                if (
                    not college_plan_mapping_obj.is_active                                                                                                                  # * not is_active
                    or (college_plan_mapping_obj.plan_valid_until and college_plan_mapping_obj.plan_valid_until.date() < date.today())                                      # * or plan_valid_until
                    or (college_plan_mapping_obj.is_trial and college_plan_mapping_obj.trial_end_date and college_plan_mapping_obj.trial_end_date.date() < date.today())    # * or is_trial & trial_end_date
                    or college_plan_mapping_obj.is_cancelled                                                                                                                # * or is_cancelled
                ):
                    # Subscription has expired
                    response_data = {
                        'error': 'Subscription has expired. Please renew your subscription.'
                    }
                    return JsonResponse(response_data, status=403)

                # except:
                #     return JsonResponse({'error': 'Invalid JWT token'}, status=401)

            else:
                response_data = {
                    'error': '403 Forbidden.'
                }
                return JsonResponse(response_data, status=403)

        # Allow the request to proceed
        response = get_response(request)
        return response
    return middleware


'''
## This one also works fine.
class SubscriptionMiddleware:
    EXCLUDED_PATHS = ['/users/login/', '/users/logout/']  # Add your login and logout API URLs here

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in self.EXCLUDED_PATHS:
            # Get the user's subscription expiry date (you should have this logic in your User model)
            print('request.user.is_authenticated---------------->', request.user.is_authenticated)
            print('user---------------->', request.user)
            if not request.user.is_superuser:
                jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
                if jwt_token:
                    jwt_token = jwt_token.split(' ')[1]

                    try:
                        from rest_framework_simplejwt.tokens import AccessToken
                        access_token = AccessToken(jwt_token)
                        user = access_token.payload.get('user_id')
                        print(user)
                        request.user = user  # Set the user in the request manually
                    except:
                        return JsonResponse({'error': 'Invalid JWT token'}, status=401)

                    # Add your logic to check the subscription expiry date here
                    # For example, you can get the user's subscription details and check if it has expired
                    # Replace the following condition with your actual subscription expiry check
                    # if user.subscription_expired:
                    response_data = {
                        'error': 'Subscription has expired. Please renew your subscription.'
                    }
                    return JsonResponse(response_data, status=403)

        response = self.get_response(request)
        return response
'''



class APIHitLoggerMiddleware:
    EXCLUDED_PATHS = ['/users/login/', '/users/logout/', '/admin', '/admin/*', '/static/*', '/media/*']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not is_excluded_path(request.path, self.EXCLUDED_PATHS) and not request.user.is_superuser:
            jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
            if jwt_token:
                jwt_token = jwt_token.split(' ')[1]
                # try:
                access_token = AccessToken(jwt_token)
                user_id = access_token.payload.get('user_id')    # int
                print('User ID from AccessToken for APIHitLoggerMiddleware ----------> ', user_id)


                # Get user agent information.
                user_agent = get_user_agent(request)
                browser_name = user_agent.browser.family
                os_name = user_agent.os.family
                internal_ip = socket.gethostbyname(socket.gethostname())    # Get internal/local IP address (if behind a proxy)
                external_ip = self.get_client_ip(request)    # Get remote/external/static IP address
                # Get MAC address (not possible via HTTP request)

                _ = UserAPIHitLog.objects.create(
                                            # user_id=request.user.id,
                                            user_id=user_id,
                                            api_name=request.path,
                                            internal_ip=internal_ip,
                                            external_ip=external_ip,
                                            browser_name=browser_name,
                                            os_name=os_name,
                    )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip



# ? Usage: In any views, you can access the IP addresses by, `request.local_ip` and `request.external_ip` respectively.
class CaptureIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the client's local network IP
        local_ip = socket.gethostbyname(socket.gethostname())
        # local_ip, _ = get_client_ip(request)

        # Get the client's external static IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            external_ip = x_forwarded_for.split(',')[0]
        else:
            external_ip = request.META.get('REMOTE_ADDR')

        # Attach the IP addresses to the request object for easy access in views
        request.local_ip = local_ip
        request.external_ip = external_ip

        print('local_ip---------------->', local_ip)
        print('external_ip---------------->', external_ip)

        response = self.get_response(request)
        return response

