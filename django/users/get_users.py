from .models import RedUser
from .serializers import UsersSerializer


class GetUsers:
    query_set = RedUser.objects.all()

    def get_microsoft_business_users(self, mode):
        """
        Function to get microsoft business users
        :param mode:
        :return:
        """
        result = ms_users = self.get_users_given_vendor_name('Microsoft', 'all')
        if mode == 'email':
            result = self.get_email_list(ms_users)
        return result

    def get_users_given_vendor_name(self, vendor_name, mode):
        """
        Function to get users for given vendor name
        :param vendor_name:
        :param mode:
        :return:
        """
        ms_user_query = self.query_set.filter(profile__vendor_category__vendor_name=vendor_name)
        serializer = UsersSerializer(ms_user_query, many=True, context={'request': None})
        result = ms_users = serializer.data
        if mode == 'email':
            result = self.get_email_list(ms_users)
        return result

    def get_users_given_vendor_id(self, vendor_id, mode):
        """
        Function to get the user records or email list for given vendor id
        :param vendor_id:
        :param mode:
        :return:
        """
        ms_user_query = self.query_set.filter(profile__vendor_category__vendor_id=vendor_id)
        serializer = UsersSerializer(ms_user_query, many=True, context={'request': None})
        result = users = serializer.data
        if mode == 'email':
            result = self.get_email_list(users)
        return result

    def get_email_list(self, user_data):
        """
        Function to get the email list from users list
        :param user_data:
        :return:
        """
        emails = []
        for user in user_data:
            email = user['email']
            if email:
                emails.append(email)
                # Todo: if we need comma separated email string ','.join(emails)
        return emails

    def get_vendors_associated_to_user(self, user_id):
        """
        Function to get associated vendor list for the given user id
        :param user_id:
        :return:
        """
        ms_user_query = self.query_set.filter(id=user_id)
        serializer = UsersSerializer(ms_user_query, many=True, context={'request': None})
        data = serializer.data[0]
        vendors = []
        if data:
            vendor_category = data['vendor_category']
            if vendor_category is not None and len(vendor_category) > 0:
                for vendor in vendor_category:
                    vendors.append(vendor['vendor_id'])
        return vendors
