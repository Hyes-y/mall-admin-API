from rest_framework.permissions import BasePermission


class IsAdminOrCreateReadOnly(BasePermission):
    """
    사용자 발급 쿠폰 생성 권한
    사용자가 발급 받을 수 있어야 하므로 생성은 모두 허용
    수정, 삭제는 불가능
    운영자 : CRUD
    일반 회원 : CR
    ERROR: Permission 01
    """
    message = "[ERROR: Permission 01] 접근 권한이 없습니다."

    def has_permission(self, request, view):
        if request.method in ('GET', 'POST'):
            return True
        return bool(request.user and request.user.is_staff)
