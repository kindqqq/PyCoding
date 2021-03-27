from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client

from .models import Category, Customer, Cart, CartProduct, Notebook
from .views import recalc_cart

User = get_user_model()


class ShopTestCases(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser', password='password')
        self.category = Category.objects.create(name='Ноутбуки', slug='notebooks')
        image = SimpleUploadedFile('notebook_image.jpg', content=b'', content_type='image/jpg')
        self.notebook = Notebook.objects.create(
            category=self.category,
            title='Test Notebook',
            slug='test-slug',
            image=image,
            price=Decimal('50000.00'),
            diagonal='17.3',
            display_type='IPS',
            processor_freq='3.4 GHz',
            ram='6 GB',
            video='Geforce GTX',
            time_without_charge='10 hours',
        )
        self.customer = Customer.objects.create(user=self.user, phone='1111', address='Polbina')
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer,
            cart=self.cart,
            content_objects=self.notebook
        )

    def test_add_too_cart(self):
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('50000.00'))

    def test_response(self):
        client = Client()
        response = client.get('/add-to-cart/notebook/test-slug')
        self.assertEqual(response.status_code, 200)
