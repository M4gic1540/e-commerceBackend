from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Order
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from copy import deepcopy


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Procesar el checkout del carrito."""
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or cart.items.count() == 0:
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # Clonar los ítems del carrito para asociarlos a la orden
        cart_items = deepcopy(list(cart.items.all()))

        # Crear la orden
        order = Order.objects.create(
            user=user,
            total_price=cart.total_price
        )
        order.items.set(cart_items)  # Asignar los ítems a la orden

        # Serializar la orden antes de vaciar el carrito
        order_data = OrderSerializer(order).data

        # Vaciar el carrito
        cart.items.all().delete()
        cart.update_total_price()

        return Response(
            {"message": "Checkout realizado con éxito.", "order": order_data},
            status=status.HTTP_201_CREATED
        )


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_item = serializer.save(cart=cart)
        cart.update_total_price()

    def perform_update(self, serializer):
        cart_item = serializer.save()
        cart_item.cart.update_total_price()

    def perform_destroy(self, instance):
        cart = instance.cart
        instance.delete()
        cart.update_total_price()
