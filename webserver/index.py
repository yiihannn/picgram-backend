
from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from webserver.models import Photo, Profile


@register(Profile)
class UserIndex(AlgoliaIndex):
    fields = ('global_id', 'username', 'first_name', 'last_name', 'description', 'occupation', 'location', 'avatar_url')
    settings = {'searchableAttributes': ['username', 'first_name', 'last_name',
                                         'description', 'occupation', 'location']}
    index_name = 'user'


@register(Photo)
class PhotoIndex(AlgoliaIndex):
    fields = ('global_id', 'file_name', 'caption', 'location', 'date_time', 'photo_tags', 'photo_comments', 'photo_url')
    settings = {'searchableAttributes': ['caption', 'location', 'photo_tags', 'photo_comments']}
    index_name = 'photo'



