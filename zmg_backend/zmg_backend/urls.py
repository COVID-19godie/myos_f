# 文件路径: zmg_backend/zmg_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView  # [新增] 引入通用视图

# 引入 SimpleJWT 的视图
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter
from core.views import DesktopIconViewSet, CategoryViewSet, ResourceViewSet

# 注册 API 路由
router = DefaultRouter()
router.register(r'desktop', DesktopIconViewSet, basename='desktop')
router.register(r'categories', CategoryViewSet)
router.register(r'resources', ResourceViewSet)

urlpatterns = [
    # 1. [关键修改] 首页路由：将根路径 '' 指向 index.html
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # 2. 管理后台
    path('admin/', admin.site.urls),
    
    # 3. JWT 认证接口
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 4. 业务 API
    path('api/', include(router.urls)),
]

# 开发模式下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)