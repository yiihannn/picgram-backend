from graphql import GraphQLError

from webserver.graphql.errorMsg import ERR_NOT_AUTHENTICATED


class AuthorizationMiddleware(object):
    def __init__(self):
        self.white_list = ['logIn', 'signUp', 'logOut']

    def resolve(self, next, root, info, **args):
        if root is None:
            if info.field_name not in self.white_list and not info.context.user.is_authenticated:
                raise GraphQLError("No user logged in!", extensions=ERR_NOT_AUTHENTICATED)
        return next(root, info, **args)
