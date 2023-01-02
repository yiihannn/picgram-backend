from django.conf.urls.static import static
from django.urls import path

from django.conf import settings
# from . import views
#
# app_name = 'webserver'
# urlpatterns = [
#     # path('', views.home, name='home'),
#     # path('login-register', views.home, name='home'),
#     # path('login', views.login, name='login'),
#     # path('logout', views.logout, name='logout'),
#     # path('register', views.register, name='register'),
#     # path('user/list', views.user_list, name='user_list'),
#     # path('user/<str:user_id>', views.user_detail, name='user_detail'),
#     # path('photosOfUser/<str:user_id>', views.user_photos, name='user_photos'),
#     # path('photos/new', views.new_photo, name='new_photo'),
#     # path('commentsOfPhoto/<str:photo_id>', views.photo_comments, name='photo_comments'),
#     # path('activity/new', views.new_activity, name='new_activity'),
#     # path('activity/feed', views.activity_feed, name='activity_feed'),
#     # path('activity/feed/<str:user_id>', views.user_activity, name='user_activity'),
#     # path('mostRecent/<str:user_id>', views.most_recent, name='most_recent'),
#     # path('mostCommented/<str:user_id>', views.most_commented, name='most_commented'),
#     # path('mentioned/<str:user_id>', views.user_mentioned, name='user_mentioned'),
#
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from graphene_file_upload.django import FileUploadGraphQLView

urlpatterns = [
    path("graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
