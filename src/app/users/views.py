from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from users.serializers import AccountSerializer


class AccountDetail(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.all()

    def get_object(self):
        return self.queryset.get(pk=self.request.user.id)
