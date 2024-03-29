import graphene
from algoliasearch_django import update_records, save_record, delete_record
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from graphene import relay
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from webserver.graphql.errorMsg import ERR_INVALID_LOGIN, ERR_INVALID_SIGNUP, ERR_INVALID_FOLLOW
from webserver.graphql.schema import UserNode, ProfileNode
from webserver.graphql.utils import parse_global_id
from webserver.models import Profile, Photo, Comment, Tag

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
        email = graphene.String()
        location = graphene.String()
        description = graphene.String()
        occupation = graphene.String()

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
        qs = Photo.objects.filter(pk=parse_global_id(input['photo_id']))
        photo = qs[0]
        curr_user = User.objects.get(pk=info.context.user.id)
        comment = Comment(user=curr_user, comment=input['content'], photo=photo)
        comment.save()
        update_records(model=Photo, qs=qs, photo_comments={
            '_operation': 'Add',
            'value': input['content']
        })
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
        save_record(photo)
        return UploadPhoto(code=2000, msg="Make comment successfully!")


class FollowUser(relay.ClientIDMutation):
    curr_user = graphene.Field(UserNode)
    target_user = graphene.Field(UserNode)

    class Input:
        user_id = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):

        user = User.objects.get(pk=parse_global_id(input['user_id']))
        curr_user = User.objects.get(pk=info.context.user.id)
        if user == curr_user:
            raise GraphQLError("Invalid self-following!", extensions=ERR_INVALID_FOLLOW)
        isFollowed = curr_user.profile.following.contains(user)
        if isFollowed:
            curr_user.profile.following.remove(user)
            user.profile.follower.remove(curr_user)
        else:
            curr_user.profile.following.add(user)
            user.profile.follower.add(curr_user)
        curr_user.save()
        user.save()
        return FollowUser(curr_user=curr_user, target_user=user)


class ChangeAvatar(relay.ClientIDMutation):
    profile = graphene.Field(ProfileNode)

    class Input:
        newAvatar = Upload(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        new_avatar = input['newAvatar']
        profile = Profile.objects.get(user_id=info.context.user.id)
        profile.avatar = new_avatar
        profile.save()
        return ChangeAvatar(profile=profile)


class EditProfile(relay.ClientIDMutation):
    user = graphene.Field(UserNode)

    class Input:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        description = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        curr_user = User.objects.get(pk=info.context.user.id)
        curr_user.first_name = input["first_name"]
        curr_user.last_name = input["last_name"]
        curr_user.profile.description = input["description"]
        curr_user.profile.save()
        curr_user.save()
        return EditProfile(user=curr_user)


class DeletePhoto(relay.ClientIDMutation):
    code = graphene.Int()
    msg = graphene.String()

    class Input:
        photo_id = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        qs = Photo.objects.filter(pk=parse_global_id(input['photo_id']))
        photo = qs[0]
        delete_record(photo)
        photo.delete()
        return DeletePhoto(code=2001, msg="Delete photo successfully!")


class DeleteComment(relay.ClientIDMutation):
    code = graphene.Int()
    msg = graphene.String()

    class Input:
        photo_id = graphene.String(required=True)
        comment_id = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        qs = Photo.objects.filter(pk=parse_global_id(input['photo_id']))
        photo = qs[0]
        comment = Comment.objects.filter(pk=parse_global_id(input['comment_id']))
        comment.delete()
        comments = [c.comment for c in photo.comment_set.all()]
        update_records(model=Photo, qs=qs, photo_comments=comments)
        return MakeComment(code=2002, msg="Delete comment successfully!")


class Mutation(graphene.ObjectType):
    log_in = LogIn.Field()
    sign_up = SignUp.Field()
    log_out = LogOut.Field()
    like_photo = LikePhoto.Field()
    make_comment = MakeComment.Field()
    upload_photo = UploadPhoto.Field()
    follow_user = FollowUser.Field()
    change_avatar = ChangeAvatar.Field()
    edit_profile = EditProfile.Field()
    delete_photo = DeletePhoto.Field()
    delete_comment = DeleteComment.Field()

