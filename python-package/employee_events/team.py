# Import the QueryBase class
from .query_base import QueryBase

# Import dependencies for SQL execution
from .sql_execution import QueryMixin

# Create a subclass of QueryBase called `Team`
class Team(QueryBase, QueryMixin):
    
    # Set the class attribute `name` to the string "team"
    name = "team"
    
    # Define a `names` method that receives no arguments
    # This method should return a list of tuples from an SQL execution
    def names(self):
        # Query 5
        # Write an SQL query that selects
        # the team_name and team_id columns
        # from the team table for all teams in the database
        query = f"""
        SELECT team_name, team_id
        FROM {self.name}
        """
        return self.query(query)

    # Define a `username` method that receives an ID argument
    # This method should return a list of tuples from an SQL execution
    def username(self, team_id):
        # Query 6
        # Write an SQL query that selects the team_name column
        # Use f-string formatting and a WHERE filter to only return
        # the team name related to the ID argument
        query = f"""
        SELECT team_name
        FROM {self.name}
        WHERE team_id = {team_id}
        """
        return self.query(query)

    # Below is a method with an SQL query
    # This SQL query generates the data needed for the machine learning model.
    # Without editing the query, alter this method so that when it is called,
    # a pandas dataframe is returned containing the execution of the SQL query
    def model_data(self, team_id):
        return f"""
            SELECT positive_events, negative_events FROM (
                SELECT employee_id,
                       SUM(positive_events) positive_events,
                       SUM(negative_events) negative_events
                FROM {self.name}
                JOIN employee_events
                    USING({self.name}_id)
                WHERE {self.name}.{self.name}_id = {team_id}
                GROUP BY employee_id
            )
        """
