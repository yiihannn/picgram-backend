import graphene
import hashlib
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from graphene import relay
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from webserver.graphql.errorMsg import ERR_INVALID_LOGIN, ERR_INVALID_SIGNUP
from django.contrib.auth.models import User

from webserver.graphql.utils import parse_global_id, encode_file_name
from webserver.models import Profile, Photo, Comment, Tag
from webserver.graphql.schema import UserNode, ProfileNode, CommentNode, PhotoNode, ActivityNode

fs = FileSystemStorage()


class LogIn(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        username = input["username"]
        user_password = input["password"]
        user = authenticate(username=username, password=user_password)
        if user is None:
            raise GraphQLError("Invalid login!", extensions=ERR_INVALID_LOGIN)
        login(request=info.context, user=user)
        return LogIn(user=user)


class SignUp(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        location = graphene.String(required=True)
        description = graphene.String(required=True)
        occupation = graphene.String(required=True)

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if User.objects.filter(username=input["username"]).exists():
            raise GraphQLError("Username has been taken!", extensions=ERR_INVALID_SIGNUP)
        user = User.objects.create_user(
            username=input["username"],
            password=input["password"],
            email=input["email"],
            first_name=input["first_name"],
            last_name=input["last_name"]
        )
        Profile(user=user,
                location=input["location"],
                description=input["description"],
                occupation=input["occupation"]).save()
        return SignUp(user=user)


class LogOut(relay.ClientIDMutation):
    code = graphene.Int()
    msg = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        logout(request=info.context)
        return LogOut(code=2000, msg="Log out successfully!")


class LikePhoto(relay.ClientIDMutation):
    code = graphene.Int()
    msg = graphene.String()

    class Input:
        photo_id = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        photo = Photo.objects.get(pk=parse_global_id(input['photo_id']))
        curr_user = User.objects.get(pk=info.context.user.id)
        doesContain = photo.liked.contains(curr_user)
        if doesContain:
            photo.liked.remove(curr_user)
        else:
            photo.liked.add(curr_user)
        photo.save()
        return LikePhoto(code=2000, msg="Like(or unlike) photo successfully!")


class MakeComment(relay.ClientIDMutation):
    code = graphene.Int()
    msg = graphene.String()

    class Input:
        photo_id = graphene.String(required=True)
        content = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        photo = Photo.objects.get(pk=parse_global_id(input['photo_id']))
        curr_user = User.objects.get(pk=info.context.user.id)
        comment = Comment(user=curr_user, comment=input['content'], photo=photo)
        comment.save()
        return MakeComment(code=2000, msg="Make comment successfully!")


class UploadPhoto(relay.ClientIDMutation):
    code = graphene.Int()
    msg = graphene.String()

    class Input:
        uploadPhoto = Upload(required=True)
        caption = graphene.String()
        location = graphene.String()
        tags = graphene.List(graphene.String)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        file_name = input['uploadPhoto']
        curr_user = User.objects.get(pk=info.context.user.id)
        photo = Photo(user=curr_user, file_name=file_name, location=input['location'], caption=input['caption'])
        photo.save()
        for tag in input['tags']:
            try:
                exist = Tag.objects.get(name__exact=tag)
            except Tag.DoesNotExist:
                Tag(name=tag).save()
                exist = Tag.objects.get(name__exact=tag)
            exist.photo.add(photo)
            exist.save()
        return UploadPhoto(code=2000, msg="Make comment successfully!")


class Mutation(graphene.ObjectType):
    log_in = LogIn.Field()
    sign_up = SignUp.Field()
    log_out = LogOut.Field()
    like_photo = LikePhoto.Field()
    make_comment = MakeComment.Field()
    upload_photo = UploadPhoto.Field()
