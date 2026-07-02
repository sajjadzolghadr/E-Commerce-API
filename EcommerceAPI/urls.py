from  rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products',views.ProductViewSet)
router.register('cart',views.CartViewSet,basename='cart')
router.register('cart-items',views.CartItemViewSet,basename='cart-items')
router.register('orders',views.OrderViewSet,basename='order')
router.register('reviews',views.ReviewViewSet,basename='review')
urlpatterns = router.urls