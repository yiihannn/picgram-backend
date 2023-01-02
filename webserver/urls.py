from django.http import HttpResponse


from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from graphene_file_upload.django import FileUploadGraphQLView

urlpatterns = [
    path("graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    re_path(r'^.*$', TemplateView.as_view(template_name='webserver/home.html'), name='home')
]
