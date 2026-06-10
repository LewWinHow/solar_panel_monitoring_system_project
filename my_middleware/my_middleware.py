from django.utils.deprecation import MiddlewareMixin
from utils.general_function import verify_network_address


class VerifyNetworkAddress(MiddlewareMixin):
    EXCLUDE_PATHS = ['/login/', '/register/','/forgot_password/','/verify_code/','/reset_password/']

    def process_request(self, request):
        if request.path in self.EXCLUDE_PATHS:
            return None
        else:
            if verify_network_address(request) is not True:
                return verify_network_address(request)

        return None

    def process_response(self, request, response):
        return response
