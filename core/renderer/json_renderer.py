import json

from rest_framework.renderers import BaseRenderer


class JSONRenderer(BaseRenderer):
    media_type = "application/json"
    format = "json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_dict = {
            "data": {},
            "detail": None,
            "dev_message": None,
            "paginate": None,
            "extra": None,
        }
        if "message" in data:
            response_dict["detail"] = data.pop("message")
        if "dev_message" in data:
            response_dict["dev_message"] = data.pop("dev_message")
        if "paginate" in data:
            response_dict["paginate"] = data.pop("paginate")
        if "extra" in data:
            response_dict["extra"] = data.pop("extra")
        if "data" in data:
            response_dict["data"] = data.pop("data")
        else:
            response_dict["data"] = data
        data = response_dict
        return json.dumps(data).encode()
