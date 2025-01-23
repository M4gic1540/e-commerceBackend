from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Generar el token JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def logout(self, request):
        RefreshToken().blacklist(request.auth)
        return Response({'detail': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Define permisos por acción.
        - `create` (registro de usuarios): Permitir acceso sin autenticación.
        - `list`, `retrieve`, `update`, `delete`: Requieren autenticación.
        """
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Sobrescribe `create` para manejar el registro de usuarios.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribe `destroy` para agregar una validación antes de eliminar un usuario.
        """
        user = self.get_object()
        if user.is_superuser:
            return Response({'detail': 'No puedes eliminar un superusuario.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(user)
        return Response({'detail': 'Usuario eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)