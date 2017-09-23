class CommonFunctions:
    @staticmethod
    def check_and_complete_request(cloud_account):
        """
        Function to complete the pending request
        :param cloud_account:
        :return:
        """
        from .models import PendingRequests
        pending_request = PendingRequests.objects.filter(cloud_account=cloud_account).values()
        if pending_request and len(pending_request):
            pending_request_id = pending_request[0]['id']
            request_object = PendingRequests.objects.get(id=pending_request_id)
            request_object.active = True
            request_object.save()
        return True

    @staticmethod
    def get_base_url(request):
        """
        Function to get the bse url from the request
        :param request:
        :return:
        """
        host = request.get_host()
        host = host.replace("8000", "4200")
        protocol = 'https://' if request.is_secure() else 'http://'
        base_url = protocol + host
        return base_url
