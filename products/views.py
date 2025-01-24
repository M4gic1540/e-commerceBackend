from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class CategoryViewSet(ModelViewSet):

    """
    ViewSet para gestionar las categorías de productos.

    Este ViewSet permite:
    - Listar, crear, actualizar y eliminar categorías (requiere autenticación).
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(ModelViewSet):

    """
    ViewSet para gestionar los productos.

    Este ViewSet permite:
    - Listar productos (sin necesidad de autenticación).
    - Ver detalles de un producto específico (sin autenticación).
    - Crear, actualizar y eliminar productos (requiere autenticación).
    """

    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Permitir listar y obtener productos sin autenticación.
        """

        """
        Define los permisos según la acción:
        - `list` y `retrieve`: Permitido para todos (sin autenticación).
        - Otras acciones (`create`, `update`, `delete`): Requieren autenticación.
        """

        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
