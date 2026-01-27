# 文件名: add_tencent.py
import os
import sys
import django

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
# 添加 zmg_backend 到 Python 路径，这样才能找到 core.models
sys.path.insert(0, os.path.join(project_root, 'zmg_backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zmg_backend.settings')
django.setup()

from core.models import Resource, DesktopIcon, User

def add_tencent_icon():
    # 1. 获取管理员用户 (或你想添加给的用户)
    try:
        user = User.objects.get(username='admin') # 确保你的用户名是 admin
    except User.DoesNotExist:
        print("❌ 找不到用户 admin，请修改脚本中的用户名")
        return

    # 2. 定义腾讯文档链接
    docs = [
        {
            'title': '腾讯文档',
            'link': 'https://docs.qq.com/desktop',
            'icon': 'fa-solid fa-file-signature',
            'x': 50, 'y': 200 # 放在左侧靠下位置
        }
    ]

    for item in docs:
        # 检查是否已存在，防止重复添加
        if Resource.objects.filter(title=item['title'], author=user).exists():
            print(f"⚠️ {item['title']} 已存在，跳过")
            continue

        # 创建资源
        res = Resource.objects.create(
            title=item['title'],
            author=user,
            kind='link',
            link=item['link'],
            icon_class=item['icon'],
            status='approved'
        )

        # 创建桌面图标
        DesktopIcon.objects.create(
            user=user,
            title=item['title'],
            content_object=res,
            x=item['x'],
            y=item['y']
        )
        print(f"✅ 成功添加: {item['title']}")

if __name__ == '__main__':
    add_tencent_icon()