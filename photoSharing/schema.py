import graphene
import webserver.graphql.query
import webserver.graphql.mutation


class Query(webserver.graphql.query.Query, graphene.ObjectType):
    pass


class Mutation(webserver.graphql.mutation.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

