from rest_framework import serializers
from .models import User, Resource, Category, Comment, DesktopIcon

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ['id', 'username', 'role', 'avatar', 'score', 'bio']

class CategorySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Category
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta: 
        model = Resource
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta: 
        model = Comment
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta: 
        model = User
        fields = ('username', 'password', 'email')
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# --- 核心：桌面图标序列化 ---
class DesktopIconSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField() # 新增预览字段

    class Meta:
        model = DesktopIcon
        fields = '__all__'

    def get_type(self, obj):
        if not obj.content_type: return 'unknown'
        return obj.content_type.model 

    def get_data(self, obj):
        if not obj.content_object: return {}
        
        # 如果是文件
        if obj.content_type.model == 'resource':
            res = obj.content_object
            return {
                'id': res.id,
                'title': res.title,
                'cover': res.cover.url if res.cover else None,
                'kind': res.kind,
                'file': res.file.url if res.file else None,
                'link': res.link
            }
        # 如果是文件夹
        elif obj.content_type.model == 'category':
            cat = obj.content_object
            return {
                'id': cat.id,
                'name': cat.name,
                'icon': cat.icon
            }
        return {}

    def get_preview(self, obj):
        """
        获取文件夹内部的前 4 个图标，用于前端九宫格显示
        """
        # 只有文件夹需要预览
        if not obj.content_type or obj.content_type.model != 'category':
            return []
            
        cat = obj.content_object
        if not cat: 
            return []

        # 查询属于这个文件夹的图标
        # 注意：这里我们查询 DesktopIcon 表，parent_folder 指向当前 category
        from .models import DesktopIcon # 局部引用防止循环导入
        children = DesktopIcon.objects.filter(parent_folder=cat).order_by('created_at')[:4]
        
        preview_list = []
        for child in children:
            item = {'type': 'unknown', 'cover': None}
            if child.content_type:
                item['type'] = child.content_type.model
                # 如果是资源且有封面，返回封面
                if child.content_type.model == 'resource':
                    res = child.content_object
                    if res and res.cover:
                        item['cover'] = res.cover.url
            preview_list.append(item)
            
        return preview_list