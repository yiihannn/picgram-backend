# import datetime
#
# from bson import ObjectId
# from django.core.files.storage import FileSystemStorage
# from django.shortcuts import render
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.request import Request
# from rest_framework import status
#
# from django.contrib.auth.models import User
# from .models import Photo, Comment, Activity
#
# fs = FileSystemStorage()
#
#
# def home(request):
#     return render(request, 'webserver/home.html')
#
#
# @api_view(['POST'])
# def login(request: Request):
#     username = request.data['login_name']
#     pwd = request.data['password']
#     user = User.objects(username=username)
#     if not user:
#         return Response("username doesn't exist", status=status.HTTP_400_BAD_REQUEST)
#     user = user[0]
#     if pwd != user.password:
#         return Response("wrong password", status=status.HTTP_400_BAD_REQUEST)
#     request.session['user_id'] = str(user.id)
#     return Response({'_id': str(user.id)}, status=status.HTTP_200_OK)
#
#
# @api_view(['POST'])
# def logout(request):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     del request.session['user_id']
#     return Response("successfully log out", status=status.HTTP_200_OK)
#
#
# @api_view(['POST'])
# def register(request):
#     username = request.data['login_name']
#     user = User.objects(username=username)
#     if user:
#         return Response("user already exists", status=status.HTTP_400_BAD_REQUEST)
#     new_user = User(username=request.data['login_name'],
#                     password=request.data['password'],
#                     first_name=request.data['first_name'],
#                     last_name=request.data['last_name'],
#                     location=request.data['location'],
#                     description=request.data['description'],
#                     occupation=request.data['occupation'])
#     new_user.save()
#     request.session['user_id'] = str(new_user.id)
#     return Response({'_id': str(new_user.id)}, status=status.HTTP_200_OK)
#
#
# @api_view(['POST'])
# def new_photo(request: Request):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     if not request.FILES:
#         return Response("cannot find photo to upload", status=status.HTTP_400_BAD_REQUEST)
#     file = request.FILES['uploadedphoto'] if 'uploadedphoto' in request.FILES else None
#     upload_time = datetime.datetime.now()
#     filename = 'U' + upload_time.strftime('%m%d%Y-%H:%M:%S') + file.name
#     fs.save(filename, file)
#     user = User.objects(id=request.session['user_id'])
#     photo = Photo(file_name=filename, date_time=upload_time, user=user[0])
#     photo.save()
#     return Response({'_id': str(photo.id), 'msg': "success"}, status=status.HTTP_200_OK)
#
#
# @api_view(['POST'])
# def photo_comments(request: Request, photo_id):
#     print(request.data)
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     if not request.data['comment'] or len(request.data['comment']) == 0:
#         return Response("empty comment", status=status.HTTP_400_BAD_REQUEST)
#     photo = Photo.objects(id=ObjectId(photo_id))[0]
#     user = User.objects(id=request.session['user_id'])[0]
#     comment = Comment(comment=request.data['comment'], date_time=datetime.datetime.now(), user=user)
#     photo.update(push__comments=comment)
#     if 'mention' in request.data and len(request.data['mention']) > 0:
#         for mentioned in request.data['mention']:
#             mentioned_user = User.objects(id=mentioned)[0]
#             if mentioned_user not in photo.mentions:
#                 photo.update(push__mentions=mentioned_user)
#     return Response("comment successfully added", status=status.HTTP_200_OK)
#
#
# @api_view(['POST'])
# def new_activity(request: Request):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     user = User.objects(id=request.session['user_id'])[0]
#     date_time = datetime.datetime.now()
#     category = request.data['category']
#     content = request.data['content']
#     activity = Activity(user=user, date_time=date_time, category=category, content=content)
#     activity.save()
#     return Response("new activity added", status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def user_list(request):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     other = []
#     users = []
#     for u in User.objects().only('first_name', 'last_name'):
#         u = u.to_mongo()
#         u['_id'] = str(u['_id'])
#         if u['_id'] == request.session['user_id']:
#             users.append(u)
#         else:
#             other.append(u)
#     for o in other:
#         users.append(o)
#     return Response(users, status=status.HTTP_200_OK)
#
#
# # Return the information for User (id)
# @api_view(['GET'])
# def user_detail(request, user_id):
#     user = User.objects(id=ObjectId(user_id))
#     if not user:
#         return Response("user does not exist", status=status.HTTP_404_NOT_FOUND)
#     user = user[0].to_mongo()
#     user['_id'] = str(user['_id'])
#     return Response(user, status=status.HTTP_200_OK)
#
#
# # Return the Photos for User (id)
# @api_view(['GET'])
# def user_photos(request, user_id):
#     photos = Photo.objects(user=ObjectId(user_id))
#     if not photos:
#         return Response("user has no photo", status=status.HTTP_404_NOT_FOUND)
#     res = []
#     for p in photos:
#         p = p.to_mongo()
#         p['_id'] = str(p['_id'])
#         p['user'] = str(p['user'])
#         comments = []
#         for c in p['comments']:
#             commenter = User.objects(id=c['user']).first()
#             c['user'] = {}
#             c['user']['_id'] = str(commenter.id)
#             c['user']['first_name'] = commenter.first_name
#             c['user']['last_name'] = commenter.last_name
#             comments.append(c)
#         p['comments'] = comments
#         mentions = []
#         for m in p['mentions']:
#             mentions.append(str(m))
#         p['mentions'] = mentions
#         res.append(p)
#     return Response(res, status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def activity_feed(request):
#     activities = Activity.objects().order_by('-date_time')[:5]
#     res = []
#     for act in activities:
#         act = act.to_mongo()
#         act['_id'] = str(act['_id'])
#         user = User.objects(id=act['user'])[0]
#         act['first_name'] = user.first_name
#         act['last_name'] = user.last_name
#         act['user'] = str(act['user'])
#         cont = act['content']
#         if act['category'] == "comment":
#             author = User.objects(id=cont['author_id'])[0]
#             cont['author_first_name'] = author.first_name
#             cont['author_last_name'] = author.last_name
#         res.append(act)
#     return Response(res, status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def user_activity(request, user_id):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     activity = Activity.objects(user=user_id).order_by('-date_time').first()
#     activity = activity.to_mongo()
#     activity['_id'] = str(activity['_id'])
#     activity['user'] = str(activity['user'])
#     return Response(activity, status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def most_recent(request, user_id):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     photo = Photo.objects(user=user_id).order_by('-date_time').exclude('mentions', 'comments').first()
#     photo = photo.to_mongo()
#     photo['_id'] = str(photo['_id'])
#     photo['user'] = str(photo['user'])
#     return Response(photo, status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def most_commented(request, user_id):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     photos = Photo.objects(user=user_id).order_by('-date_time').exclude('mentions')
#     comment_cnt = 0
#     most_commented_photo = photos[0]
#     for p in photos:
#         if len(p.comments) > comment_cnt:
#             comment_cnt = len(p.comments)
#             most_commented_photo = p
#     most_commented_photo = most_commented_photo.to_mongo()
#     most_commented_photo['countComments'] = comment_cnt
#     most_commented_photo['_id'] = str(most_commented_photo['_id'])
#     most_commented_photo['user'] = str(most_commented_photo['user'])
#     comments = []
#     for c in most_commented_photo['comments']:
#         c['user'] = str(c['user'])
#         comments.append(c)
#     most_commented_photo['comments'] = comments
#     return Response(most_commented_photo, status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def user_mentioned(request, user_id):
#     if 'user_id' not in request.session:
#         return Response("no user logged in", status=status.HTTP_401_UNAUTHORIZED)
#     mention_photos = Photo.objects(mentions=user_id).order_by('-date_time').exclude('comments', 'mentions')
#     res = []
#     for mp in mention_photos:
#         mp = mp.to_mongo()
#         user = User.objects(id=mp['user'])[0]
#         mp['first_name'] = user.first_name
#         mp['last_name'] = user.last_name
#         mp['user'] = str(mp['user'])
#         mp['_id'] = str(mp['_id'])
#         res.append(mp)
#     return Response(res, status=status.HTTP_200_OK)
