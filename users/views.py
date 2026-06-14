from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserProfileSerializer


class CurrentUserView(APIView):
    """
    Returns the profile data of the currently authenticated user.
    """

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)