# 文件路径: zmg_backend/zmg_backend/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
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

# API视图
from core.api_views import (
    api_login, api_logout, api_user_info, 
    api_files_list, api_search, api_upload_file,
    health_check
)

# 注册 API 路由
router = DefaultRouter()
router.register(r'desktop', DesktopIconViewSet, basename='desktop')
router.register(r'categories', CategoryViewSet)
router.register(r'resources', ResourceViewSet)

urlpatterns = [
    # 1. 管理后台
    path('admin/', admin.site.urls),
    
    # 2. API 路由 - 精确匹配，优先级最高
    path('api/token/', api_login, name='api_token'),
    path('api/logout/', api_logout, name='api_logout'),
    path('api/user/', api_user_info, name='api_user_info'),
    path('api/files/', api_files_list, name='api_files_list'),
    path('api/search/', api_search, name='api_search'),
    path('api/upload/', api_upload_file, name='api_upload_file'),
    path('api/health/', health_check, name='health_check'),
    path('api/verify/', api_user_info, name='api_verify'),
    
    # 3. 业务 API - 必须在根路由之前
    path('api/', include(router.urls)),

    # 4. 静态文件和媒体文件服务 - 仅在非API路径下提供
    # 这样API请求不会被误认为静态文件
    
    # 5. 首页路由：只匹配确切的根路径
    re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
]

# 开发模式下提供媒体文件访问 - 移到urlpatterns外避免冲突
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 注意：不要添加 STATIC_URL 的静态文件服务，避免与API冲突

# 开发模式下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)