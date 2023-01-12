import graphene
from django.contrib.auth.models import User
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from webserver.graphql.schema import TagNode, TagFilter
from webserver.graphql.schema import UserNode, UserFilter, PhotoNode, PhotoFilter


class Query(graphene.ObjectType):
    user = relay.Node.Field(UserNode)
    get_users = DjangoFilterConnectionField(UserNode, filterset_class=UserFilter)
    photo = relay.Node.Field(PhotoNode)
    get_photos = DjangoFilterConnectionField(PhotoNode, filterset_class=PhotoFilter)
    tag = relay.Node.Field(TagNode)
    get_tags = DjangoFilterConnectionField(TagNode, filterset_class=TagFilter)
    current_user = graphene.Field(UserNode)

    def resolve_current_user(self, info):
        return User.objects.get(pk=info.context.user.id)

