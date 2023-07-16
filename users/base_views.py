from rest_framework.generics import (CreateAPIView, ListAPIView, ListCreateAPIView,
                                 RetrieveAPIView, RetrieveUpdateAPIView, get_object_or_404)
from rest_framework.permissions import IsAuthenticated

# from knox.auth import TokenAuthentication

class BaseCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

class BaseListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

class BaseRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

class BaseRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

class BaseListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

