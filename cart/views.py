from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Order
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from copy import deepcopy


class CartViewSet(ModelViewSet):
    """
    ViewSet para gestionar el carrito de compras.

    El ViewSet permite:
    - Listar los carritos asociados al usuario autenticado.
    - Crear, actualizar y eliminar carritos.
    - Realizar el checkout del carrito.

    Métodos personalizados:
    - checkout: Procesa la compra de los productos en el carrito.
    """

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna los carritos asociados al usuario autenticado.
        """
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Asocia el carrito creado al usuario autenticado.
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Procesa el checkout del carrito.

        Crea una orden con los ítems del carrito y vacía el carrito del usuario autenticado.

        - Retorna un mensaje de éxito y los detalles de la orden creada.
        - Retorna un error si el carrito está vacío.
        """
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or cart.items.count() == 0:
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = deepcopy(list(cart.items.all()))

        order = Order.objects.create(
            user=user,
            total_price=cart.total_price
        )
        order.items.set(cart_items)

        order_data = OrderSerializer(order).data

        cart.items.all().delete()
        cart.update_total_price()

        return Response(
            {"message": "Checkout realizado con éxito.", "order": order_data},
            status=status.HTTP_201_CREATED
        )


class CartItemViewSet(ModelViewSet):

    """
    ViewSet para gestionar los ítems del carrito.

    Este ViewSet permite:
    - Listar los ítems del carrito del usuario autenticado.
    - Crear, actualizar y eliminar ítems del carrito.
    """

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        """
        Retorna los ítems del carrito asociados al usuario autenticado.
        """

        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):

        """
        Agrega un ítem al carrito del usuario autenticado.
        Actualiza el precio total del carrito después de agregar el ítem.
        """

        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_item = serializer.save(cart=cart)
        cart.update_total_price()

    def perform_update(self, serializer):
        """
        Actualiza un ítem del carrito y recalcula el precio total del carrito.
        """
        serializer.save()
        serializer.instance.cart.update_total_price()

    def perform_destroy(self, instance):
        """
        Elimina un ítem del carrito y recalcula el precio total del carrito.
        """
        cart = instance.cart
        instance.delete()
        cart.update_total_price()