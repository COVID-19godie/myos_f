"""
API视图 - 支持前端通信
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from core.models import User
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API登录接口 - 使用SimpleJWT"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'detail': '用户名和密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user:
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username,
                'user_id': user.id
            })
        else:
            return Response({
                'success': False,
                'detail': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'success': False,
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """API退出登录接口"""
    try:
        # 删除用户的token
        Token.objects.filter(user=request.user).delete()
        
        return Response({
            'success': True,
            'message': '退出登录成功'
        })
    except Exception as e:
        return Response({
            'success': False,
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_info(request):
    """获取用户信息接口"""
    try:
        user = request.user
        return Response({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_files_list(request):
    """获取文件列表接口"""
    try:
        # 这里应该从数据库或文件系统获取真实数据
        # 暂时返回模拟数据
        mock_files = [
            {
                'id': 1,
                'name': '工作报告.docx',
                'type': 'document',
                'size': 2048576,
                'modified': '2024-01-15T10:30:00Z',
                'path': '/documents/工作报告.docx'
            },
            {
                'id': 2,
                'name': '项目截图.png',
                'type': 'image',
                'size': 1024000,
                'modified': '2024-01-14T15:20:00Z',
                'path': '/images/项目截图.png'
            },
            {
                'id': 3,
                'name': '演示视频.mp4',
                'type': 'video',
                'size': 15728640,
                'modified': '2024-01-13T09:45:00Z',
                'path': '/videos/演示视频.mp4'
            },
            {
                'id': 4,
                'name': '音乐文件.mp3',
                'type': 'music',
                'size': 5242880,
                'modified': '2024-01-12T20:15:00Z',
                'path': '/music/音乐文件.mp3'
            }
        ]
        
        return Response({
            'success': True,
            'data': mock_files,
            'count': len(mock_files)
        })
    except Exception as e:
        return Response({
            'success': False,
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_search(request):
    """搜索接口"""
    try:
        query = request.GET.get('q', '')
        
        if not query:
            return Response({
                'success': False,
                'detail': '搜索关键词不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 模拟搜索结果
        results = [
            {
                'id': 1,
                'name': f'{query}_相关文档.docx',
                'type': 'document',
                'relevance': 0.95
            }
        ]
        
        return Response({
            'success': True,
            'data': results,
            'query': query
        })
    except Exception as e:
        return Response({
            'success': False,
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upload_file(request):
    """文件上传接口"""
    try:
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'detail': '没有文件被上传'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        
        # 这里应该处理文件保存逻辑
        # 暂时返回成功响应
        return Response({
            'success': True,
            'message': '文件上传成功',
            'data': {
                'filename': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.content_type
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def health_check(request):
    """健康检查接口"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': '2024-01-15T10:00:00Z',
        'version': '1.0.0'
    })