from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LoginView(APIView):
    """
    Vista para el inicio de sesión de usuarios.

    Métodos:
    - post: Valida las credenciales del usuario y genera un token JWT.
    - logout: Invalida el token actual y cierra la sesión.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Inicio de sesión exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Datos del usuario autenticado",
                        ),
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Token JWT de acceso"
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description="Errores de validación",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Mensaje de error"
                        )
                    }
                )
            )
        }
    )
    def post(self, request):
        """
        Valida las credenciales y genera un token JWT para el usuario autenticado.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Generar el token JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class LogoutView(APIView):
    """
    Vista para cerrar sesión del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Invalida el token de actualización para cerrar sesión.
        """
        try:
            refresh = request.data.get("refresh")
            if not refresh:
                return Response({"detail": "Token de actualización no proporcionado."}, status=status.HTTP_400_BAD_REQUEST)

            # Invalida el token y lo agrega a la lista negra
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"detail": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
