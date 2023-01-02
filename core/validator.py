import re

from django.utils.translation import gettext as _
from rest_framework import serializers


def mobile_number_validation(phone_number):
    """
    This function check is phone is valid or not for Iran
    @param: phone number
    """
    pattern = re.compile(r"^09\d{9}$")
    if not pattern.search(phone_number):
        raise serializers.ValidationError(_("mobile number is not valid"))
