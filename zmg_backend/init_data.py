#!/usr/bin/env python
"""
数据初始化脚本 - 生成测试用户、分类和资源
"""
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zmg_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Category, Resource
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

def create_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    # 创建管理员
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'role': 'admin',
            'score': 1000,
            'bio': '系统管理员'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("创建管理员: admin")
    
    # 创建教师
    teacher_user, created = User.objects.get_or_create(
        username='teacher_zhang',
        defaults={
            'email': 'teacher@example.com',
            'role': 'teacher',
            'score': 500,
            'bio': '资深物理教师，专注高中物理教学'
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        print("创建教师: teacher_zhang")
    
    # 创建学生
    student_user, created = User.objects.get_or_create(
        username='student_li',
        defaults={
            'email': 'student@example.com',
            'role': 'student',
            'score': 100,
            'bio': '高三学生，热爱学习'
        }
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
        print("创建学生: student_li")
    
    return admin_user, teacher_user, student_user

def create_categories():
    print("2. 创建层级分类...")
    desktop, _ = Category.objects.get_or_create(name='Desktop', defaults={'icon': 'desktop', 'parent': None})
    
    # [新增] Windows 风格标准库
    docs, _ = Category.objects.get_or_create(name='我的文档', defaults={'icon': 'file-lines', 'parent': None})
    pics, _ = Category.objects.get_or_create(name='图片', defaults={'icon': 'image', 'parent': None})
    vids, _ = Category.objects.get_or_create(name='视频', defaults={'icon': 'film', 'parent': None})
    music, _ = Category.objects.get_or_create(name='音乐', defaults={'icon': 'music', 'parent': None})
    downloads, _ = Category.objects.get_or_create(name='下载', defaults={'icon': 'download', 'parent': None})
    
    # --- 2. 其他顶级分类 ---
    science, _ = Category.objects.get_or_create(name='理科', defaults={'icon': 'atom', 'parent': None})
    arts, _ = Category.objects.get_or_create(name='文科', defaults={'icon': 'book-open', 'parent': None})
    general, _ = Category.objects.get_or_create(name='通用', defaults={'icon': 'layout-grid', 'parent': None})
    
    # --- 3. 子分类 ---
    subs = [
        ('物理', science), ('数学', science), ('化学', science),
        ('历史', arts), ('哲学', arts),
        ('文档', general), ('工具', general)
    ]
    
    cat_map = {'Desktop': desktop, '我的文档': docs, '图片': pics, '视频': vids, '音乐': music, '下载': downloads, '理科': science, '文科': arts, '通用': general}
    
    for name, parent in subs:
        c, _ = Category.objects.get_or_create(name=name, defaults={'parent': parent, 'icon': 'folder'})
        cat_map[name] = c
        
    return cat_map

def create_resources(users, categories):
    """创建测试资源"""
    print("创建测试资源...")
    
    admin, teacher, student = users
    
    # 创建模拟文件内容
    fake_pdf = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n'
    
    resources_data = [
        {
            'title': '牛顿运动定律详解',
            'description': '详细讲解牛顿三大运动定律，包含公式推导和实际例题分析。适合高一学生学习物理力学基础。',
            'author': teacher,
            'category': categories['物理'],
            'file_content': fake_pdf,
            'status': 'approved',
        },
        {
            'title': '电磁感应专题训练',
            'description': '高二物理电磁学重点内容，包含楞次定律、法拉第电磁感应定律的公式推导和典型例题。',
            'author': teacher,
            'category': categories['化学'],  # 改为化学分类，因为电磁学不存在
            'file_content': fake_pdf,
            'status': 'approved',
        },
        {
            'title': '2024年高考物理模拟试卷',
            'description': '最新高考物理模拟试题，涵盖力学、电磁学、光学等各个知识点，附详细答案解析。',
            'author': admin,
            'category': categories['物理'],
            'file_content': fake_pdf,
            'status': 'approved',
        },
    ]
    
    for res_data in resources_data:
        # 创建模拟文件
        file_name = res_data['title'] + '.pdf'
        uploaded_file = SimpleUploadedFile(
            file_name,
            res_data['file_content'],
            content_type='application/pdf'
        )
        
        resource, created = Resource.objects.get_or_create(
            title=res_data['title'],
            defaults={
                'description': res_data['description'],
                'author': res_data['author'],
                'category': res_data['category'],
                'file': uploaded_file,
                'status': res_data['status'],
            }
        )
        
        if created:
            print("创建资源: " + resource.title)

if __name__ == '__main__':
    print("开始初始化测试数据...")
    
    # 创建用户
    users = create_users()
    
    # 创建分类
    categories = create_categories()
    
    # 创建资源
    create_resources(users, categories)
    
    print("数据初始化完成！")
    print("测试账号信息：")
    print("管理员: admin / admin123")
    print("教师: teacher_zhang / teacher123")
    print("学生: student_li / student123")
