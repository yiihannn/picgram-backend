import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from webserver.graphql.schema import UserNode, UserFilter, PhotoNode, PhotoFilter
from webserver.graphql.schema import TagNode, TagFilter


class Query(graphene.ObjectType):
    user = relay.Node.Field(UserNode)
    get_users = DjangoFilterConnectionField(UserNode, filterset_class=UserFilter)
    photo = relay.Node.Field(PhotoNode)
    get_photos = DjangoFilterConnectionField(PhotoNode, filterset_class=PhotoFilter)
    tag = relay.Node.Field(TagNode)
    get_tags = DjangoFilterConnectionField(TagNode, filterset_class=TagFilter)
