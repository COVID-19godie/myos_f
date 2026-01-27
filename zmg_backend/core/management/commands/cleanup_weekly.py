import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from core.models import Resource, DesktopIcon

class Command(BaseCommand):
    help = '每周清理规则：删除7天前的资源文件及其图标'

    def add_arguments(self, parser):
        # 允许通过命令行参数指定天数，默认7天
        parser.add_argument('--days', type=int, default=7, help='删除多少天前的数据')

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        self.stdout.write(f"正在扫描 {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} 之前的文件...")

        # 1. 查找过期的资源
        # 注意：这里我们排除了 'link' 类型的资源，只清理上传的物理文件
        # 如果你想连纯链接也清理，可以去掉 exclude
        expired_resources = Resource.objects.filter(
            created_at__lt=cutoff_date
        ).exclude(kind='link')

        count = expired_resources.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("没有发现过期文件，无需清理。"))
            return

        # 获取 Resource 对应的 ContentType ID，用于查找关联的桌面图标
        resource_ctype = ContentType.objects.get_for_model(Resource)

        success_count = 0
        for res in expired_resources:
            try:
                title = res.title
                
                # 2. 删除物理文件
                if res.file and os.path.isfile(res.file.path):
                    os.remove(res.file.path)
                    # 同时尝试清理空文件夹（可选）
                    try:
                        folder = os.path.dirname(res.file.path)
                        if not os.listdir(folder): # 如果文件夹空了
                            os.rmdir(folder)
                    except OSError:
                        pass
                
                # 3. 删除关联的桌面图标 (DesktopIcon)
                # 因为是 GenericForeignKey，Django 默认不会级联删除，需手动处理
                DesktopIcon.objects.filter(
                    content_type=resource_ctype,
                    object_id=res.id
                ).delete()

                # 4. 删除数据库记录
                res.delete()
                
                success_count += 1
                self.stdout.write(f"已删除: {title}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"删除失败 {res.id}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"清理完成！共清理了 {success_count} 个过期资源。"))