from flask import Flask
from flask_graphql import GraphQLView
from gql_server.schema import schema

app = Flask(__name__)
app.add_url_rule(
  '/graphql',
  view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)
app.run()