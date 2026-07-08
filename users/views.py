from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated

class CurrentUserView(APIView):
    """
    GET /users/me : Returns the profile of the currently authenticated Firebase user.
    PUT /users/me : Updates allowed profile fields
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)