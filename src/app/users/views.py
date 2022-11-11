from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from users.serializers import AccountSerializer


User = get_user_model()


class AccountDetail(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.all()

    def get_object(self):
        return self.queryset.get(pk=self.request.user.id)
