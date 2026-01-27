from rest_framework import viewsets, permissions, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Q
import os
import shutil
import zipfile
import uuid
from .models import Resource, Category, User, Comment, DesktopIcon
from .serializers import ResourceSerializer, CategorySerializer, UserSerializer, RegisterSerializer, CommentSerializer, DesktopIconSerializer

# --- 基础视图 ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['POST'])
    def view(self, request, pk=None):
        return Response({'status': 'ok'})
        
    @action(detail=True, methods=['POST'])
    def comment(self, request, pk=None):
        Comment.objects.create(
            user=request.user, 
            resource=self.get_object(), 
            content=request.data.get('content')
        )
        return Response({'status': 'success'})
        
    @action(detail=True, methods=['GET'])
    def comments(self, request, pk=None):
        return Response(CommentSerializer(self.get_object().comments.all(), many=True).data)

# --- 核心：桌面图标视图 ---
import os

class DesktopIconViewSet(viewsets.ModelViewSet):
    serializer_class = DesktopIconSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        根据 parent_id 过滤图标。
        parent_id=root 或不传 -> 返回桌面顶级图标
        parent_id=recent -> 返回最近创建的 20 个图标
        parent_id=image/doc/video/audio -> 返回对应类型的资源
        parent_id=123 -> 返回文件夹 ID 为 123 内部的图标
        """
        parent_id = self.request.query_params.get('parent_id')
        user = self.request.user

        # 基础查询：当前用户的图标
        qs = DesktopIcon.objects.filter(user=user)

        # === 核心逻辑：侧边栏过滤器 ===

        # 1. 桌面 (Root)
        if parent_id == 'root' or not parent_id:
            return qs.filter(parent_folder__isnull=True)

        # 2. 最近访问 (Recent) - 返回最近创建的 20 个图标
        elif parent_id == 'recent':
            return qs.order_by('-created_at')[:20]

        # 3. 库查询 (图片/文档/视频/音频)
        # 这里使用了 Django 的 ContentType 来跨表查询 Resource
        elif parent_id in ['image', 'doc', 'video', 'audio']:
            # 获取 Resource 模型的 ContentType ID
            resource_ct = ContentType.objects.get_for_model(Resource)

            # 筛选：图标指向的是 Resource，且 Resource 的 kind 符合要求
            # 使用子查询获取符合条件的 Resource ID
            target_resources = Resource.objects.filter(kind=parent_id).values('id')

            return qs.filter(
                content_type=resource_ct,
                object_id__in=target_resources
            )

        # 4. 普通文件夹进入
        else:
            return qs.filter(parent_folder_id=parent_id)

    @action(detail=True, methods=['PATCH'])
    def move(self, request, pk=None):
        """
        移动图标：支持修改坐标 (x, y) 和 父文件夹 (parent_id)
        """
        icon = self.get_object()
        
        # 1. 修改坐标
        if 'x' in request.data:
            icon.x = request.data['x']
        if 'y' in request.data:
            icon.y = request.data['y']
            
        # 2. 修改父文件夹 (实现拖拽归档)
        if 'parent_id' in request.data:
            pid = request.data['parent_id']
            if pid == 'root' or pid is None:
                icon.parent_folder = None
            else:
                icon.parent_folder_id = pid
                
        icon.save()
        return Response({'status': 'moved'})

    @action(detail=False, methods=['POST'])
    def create_folder(self, request):
        user = request.user
        name = request.data.get('name', '新建文件夹')
        x = request.data.get('x', 50)
        y = request.data.get('y', 50)
        parent_id = request.data.get('parent_id')
        
        # 处理 parent_id 为 'root' 的情况
        if parent_id == 'root': 
            parent_id = None

        # 1. 创建真实的 Category 对象
        real_folder = Category.objects.create(name=name, parent_id=parent_id, icon='folder')
        
        # 2. 创建桌面图标指向它
        icon = DesktopIcon.objects.create(
            user=user, 
            title=name, 
            content_object=real_folder, 
            x=x, 
            y=y, 
            parent_folder_id=parent_id
        )
        return Response(DesktopIconSerializer(icon).data)

    @action(detail=False, methods=['POST'])
    def upload_file(self, request):
        user = request.user
        file_obj = request.FILES.get('file')
        # 获取相对路径，例如 "MyFolder/Sub/test.txt"
        # 如果是单文件上传，这个值可能是 "undefined" 或空
        relative_path = request.data.get('relative_path', '')
        
        parent_id = request.data.get('parent_id')
        
        # 确定起始父文件夹
        current_parent_cat = None
        if parent_id and parent_id != 'root':
            try:
                current_parent_cat = Category.objects.get(id=parent_id)
            except Category.DoesNotExist:
                pass

        # === 核心逻辑：递归创建文件夹 ===
        if relative_path and '/' in relative_path:
            # 分割路径，去掉最后的文件名，只保留文件夹部分
            # 例如 "A/B/c.txt" -> ["A", "B"]
            path_parts = os.path.dirname(relative_path).split('/')
            
            for part_name in path_parts:
                if not part_name: continue
                
                # 1. 查找当前目录下是否已存在同名文件夹
                cat = Category.objects.filter(
                    name=part_name, 
                    parent=current_parent_cat
                ).first()
                
                # 2. 如果不存在，创建它
                if not cat:
                    cat = Category.objects.create(
                        name=part_name, 
                        parent=current_parent_cat, 
                        icon='folder'
                    )
                    # 重要：为新文件夹创建桌面图标，否则在桌面/窗口里看不到它
                    # 这里坐标随机生成，防止重叠
                    import random
                    DesktopIcon.objects.create(
                        user=user,
                        title=part_name,
                        content_object=cat,
                        parent_folder=current_parent_cat,
                        x=random.randint(50, 400),
                        y=random.randint(50, 300)
                    )
                
                # 3. 深入下一层
                current_parent_cat = cat

        # === 创建资源文件 ===
        # 此时 current_parent_cat 已经指向了最深层的文件夹
        res = Resource.objects.create(
            title=file_obj.name, 
            author=user, 
            file=file_obj, 
            category=current_parent_cat, 
            status='approved'
        )
        
        # 创建文件的图标
        import random
        icon = DesktopIcon.objects.create(
            user=user, 
            title=res.title, 
            content_object=res, 
            x=request.data.get('x', random.randint(50, 500)), 
            y=request.data.get('y', random.randint(50, 400)), 
            parent_folder=current_parent_cat # 链接到正确的父文件夹
        )
        
        return Response(DesktopIconSerializer(icon).data)

    @action(detail=True, methods=['POST'])
    def rename(self, request, pk=None):
        icon = self.get_object()
        new_name = request.data.get('name')
        if new_name:
            icon.title = new_name
            icon.save()
            # 可选：同步修改底层资源的名字
            if icon.content_object and hasattr(icon.content_object, 'title'):
                icon.content_object.title = new_name
                icon.content_object.save()
            elif icon.content_object and hasattr(icon.content_object, 'name'):
                icon.content_object.name = new_name
                icon.content_object.save()
                
        return Response({'status': 'renamed'})

    # [新增] 更换图标接口
    @action(detail=True, methods=['POST'])
    def change_icon(self, request, pk=None):
        icon = self.get_object()
        new_icon_class = request.data.get('icon_class')
        
        if not new_icon_class:
            return Response({'status': 'error', 'msg': '图标参数为空'}, status=400)

        # 获取实际关联的对象 (Resource 或 Category)
        obj = icon.content_object
        
        # 1. 如果是文件/应用 (Resource)
        if isinstance(obj, Resource):
            obj.icon_class = new_icon_class
            obj.save()
            
        # 2. 如果是文件夹 (Category)
        elif isinstance(obj, Category):
            # Category 模型原本的 icon 字段可能存的是 "folder" 这种简写
            # 现在我们直接存完整的类名，例如 "fa-solid fa-folder-open"
            obj.icon = new_icon_class
            obj.save()
            
        return Response({'status': 'success', 'msg': '图标已更新'})

    # [新增] H5 应用安装接口
    @action(detail=False, methods=['POST'])
    def create_link(self, request):
        user = request.user
        title = request.data.get('title')
        link = request.data.get('link')
        icon_class = request.data.get('icon_class')

        # 处理 parent_id 为 'root' 的情况
        parent_id = request.data.get('parent_id')
        if parent_id == 'root':
            parent_id = None

        # 创建资源
        res = Resource.objects.create(
            title=title,
            author=user,
            link=link,
            kind='link',
            icon_class=icon_class,
            status='approved'
        )

        # 创建桌面图标
        icon = DesktopIcon.objects.create(
            user=user,
            title=res.title,
            content_object=res,
            x=request.data.get('x', 50),
            y=request.data.get('y', 50),
            parent_folder_id=parent_id # 允许指定文件夹
        )
        return Response(DesktopIconSerializer(icon).data)

    # [新增] 创建 HTML/富文本文件
    @action(detail=False, methods=['POST'])
    def create_html_file(self, request):
        user = request.user
        title = request.data.get('title', '未命名文档')
        content = request.data.get('content', '<h1>Hello World</h1>')
        
        # 将字符串内容转换为文件
        file_content = ContentFile(content.encode('utf-8'))
        file_name = f"{title}.html"
        
        # 创建文档资源
        res = Resource.objects.create(
            title=title, author=user, kind='doc',
            icon_class='fa-brands fa-html5', status='approved'
        )
        res.file.save(file_name, file_content) # 保存文件
        
        # 创建图标
        icon = DesktopIcon.objects.create(
            user=user, title=title, content_object=res,
            x=request.data.get('x', 50), y=request.data.get('y', 50),
            parent_folder_id=request.data.get('parent_id')
        )
        return Response(DesktopIconSerializer(icon).data)

    # [新增] H5 应用安装接口 (处理 ZIP 上传与解压)
    @action(detail=False, methods=['POST'])
    def install_h5_app(self, request):
        import zipfile
        import uuid
        
        user = request.user
        file_obj = request.FILES.get('file')
        
        # 1. 获取基本参数
        title = request.data.get('title', '未命名应用')
        icon_class = request.data.get('icon_class', 'fa-solid fa-gamepad') # 默认给个游戏手柄图标
        
        if not file_obj:
             return Response({'status': 'error', 'msg': '未上传文件'}, status=400)

        # 2. 准备解压路径
        # 路径规则: media/h5apps/<应用名>_<随机ID>/
        # 使用 safe_name 过滤掉特殊字符，防止路径遍历攻击
        safe_name = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
        folder_name = f"{safe_name}_{uuid.uuid4().hex[:8]}"
        extract_root = os.path.join(settings.MEDIA_ROOT, 'h5apps', folder_name)
        
        if not os.path.exists(extract_root):
            os.makedirs(extract_root)
            
        # 3. 解压 ZIP 文件
        try:
            if not zipfile.is_zipfile(file_obj):
                 return Response({'status': 'error', 'msg': '请上传 ZIP 格式的压缩包'}, status=400)
                 
            with zipfile.ZipFile(file_obj, 'r') as zip_ref:
                zip_ref.extractall(extract_root)
        except Exception as e:
            # 如果解压出错，清理创建的空文件夹
            shutil.rmtree(extract_root)
            return Response({'status': 'error', 'msg': f'解压失败: {str(e)}'}, status=500)
            
        # 4. 智能寻找 index.html 入口
        # 有些压缩包里面直接是文件，有些可能包含一层文件夹
        entry_path = None
        for root, dirs, files in os.walk(extract_root):
            if 'index.html' in files:
                # 找到入口文件，计算相对于 MEDIA_ROOT 的路径
                full_path = os.path.join(root, 'index.html')
                # rel_path 例如: h5apps/MyGame_xxx/src/index.html
                entry_path = os.path.relpath(full_path, settings.MEDIA_ROOT)
                break
        
        if not entry_path:
            shutil.rmtree(extract_root) # 清理垃圾文件
            return Response({'status': 'error', 'msg': '压缩包内未找到 index.html 入口文件'}, status=400)
            
        # 5. 构造访问 URL (将文件路径转换为 URL 路径)
        # settings.MEDIA_URL 通常是 '/media/'
        # windows 下路径分隔符可能是 \，需要替换为 / 供浏览器使用
        app_link = os.path.join(settings.MEDIA_URL, entry_path).replace('\\', '/')
        
        # 6. 保存到数据库
        # 我们使用 'link' 类型，这样前端双击时会直接打开 URL
        res = Resource.objects.create(
            title=title,
            author=user,
            kind='link',         
            link=app_link,       
            icon_class=icon_class,
            status='approved'
        )
        
        # 7. 创建桌面图标
        # 处理 parent_id 为 'root' 的情况
        parent_id = request.data.get('parent_id')
        if parent_id == 'root':
            parent_id = None

        icon = DesktopIcon.objects.create(
            user=user,
            title=title,
            content_object=res,
            x=request.data.get('x', 50),
            y=request.data.get('y', 50),
            parent_folder_id=parent_id
        )

        return Response(DesktopIconSerializer(icon).data)

    # [核心修复] 万能删除接口 (支持文件夹、文件、应用)
    @action(detail=True, methods=['DELETE'])
    def uninstall(self, request, pk=None):
        try:
            # 1. 获取桌面图标
            icon = self.get_object()
            
            # 安全检查：确保图标存在且属于当前用户
            if icon.user != request.user:
                return Response({'status': 'error', 'msg': '无权删除此项目'}, status=403)

            # 获取图标指向的真实对象 (可能是 文件夹Category 或 文件Resource)
            obj = icon.content_object

            print(f">>> 正在删除: {icon.title} (类型: {type(obj).__name__ if obj else 'None'}, ID: {pk})")

            # 2. 情况A：如果有有效对象
            if obj:
                # 2.1 如果是文件夹 (Category)
                if isinstance(obj, Category):
                    try:
                        # 先删除该文件夹内的所有桌面图标（避免外键约束错误）
                        DesktopIcon.objects.filter(parent_folder=obj).delete()
                        
                        # 删除文件夹本体
                        obj.delete()
                        print("✅ 文件夹已删除")
                    except Exception as folder_error:
                        print(f"❌ 删除文件夹时出错: {folder_error}")
                        # 即使文件夹删除失败，也继续删除图标
                        
                # 2.2 如果是文件/应用 (Resource)
                elif isinstance(obj, Resource):
                    # 特殊处理：如果是 H5 应用，尝试删除物理文件目录
                    if obj.kind == 'link' and obj.link and '/h5apps/' in obj.link:
                        import shutil
                        from django.conf import settings
                        try:
                            # 更安全的路径解析
                            if settings.MEDIA_URL.startswith('/'):
                                clean_media_url = settings.MEDIA_URL[1:]  # 移除开头的 /
                            else:
                                clean_media_url = settings.MEDIA_URL
                                
                            if obj.link.startswith('/'):
                                clean_link = obj.link[1:]  # 移除开头的 /
                            else:
                                clean_link = obj.link
                            
                            # 解析相对路径
                            if clean_link.startswith(clean_media_url):
                                rel_path = clean_link[len(clean_media_url):]
                            else:
                                rel_path = clean_link
                                
                            if 'h5apps' in rel_path:
                                parts = [p for p in rel_path.split('/') if p]  # 过滤空字符串
                                # 路径格式: h5apps/app_name_hash/filename
                                if len(parts) >= 2:
                                    app_root = os.path.join(settings.MEDIA_ROOT, parts[0], parts[1])
                                    if os.path.exists(app_root):
                                        shutil.rmtree(app_root)
                                        print(f"✅ 物理文件夹已清除: {app_root}")
                                    else:
                                        print(f"⚠️ 物理文件夹不存在: {app_root}")
                                else:
                                    print(f"⚠️ H5应用路径格式不正确: {rel_path}")
                        except Exception as e:
                            print(f"⚠️ 物理文件清理出错 (不影响数据库删除): {e}")
                            # 记录错误但不中断删除流程

                    # 删除文件对象
                    try:
                        obj.delete()
                        print("✅ 文件资源已删除")
                    except Exception as resource_error:
                        print(f"❌ 删除资源时出错: {resource_error}")
                        # 即使资源删除失败，也继续删除图标
            
            # 3. 无论对象是否存在或删除是否成功，都删除桌面图标本身
            try:
                icon.delete()
                print("✅ 桌面图标已删除")
            except Exception as icon_error:
                print(f"❌ 删除图标时出错: {icon_error}")
                return Response({'status': 'error', 'msg': f'删除图标失败: {str(icon_error)}'}, status=500)

            return Response({'status': 'success', 'msg': '删除成功'})

        except DesktopIcon.DoesNotExist:
            return Response({'status': 'error', 'msg': '图标不存在'}, status=404)
        except Exception as e:
            # 打印详细错误方便调试
            import traceback
            traceback.print_exc()
            return Response({'status': 'error', 'msg': f'删除失败: {str(e)}'}, status=500)