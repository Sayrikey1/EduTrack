from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from accounts.models import User
from services.util import CustomAPIRequestUtil


class ClientService(CustomAPIRequestUtil):
    def __init__(self, request=None):
        super().__init__(request)

    def register(self, payload, user: User):
        for field, value in payload.items():
            setattr(user, field, value)

        user.registration_complete = True
        user.save()

        return user, None

    def filter_qs_by_date(self, qs, start_date=timezone.now(), end_date=None):
        if start_date:
            start_date = timezone.datetime.strptime(str(start_date), "%Y-%m-%d")
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            end_date = timezone.datetime.strptime(str(end_date), "%Y-%m-%d")
            qs = qs.filter(created_at__lte=end_date)
        return qs


class PasswordService(CustomAPIRequestUtil):
    def __init__(self, request):
        super().__init__(request)

    def verify_password(self, incoming_password, db_password):
        return check_password(incoming_password, db_password)

    def update_password(self, payload, user: User):
        new_password = payload.get("new_password")
        old_password = payload.get("old_password")

        # Verify old password
        user_password = user.password

        is_verified = self.verify_password(old_password, user_password)

        if not is_verified:
            return None, "Password Incorrect"

        user.password = make_password(new_password)
        user.save()

        return "Password set successfully", None
