from .cart import Cart

def cart(requrst):
    return {'cart': Cart(requrst)}