from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart(object):

    def __init__(self, request):
        """Savatcha ichidagi narsa aniqlanishi"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Sessiyaga bo`sh savatchani saqlaymiz.
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """Savatchaga mahsulot qo`shish yoki uning miqdorini o`zgartirish."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Sessiyani o`zgartirilgan deb belgilaymiz
        self.session.modified = True

    def remove(self, product):
        """Mahsulotni savatchadan yo`qotish"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Savatchadagi Mlar bo`yisha o`tib, tegishli Product obektlarini olamiz"""
        product_ids = self.cart.keys()
        # Product modeli obektlarini olib, ularni Sga uzatamiz
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Sdagi umumiy Mlar miqdorini qaytaramiz"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Sni tozalash
        del self.session[settings.CART_SESSION_ID]
        self.save()