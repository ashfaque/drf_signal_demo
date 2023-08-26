# In settings.py
'''
MIDDLEWARE += ["SFTCRM.custom_middleware.CheckSubscriptionMiddleware"]


CUSTOM_STATIC_MEDIA_PATH = list(filter(None, map(str.strip, str(os.getenv('STATIC_MEDIA_SERVER_HOST')).split('/'))))
SUBSCRIPTION_EXCLUDED_URLS = ['/{}/*'.format(CUSTOM_STATIC_MEDIA_PATH[-1])] if CUSTOM_STATIC_MEDIA_PATH else []

# * Add those endpoints that you don't want to check for subscription expiry in this list.
SUBSCRIPTION_EXCLUDED_URLS += [
    '/admin',
    '/admin/*',
    '/static/*',
    '/media/*',
    '/login/',
    '/logout/',
    '/master/subscription_company_tagging_list/',
]
'''

# In middleware.py
from django.http import JsonResponse
from datetime import date
from master.models import TMasterSubscriptionCompanyMapping
from django.conf import settings
from rest_framework.exceptions import APIException
from knox.auth import TokenAuthentication


def is_excluded_path(path: str, excluded_paths: list) -> bool:
    import fnmatch
    for pattern in excluded_paths:
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def CheckSubscriptionMiddleware(get_response):
    def middleware(request):
        # print('requst.path----------------> ', request.path)

        if not is_excluded_path(request.path, settings.SUBSCRIPTION_EXCLUDED_URLS) and not request.user.is_superuser:    # ? Subscription will only be checked if the request is not for an excluded path. And user is not superuser.
            # print(request.__dict__)
            # print('request.user.is_authenticated---------------->', request.user.is_authenticated)
            # print('user---------------->', request.user)
            user_obj, digest = TokenAuthentication().authenticate(request)    # Incorrect tokens will be handled here as well and a suitable error msg will also be thrown.
            if not user_obj.is_superuser:    # If user is a superuser and request is coming from an API hit, with Knox token.
                user_company_obj = user_obj.cu_user.company if user_obj.cu_user.company else None
                if not user_company_obj:
                    return JsonResponse({
                                'error': f'No company is assigned to user: {user_obj.username}.'
                            }, status=403)

                company_subscription_mapping_obj = TMasterSubscriptionCompanyMapping.objects.filter(company=user_company_obj).order_by('-created_at').first() if user_company_obj else None

                if not company_subscription_mapping_obj:
                    return JsonResponse({
                                'error': f'No subscription registered for the company: {user_company_obj.coc_name}.'
                            }, status=403)

                # ? Check if the subscription has expired
                subscription_valid_until = company_subscription_mapping_obj.grace_end_date if company_subscription_mapping_obj.grace_end_date else company_subscription_mapping_obj.subscription_valid_until
                # If Subscription has expired.
                if (
                    not company_subscription_mapping_obj.is_active                                                                                                                  # * Subscription is not marked as active.
                    or (company_subscription_mapping_obj.subscription_valid_from and company_subscription_mapping_obj.subscription_valid_from.date() > date.today())                # * Subscription not started yet.
                    or (subscription_valid_until and subscription_valid_until.date() < date.today())                                                                                # * Subscription end data is exceeded or subscription grace period also exceeded.
                    or (company_subscription_mapping_obj.is_trial and company_subscription_mapping_obj.trial_start_date and company_subscription_mapping_obj.trial_end_date and (   # * or is_trial=True & date.today() is NOT between trial_start_date or trial_end_date.
                            company_subscription_mapping_obj.trial_start_date.date() > date.today() or company_subscription_mapping_obj.trial_end_date.date() < date.today())
                    )
                    or company_subscription_mapping_obj.is_cancelled                                                                                                                # * or is_cancelled
                ):
                    response_data = {
                        'error': f'Subscription not active for the company: {user_company_obj.coc_name}.'
                    }
                    return JsonResponse(response_data, status=403)


        # Allow the request to proceed.
        response = get_response(request)
        return response
    return middleware

