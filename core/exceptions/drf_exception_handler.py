from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback

from core.logging import exception_log, log_data
from .exception_data import exception_data

from django.core.exceptions import ValidationError


def drf_exception_handler(exc, context):
    path, logger, version = log_data(context["view"])
    response, data = exception_data(context["view"])
    if isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(exc.messages, code=exc.code)
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, IntegrityError):
        exc = exceptions.ValidationError(exc, code="unique")
    api_exception = isinstance(exc, exceptions.APIException)
    if api_exception:
        set_rollback()
        if isinstance(exc.detail, (list, dict)):
            if isinstance(exc.detail, dict):
                keys = list(exc.detail.keys())
                err = exc.detail[keys[0]]
                response.update({"message": err, "status": exc.status_code})
            else:
                response.update(
                    {
                        "message": exc.detail[0],
                        "status": exc.status_code,
                    }
                )
            response.update({"dev_message": exc.detail, "status": exc.status_code})
        else:
            response.update({"message": exc.detail, "status": exc.status_code})

    try:
        if api_exception:
            logger.error(
                exception_log(
                    path, exc, request=context["request"], version=version, **data
                )
            )
        else:
            logger.exception(
                exception_log(
                    path, exc, request=context["request"], version=version, **data
                )
            )
    except Exception as e:
        pass
    return Response(response, status=response.pop("status"))
