
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny

from courses.models import Course, CourseSubject

from .filters import CourseFilter
from .serializers import (
    CourseSerializer, CourseSubjectSerializer, PrivateCourseSerializer, CourseUpdateSerializer)


def is_true(value):
    return str(value).lower() in ['true', '1', 'y', 'yes']


class CourseAPIView(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    '''
    ## Filtering

    The API allows for filtering the list of courses.

    * By universities: `university=CNAM&university=CentraleParis`
    * By course subjects: `subject=philosophy&subject=science`
    * By availability:
        * `availability=start-soon`
        * `availability=end-soon`
        * `availability=enrollment-ends-soon`
        * `availability=new`
        * `availability=current`

    ## Pagination

    You can limit the number of Results Per Page using the `rpp`
    API parameter.

    * Pagination: `/api/courses/locations/?rpp=6`

    By default, pagination is set to 10.

    ## Ordering

    The results may be sorted by name, enrollment start date or start date
    using the `sort` API parameter.

    ## Extended List of Courses

    Only courses that are shown in the courses catalog are listed in the
    public API. Admin API users can access an extended list of courses -
    courses that are not shown in catalog. When logged in as admin,
    you can use the `extended_list` parameter.

    * Extended list: `/api/courses/?extended_list=True`

    '''
    filter_backends = (CourseFilter,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    paginate_by = 100
    paginate_by_param = 'rpp'
    max_paginate_by = None
    parser_classes = (JSONParser,)

    @property
    def is_admin(self):
        is_admin = self.request.user.is_staff or self.request.user.is_superuser
        return is_admin

    @property
    def extended_list(self):
        extended_list = self.request.query_params.get('extended_list')
        return is_true(extended_list)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.is_admin:
            if self.action == 'update':
                return CourseUpdateSerializer
            if self.action in ('retrieve', 'list'):
                return PrivateCourseSerializer
        if self.action in ('retrieve', 'list'):
            return CourseSerializer

    def get_queryset(self):
        if not (self.is_admin and self.extended_list):
            queryset = Course.objects.with_related().public()
        else:
            queryset = Course.objects.with_related()
        queryset = queryset.filter(is_active=True)
        return queryset


class CourseSubjectAPIView(
        mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    paginate_by = 100
    paginate_by_param = 'rpp'
    max_paginate_by = None
    queryset = CourseSubject.objects.all()
    serializer_class = CourseSubjectSerializer
