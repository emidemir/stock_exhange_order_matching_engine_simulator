from rest_framework import generics, permissions
from .serializers import UserSerializer

from .models import User
from rest_framework.filters import SearchFilter, OrderingFilter

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET: Retrieve my own profile (including balance).
    PATCH: Update my email or phone number.
    """
    serializer_class = UserSerializer
    # Only logged-in users can access this
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Magic: This forces the view to always return the LOGGED IN user.
        # It ignores any ID passed in the URL, preventing users from seeing others' data.
        return self.request.user
    
class UserListView(generics.ListAPIView):
    """
    GET: List all users to show a 'Leaderboard' on the dashboard.
    """
    queryset = User.objects.all().order_by('-balance') # Richer users first
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username']