
# ? Register this middleware under the MIDDLEWARE list in settings.py.

from django.http import JsonResponse
from datetime import date
from users import models as user_models
from master.models import CollegePlanMapping
from rest_framework.exceptions import APIException
from django.contrib.auth.models import AnonymousUser


def is_excluded_path(path: str, excluded_paths: list) -> bool:
    import fnmatch
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
            # from pprint import pprint
            # # pprint(request.__dict__)
            # print('request.user.is_authenticated---------------->', request.user.is_authenticated)
            # print('user---------------->', request.user)

            # if not isinstance(request.user, AnonymousUser):
            # if str(request.user) != 'AnonymousUser':
            jwt_token = request.META.get('HTTP_AUTHORIZATION', None)
            if jwt_token:
                jwt_token = jwt_token.split(' ')[1]
                from rest_framework_simplejwt.tokens import AccessToken
                # try:
                access_token = AccessToken(jwt_token)
                user = access_token.payload.get('user_id')    # int
                print('User ID from AccessToken ----------> ', user)

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
