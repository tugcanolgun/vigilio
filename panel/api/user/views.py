from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from panel.api.user.serializers import ChangePasswordSerializer
from panel.decorators import check_demo


class ChangePasswordEndpoint(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    verbose_request_logging = True

    @check_demo
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()

        message: str = "Password change has failed."

        if request.user.check_password(serializer.object.current_password):
            request.user.set_password(serializer.object.new_password)
            request.user.save()
            message = "Password has been changed."

        return Response({"operation": message})
