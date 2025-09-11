"""
GraphQL schema for the backend gateway.
"""
import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_active')


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None


schema = graphene.Schema(query=Query)
