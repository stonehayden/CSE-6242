import http.client
import json
import csv
import requests
from copy import deepcopy
import time


#############################################################################################################################
# cse6242 
# All instructions, code comments, etc. contained within this notebook are part of the assignment instructions.
# Portions of this file will auto-graded in Gradescope using different sets of parameters / data to ensure that values are not
# hard-coded.
#
# Instructions:  Implement all methods in this file that have a return
# value of 'NotImplemented'. See the documentation within each method for specific details, including
# the expected return value
#
# Helper Functions:
# You are permitted to write additional helper functions/methods or use additional instance variables within
# the `Graph` class or `TMDbAPIUtils` class so long as the originally included methods work as required.
#
# Use:
# The `Graph` class  is used to represent and store the data for the TMDb co-actor network graph.  This class must
# also provide some basic analytics, i.e., number of nodes, edges, and nodes with the highest degree.
#
# The `TMDbAPIUtils` class is used to retrieve Actor/Movie data using themoviedb.org API.  We have provided a few necessary methods
# to test your code w/ the API, e.g.: get_movie_cast(), get_movie_credits_for_person().  You may add additional
# methods and instance variables as desired (see Helper Functions).
#
# The data that you retrieve from the TMDb API is used to build your graph using the Graph class.  After you build your graph using the
# TMDb API data, use the Graph class write_edges_file & write_nodes_file methods to produce the separate nodes and edges
# .csv files for use with the Argo-Lite graph visualization tool.
#
# While building the co-actor graph, you will be required to write code to expand the graph by iterating
# through a portion of the graph nodes and finding similar artists using the TMDb API. We will not grade this code directly
# but will grade the resulting graph data in your Argo-Lite graph snapshot.
#
#############################################################################################################################


class Graph:

    # Do not modify
    def __init__(self, with_nodes_file=None, with_edges_file=None):
        """
        option 1:  init as an empty graph and add nodes
        option 2: init by specifying a path to nodes & edges files
        """
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0], n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0], e[1]) for e in edges_CSV]


    def add_node(self, id: str, name: str) -> None:
        """
        add a tuple (id, name) representing a node to self.nodes if it does not already exist
        The graph should not contain any duplicate nodes
        """
        name = name.replace(",", "")
        id = str(id)
        node = (id, name)
        if node not in self.nodes:
            self.nodes.append(node)
        # return NotImplemented


    def add_edge(self, source: str, target: str) -> None:
        """
        Add an edge between two nodes if it does not already exist.
        An edge is represented by a tuple containing two strings: e.g.: ('source', 'target').
        Where 'source' is the id of the source node and 'target' is the id of the target node
        e.g., for two nodes with ids 'a' and 'b' respectively, add the tuple ('a', 'b') to self.edges
        """
        # int causes error when writing file
        source = str(source)
        target = str(target)

        edge = (source, target)
        if edge not in self.edges and (target, source) not in self.edges:
            self.edges.append(edge)


    def total_nodes(self) -> int:
        """
        Returns an integer value for the total number of nodes in the graph
        """
        return len(self.nodes)

    def total_edges(self) -> int:
        """
        Returns an integer value for the total number of edges in the graph
        """
        return len(self.edges)

    def max_degree_nodes(self) -> dict:
        """
        Return the node(s) with the highest degree
        Return multiple nodes in the event of a tie
        Format is a dict where the key is the node_id and the value is an integer for the node degree
        e.g. {'a': 8}
        or {'a': 22, 'b': 22}
        """
        # finding number of undirected edges incident on each node
        node_degree = {}
        for node in self.nodes:
            node_degree[node[0]] = 0
        for edge in self.edges:
            node_degree[edge[0]] += 1
            node_degree[edge[1]] += 1
        # finding max degree
        max_degree = max(node_degree.values())
        max_degree_nodes = {}
        for node, degree in node_degree.items():
            # if degree is greater than overwriting max_degree_nodes dict
            if degree > max_degree:
                max_degree_nodes = {node: degree}
            # if degree and max degree is equal then add node to max_degree_nodes dict
            if node_degree[node] == max_degree:
                max_degree_nodes[node] = max_degree

        return max_degree_nodes


    def get_number_of_non_leaf_vertices(self):
        """
        function to return number of nodes that have degree greater than 1
        :return: int
        """
        # finding number of undirected edges incident on each node
        node_degree = {}
        for node in self.nodes:
            node_degree[node[0]] = 0
        for edge in self.edges:
            node_degree[edge[0]] += 1
            node_degree[edge[1]] += 1

        count = 0
        for node, degree in node_degree.items():
            if int(degree) > 1:
                count += 1

        return count


    def print_nodes(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.nodes)


    def print_edges(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.edges)


    # Do not modify
    def write_edges_file(self, path="edges.csv")->None:
        """
        write all edges out as .csv
        :param path: string
        :return: None
        """
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")


    # Do not modify
    def write_nodes_file(self, path="nodes.csv")->None:
        """
        write all nodes out as .csv
        :param path: string
        :return: None
        """
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")



class  TMDBAPIUtils:

    # Do not modify
    def __init__(self, api_key:str):
        self.api_key=api_key

    def get_movie_cast(self, movie_id:str, limit:int=None, exclude_ids:list=None) -> list:
        """
        Get the movie cast for a given movie id, with optional parameters to exclude an cast member
        from being returned and/or to limit the number of returned cast members
        documentation url: https://developers.themoviedb.org/3/movies/get-movie-credits

        :param string movie_id: a numerical movie_id
        :param integer limit: maximum number of returned cast members by their 'order' attribute
            e.g., limit=5 will attempt to return the 5 cast members having 'order' attribute values between 0-4
            If after excluding, there are fewer cast members than the specified limit, then return the remaining members (excluding the ones whose order values are outside the limit range). 
            If cast members with 'order' attribute in the specified limit range have been excluded, do not include more cast members to reach the limit.
            If after excluding, the limit is not specified, then return all remaining cast members."
            e.g., if limit=5 and the actor whose id corresponds to cast member with order=1 is to be excluded,
            return cast members with order values [0, 2, 3, 4], not [0, 2, 3, 4, 5]
        :param list exclude_ids: a list of ints containing ids (not cast_ids) of cast members  that should be excluded from the returned result
            e.g., if exclude_ids are [353, 455] then exclude these from any result.
        :rtype: list
            return a list of dicts, one dict per cast member with the following structure:
                [{'id': 97909 # the id of the cast member
                'character': 'John Doe' # the name of the character played
                'credit_id': '52fe4249c3a36847f8012927' # id of the credit, ...}, ... ]
                Note that this is an example of the structure of the list and some of the fields returned by the API.
                The result of the API call will include many more fields for each cast member.

        Important: the exclude_ids processing should occur prior to limiting output.
        """
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={self.api_key}&language=en-US"
        while True:
            try:
                response = requests.get(url)
                break
            except:
                time.sleep(1)
                pass

        response_json = response.json()
        cast_members = response_json['cast']
        cast_members_to_return = []
        # if limit is defined
        if limit is not None:
            # keep adding cast till we reach required limit
            while True:
                # if there are not cast_members left in list then break
                if len(cast_members_to_return) == int(limit) or len(cast_members) == 0:
                    break
                cast_member = cast_members.pop(0)
                # if cast member is not in exclude_ids then add to cast_members_to_return
                if exclude_ids:
                    if cast_member['id'] in exclude_ids:
                        continue

                # now checking if order is in required limit
                if cast_member['order'] < limit:
                    cast_members_to_return.append(cast_member)
        else:
            # if limit is None
            for cm in cast_members:
                # if cast member is not in exclude_ids then add to cast_members_to_return
                if exclude_ids:
                    if cm['id'] in exclude_ids:
                        continue

                cast_members_to_return.append(cm)

        return cast_members_to_return

    def get_movie_credits_for_person(self, person_id:str, vote_avg_threshold:float=None)->list:
        """
        Using the TMDb API, get the movie credits for a person serving in a cast role
        documentation url: https://developers.themoviedb.org/3/people/get-person-movie-credits

        :param string person_id: the id of a person
        :param vote_avg_threshold: optional parameter to return the movie credit if it is >=
            the specified threshold.
            e.g., if the vote_avg_threshold is 5.0, then only return credits with a vote_avg >= 5.0
        :rtype: list
            return a list of dicts, one dict per movie credit with the following structure:
                [{'id': 97909 # the id of the movie credit
                'title': 'Long, Stock and Two Smoking Barrels' # the title (not original title) of the credit
                'vote_avg': 5.0 # the float value of the vote average value for the credit}, ... ]
        """
        url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits?api_key={self.api_key}&language=en-US"
        while True:
            try:
                response = requests.get(url)
                break
            except:
                time.sleep(1)
                pass
        response_json = response.json()
        movie_cast = response_json['cast']

        cast_to_return = []

        # if vote_avg_threshold is defined
        if vote_avg_threshold is not None:
            cast_to_return = [cast for cast in movie_cast if cast['vote_average'] >= vote_avg_threshold]
            # for cast in movie_cast:
            #     if cast['vote_average'] >= vote_avg_threshold:
            #         cast_to_return.append(cast)
        else:
            cast_to_return = movie_cast

        return cast_to_return


#############################################################################################################################
#
# BUILDING YOUR GRAPH
#
# Working with the API:  See use of http.request: https://docs.python.org/3/library/http.client.html#examples
#
# Using TMDb's API, build a co-actor network for the actor's/actress' highest rated movies
# In this graph, each node represents an actor
# An edge between any two nodes indicates that the two actors/actresses acted in a movie together
# i.e., they share a movie credit.
# e.g., An edge between Samuel L. Jackson and Robert Downey Jr. indicates that they have acted in one
# or more movies together.
#
# For this assignment, we are interested in a co-actor network of highly rated movies; specifically,
# we only want the top 3 co-actors in each movie credit of an actor having a vote average >= 8.0.
# Build your co-actor graph on the actor 'Laurence Fishburne' w/ person_id 2975.
#
# You will need to add extra functions or code to accomplish this.  We will not directly call or explicitly grade your
# algorithm. We will instead measure the correctness of your output by evaluating the data in your argo-lite graph
# snapshot.
#
# GRAPH SIZE
# With each iteration of your graph build, the number of nodes and edges grows approximately at an exponential rate.
# Our testing indicates growth approximately equal to e^2x.
# Since the TMDB API is a live database, the number of nodes / edges in the final graph will vary slightly depending on when
# you execute your graph building code. We take this into account by rebuilding the solution graph every few days and
# updating the auto-grader.  We establish a bound for lowest & highest encountered numbers of nodes and edges with a
# margin of +/- 100 for nodes and +/- 150 for edges.  e.g., The allowable range of nodes is set to:
#
# Min allowable nodes = min encountered nodes - 100
# Max allowable nodes = max allowable nodes + 100
#
# e.g., if the minimum encountered nodes = 507 and the max encountered nodes = 526, then the min/max range is 407-626
# The same method is used to calculate the edges with the exception of using the aforementioned edge margin.
# ----------------------------------------------------------------------------------------------------------------------
# BEGIN BUILD CO-ACTOR NETWORK
#
# INITIALIZE GRAPH
#   Initialize a Graph object with a single node representing Laurence Fishburne
#
# BEGIN BUILD BASE GRAPH:
#   Find all of Laurence Fishburne's movie credits that have a vote average >= 8.0
#   FOR each movie credit:
#   |   get the movie cast members having an 'order' value between 0-2 (these are the co-actors)
#   |
#   |   FOR each movie cast member:
#   |   |   using graph.add_node(), add the movie cast member as a node (keep track of all new nodes added to the graph)
#   |   |   using graph.add_edge(), add an edge between the Laurence Fishburne (actress) node
#   |   |   and each new node (co-actor/co-actress)
#   |   END FOR
#   END FOR
# END BUILD BASE GRAPH
#
#
# BEGIN LOOP - DO 2 TIMES:
#   IF first iteration of loop:
#   |   nodes = The nodes added in the BUILD BASE GRAPH (this excludes the original node of Laurence Fishburne!)
#   ELSE
#   |    nodes = The nodes added in the previous iteration:
#   ENDIF
#
#   FOR each node in nodes:
#   |  get the movie credits for the actor that have a vote average >= 8.0
#   |
#   |   FOR each movie credit:
#   |   |   try to get the 3 movie cast members having an 'order' value between 0-2
#   |   |
#   |   |   FOR each movie cast member:
#   |   |   |   IF the node doesn't already exist:
#   |   |   |   |    add the node to the graph (track all new nodes added to the graph)
#   |   |   |   ENDIF
#   |   |   |
#   |   |   |   IF the edge does not exist:
#   |   |   |   |   add an edge between the node (actor) and the new node (co-actor/co-actress)
#   |   |   |   ENDIF
#   |   |   END FOR
#   |   END FOR
#   END FOR
# END LOOP
#
# Your graph should not have any duplicate edges or nodes
# Write out your finished graph as a nodes file and an edges file using:
#   graph.write_edges_file()
#   graph.write_nodes_file()
#
# END BUILD CO-ACTOR NETWORK
# ----------------------------------------------------------------------------------------------------------------------

# Exception handling and best practices
# - You should use the param 'language=en-US' in all API calls to avoid encoding issues when writing data to file.
# - If the actor name has a comma char ',' it should be removed to prevent extra columns from being inserted into the .csv file
# - Some movie_credits may actually be collections and do not return cast data. Handle this situation by skipping these instances.
# - While The TMDb API does not have a rate-limiting scheme in place, consider that making hundreds / thousands of calls
#   can occasionally result in timeout errors. If you continue to experience 'ConnectionRefusedError : [Errno 61] Connection refused',
#   - wait a while and then try again.  It may be necessary to insert periodic sleeps when you are building your graph.


def return_name()->str:
    """
    Return a string containing your GT Username
    e.g., gburdell3
    Do not return your 9 digit GTId
    """
    return "shayden33"


def return_argo_lite_snapshot()->str:
    """
    Return the shared URL of your published graph in Argo-Lite
    """
    return "https://poloclub.github.io/argo-graph-lite/#04e3bfe9-4a9a-4b3a-a112-5f06b52013ff"



# You should modify __main__ as you see fit to build/test your graph using  the TMDBAPIUtils & Graph classes.
# Some boilerplate/sample code is provided for demonstration. We will not call __main__ during grading.

if __name__ == "__main__":
    graph = Graph()
    graph.add_node(id='2975', name='Laurence Fishburne')
    tmdb_api_utils = TMDBAPIUtils(api_key='fb221aacd147661e5fd762c4c7588512')

    # call functions or place code here to build graph (graph building code not graded)
    # Suggestion: code should contain steps outlined above in BUILD CO-ACTOR NETWORK

    movie_credit = tmdb_api_utils.get_movie_credits_for_person(person_id='2975', vote_avg_threshold=8.0)
    nodes = []
    edges = []
    for movie in movie_credit:
        movie_id = movie.get('id')
        if movie_id is None:
            continue

        cast_members = tmdb_api_utils.get_movie_cast(movie_id=movie['id'], limit=3)
        for cast_member in cast_members:
            node = (cast_member['id'], cast_member['name'])
            edge = ('2975', cast_member['id'])
            nodes.append(node)
            edges.append(edge)
            if node not in graph.nodes:
                graph.add_node(cast_member['id'], cast_member['name'])
            # using graph.add_edge(), add an edge between the Laurence Fishburne (actress) node and each new node
            # (co-actor/co-actress)
            if edge not in graph.edges:
                graph.add_edge(source='2975', target=cast_member['id'])

    graph.write_edges_file()
    graph.write_nodes_file()

    for i in range(2):
        if i == 0:
            # creating a deep copy
            nodes = deepcopy(graph.nodes)
            # removing original Laurence Fishburne node
            nodes.remove(('2975', 'Laurence Fishburne'))
        else:
            # nodes = nodes added in previous iteration
            pass

        for node in nodes:
            movie_credit = tmdb_api_utils.get_movie_credits_for_person(person_id=node[0], vote_avg_threshold=8.0)
            # waiting for 1 sec after each api call
            time.sleep(1)
            for movie in movie_credit:
                movie_id = movie.get('id')
                if movie_id is None:
                    print(movie)
                    continue
                cast_members = tmdb_api_utils.get_movie_cast(movie_id=movie['id'], limit=3)
                # waiting for 1 sec after each api call
                time.sleep(1)
                for cast_member in cast_members:
                    if (cast_member['id'], cast_member['name']) not in graph.nodes:
                        graph.add_node(cast_member['id'], cast_member['name'])
                        nodes.append((cast_member['id'], cast_member['name']))

                    edge = ('2975', cast_member['id'])
                    if edge not in edges:
                        edges.append(edge)
                        graph.add_edge(source=node[0], target=cast_member['id'])


    # If you have already built & written out your graph, you could read in your nodes & edges files
    # to perform testing on your graph.
    # graph = Graph(with_edges_file="edges.csv", with_nodes_file="nodes.csv")
