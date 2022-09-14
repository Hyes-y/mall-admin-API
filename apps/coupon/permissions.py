from rest_framework.permissions import BasePermission


class IsAdminOrCreateOnly(BasePermission):
    """
    사용자 발급 쿠폰 생성 권한
    운영자 : CRUD
    일반 회원 : C
    ERROR: Permission 01
    """
    message = "[ERROR: Permission 01] 접근 권한이 없습니다."

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return bool(request.user and request.user.is_staff)
