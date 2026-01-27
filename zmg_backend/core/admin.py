from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Resource, Category

# 用户管理
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'score', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'score', 'avatar', 'bio')}),
    )

# 资源审核后台
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at', 'link_or_file')
    list_filter = ('status', 'category')
    search_fields = ('title', 'author__username')
    list_editable = ('status',) # 允许在列表页直接改状态(快速审核)
    
    def link_or_file(self, obj):
        return "📁 文件" if obj.file else "🔗 链接"

admin.site.register(Category)
