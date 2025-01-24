from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User


class LoginView(APIView):

    """
    Vista para el inicio de sesión de usuarios.

    Métodos:
    - post: Valida las credenciales del usuario y genera un token JWT.
    - logout: Invalida el token actual y cierra la sesión.
    """

    def post(self, request):

        """
        Valida las credenciales y genera un token JWT para el usuario autenticado.

        Retorna:
        - Datos del usuario y el token de acceso JWT en caso de éxito.
        - Errores de validación en caso de fallos.
        """

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

        """
        Invalida el token JWT del usuario autenticado, cerrando la sesión.
        """

        RefreshToken().blacklist(request.auth)
        return Response({'detail': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):

    """
    ViewSet para gestionar usuarios.

    Este ViewSet permite:
    - Registrar nuevos usuarios (sin autenticación).
    - Listar, actualizar y eliminar usuarios (requiere autenticación).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Define los permisos según la acción:
        - `create`: Permitido para todos (sin autenticación).
        - Otras acciones: Requieren autenticación.
        """
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Registra un nuevo usuario.

        Retorna:
        - Datos del usuario creado en caso de éxito.
        - Errores de validación en caso de fallos.
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un usuario.

        No permite eliminar superusuarios.
        """
        user = self.get_object()
        if user.is_superuser:
            return Response({'detail': 'No puedes eliminar un superusuario.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(user)
        return Response({'detail': 'Usuario eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)
