from django.db import models
from django.conf import settings
from products.models import Product
from django.db.models import F, Sum

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_total_price(self):
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('product__price'), output_field=models.DecimalField())
        )['total'] or 0
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Carrito de {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Carrito de {self.cart.user.username})"

    def total_price(self):
        return self.product.price * self.quantity
