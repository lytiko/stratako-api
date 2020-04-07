from datetime import datetime
import pytz
import graphene
from graphene.types import Scalar
from django.utils import timezone

class Datetime(Scalar):
    """A custom GraphQL type for representing datetimes. They take UTC datetimes
    and convert them to the user's local time. They also format them in a
    particular way when converting to string."""

    @staticmethod
    def serialize(dt):
        """Takes a Python datetime object and converts into a numerical
        timestamp."""
        
        return datetime.timestamp(dt)
    

    @staticmethod
    def parse_value(value):
        """Parses a JSON value sent to the server and turns it into a datetime
        object. This method handles data sent via the variables dictionary."""

        return datetime.fromtimestamp(float(value)).replace(tzinfo=pytz.UTC)
    

    @staticmethod
    def parse_literal(node):
        """Parses a string representing a datetime sent to the server, and turns
        it into that datetime. This method handles data sent as part of the
        query itself."""

        return Datetime.parse_value(node.value)



class Query(graphene.ObjectType):
    """The root query object. It supplies the user attribute, which is the
    portal through which other attributes are accessed."""

    user = graphene.Field("core.queries.UserType")
    

    def resolve_user(self, info, **kwargs):
        """Gets the user associated with the request, and returns that."""

        return info.context.user



schema = graphene.Schema(query=Query)