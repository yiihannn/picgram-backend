import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from django_filters import FilterSet, OrderingFilter, CharFilter, BaseInFilter
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from webserver.graphql.utils import parse_global_id
from webserver.models import Profile, Comment, Photo, Activity, Tag
from django.contrib.auth.models import User


class StringInFilter(BaseInFilter, CharFilter):
    pass


class PhotoFilter(FilterSet):
    user_in = StringInFilter(field_name="user_id", method='filter_global_id_in')
    tags_contain = CharFilter(method='filter_tags_contain')

    class Meta:
        fields = ["id", "user"]
        model = Photo

    order_by = OrderingFilter(fields=('date_time', ))

    def filter_global_id_in(self, queryset, name, value):
        ids = [int(parse_global_id(gid)) for gid in value]
        kwarg = {f'{name}__in': ids}
        return queryset.filter(**kwarg)

    def filter_tags_contain(self, queryset, name, value):
        vector = SearchVector('tag__name', weight='A') + SearchVector('caption', weight='A') \
                 + SearchVector('location', weight='A') + SearchVector('comment__comment', weight='B')
        query = SearchQuery(value)
        return queryset.annotate(rank=SearchRank(vector, query))\
            .filter(rank__gte=0.1).order_by('-rank').distinct('id', 'rank')


class PhotoNode(DjangoObjectType):
    class Meta:
        model = Photo
        interfaces = (relay.Node,)

    liked_count = graphene.Int()
    is_liked_by_curr = graphene.Boolean()
    photo_url = graphene.String()

    def resolve_liked_count(self, info):
        return self.liked.count()

    def resolve_is_liked_by_curr(self, info):
        curr_user = User.objects.get(pk=info.context.user.id)
        return self.liked.contains(curr_user)

    def resolve_photo_url(self, info):
        return self.file_name.url


class UserFilter(FilterSet):
    name_contain = CharFilter(method='filter_name_contain')

    class Meta:
        fields = ["id", "username"]
        model = User

    order_by = OrderingFilter(fields=('username',))

    def filter_name_contain(self, queryset, name, value):
        vector = SearchVector('username', weight='A') + SearchVector('first_name', weight='B') \
                 + SearchVector('last_name', weight='B')
        query = SearchQuery(value)
        return queryset.annotate(rank=SearchRank(vector, query))\
            .filter(rank__gte=0.1).order_by('-rank').distinct('id', 'rank')


class UserNode(DjangoObjectType):
    user_photos = DjangoFilterConnectionField(PhotoNode, filterset_class=PhotoFilter)

    class Meta:
        model = User
        filter_fields = ["id", "username", "email"]
        interfaces = (relay.Node, )

    def resolve_user_photos(self, info, **kwargs):
        return PhotoFilter(kwargs, queryset=self.user_photos).qs


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = ["id", "user"]
        interfaces = (relay.Node,)
    following_count = graphene.Int()
    follower_count = graphene.Int()

    def resolve_following_count(self, info):
        return self.following.count()

    def resolve_follower_count(self, info):
        return self.follower.count()


class TagFilter(FilterSet):

    class Meta:
        fields = ["id", "name"]
        model = Tag

    order_by = OrderingFilter(fields=('name', ))


class TagNode(DjangoObjectType):
    class Meta:
        model = Tag
        filter_fields = ["id", "name", "photo"]
        interfaces = (relay.Node,)

    photo_count = graphene.Int()

    def resolve_photo_count(self, info):
        return self.photo.count()


class CommentNode(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = ["id", "user"]
        interfaces = (relay.Node,)


class ActivityNode(DjangoObjectType):
    class Meta:
        model = Activity
        filter_fields = ["id", "user", "category"]
        interfaces = (relay.Node,)


