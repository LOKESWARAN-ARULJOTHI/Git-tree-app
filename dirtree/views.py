import os
import json
import requests as r
from dotenv import load_dotenv
from django.views import View
from .models import Number_of_trees_generated, User_email
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

load_dotenv()

# Class based view for Home page
class Home(View):
    # Get method to render the home page
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return render(request, "dirtree/index.html")
    
    # Post method that gets the url and generates Tree
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        repourl = body['repourl']
        link_in_parts = list(map(str, repourl.strip().split('/')))  #Splits the urls to get the username and repo name
        github_index = None
        for i in range(len(link_in_parts)):    # Finds the index of github.com to give the index of username and repo name
            if link_in_parts[i] == "github.com":
                github_index = i
                break
        user_name = link_in_parts[github_index+1]    # Github Username is stored in user_name
        repository_name = link_in_parts[github_index+2]    # Github Repository name is stored in repository_name
        store_email(user_name, repository_name)
        files_list = get_files([], user_name, repository_name, '')
        routes = create_Node(files_list)
        increment_notg()
        return HttpResponse(json.dumps(routes), content_type="application/json")



# number-of-trees-generated urlpattern response function  
def no_of_trees(request):
    trees_generated = Number_of_trees_generated.objects.get(id=1)
    return HttpResponse(trees_generated)
    
# increments the no of trees generated field in DB
def increment_notg():
    notg = Number_of_trees_generated.objects.get(id=1)
    notg.notg += 1
    notg.save()
    
# Fetches and stores the email id to the DB
def store_email(user_name, repository_name):
    email_get_response = r.get("https://api.github.com/repos/"+user_name+"/"+repository_name+"/commits", auth=(os.environ.get('GITHUB_USERNAME'), os.environ.get('TOKEN_KEY'))).json()    # Returns all the commits made in the repository
    email = email_get_response[0]["commit"]["author"]["email"]
    new_email = User_email.objects.get_or_create(email=email)

# Uses Github api to get the files and directories paths
def get_files(paths, user_name, repository_name, path=''):
    files_fetch_response = r.get("https://api.github.com/repos/"+user_name+"/"+repository_name+"/commits", auth=(os.environ.get('GITHUB_USERNAME'), os.environ.get('TOKEN_KEY'))).json()    # Returns all the commits made in the repository
    trees = r.get(files_fetch_response[0]["commit"]["tree"]["url"]+"?recursive=true").json()["tree"]    # gets the paths of files and directories from the latest commit
    paths=[]
    for tree in trees:
        paths.append(tree["path"])
    return paths

# Tree class to generate tree for a repo
class Node():
    def __init__(self,data):
        self.data = data
        self.children = []
        self.parent = None
    
    # returns the level of the node
    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    # Adds the child node to the parent node
    def add_child(self, child):
        for c in self.children:
            if child.data == c.data:
                return c    # if child already exists, returns it         
        else:
            child.parent = self
            self.children.append(child)
            return self.children[-1]    # appends the new child
        
    # dynamically returns the prefix of the files or directory in tree nodes
    def get_prefix(self, prefix):
        if self.parent:
            if self.parent.parent:
                parent = self.parent
                grand_parent = parent.parent
                if parent == grand_parent.children[-1]:
                    prefix = '   ' + prefix
                else:
                    prefix = '│  ' + prefix
                prefix = parent.get_prefix(prefix)
            else:
                prefix = '' + prefix
        else:
            prefix = '' + prefix
        return prefix
    
    # returns the Tree of the repository
    def get_tree(self,last_child = True, tree=[]):
        if self.data == "root":
            tree.append('.')
        else:
            prefix = ''
            prefix = self.get_prefix('')
            if last_child:    # adds prefix to the files or directory in tree nodes
                full_sentence = prefix + "└── " + self.data
            else:
                full_sentence = prefix + "├── " + self.data
            tree.append(full_sentence)
            
        if self.children:    # recursively calls the get_tree() if it has child
            for child in self.children:
                if child != self.children[-1]:
                    last_child = False
                else:
                    last_child = True
                child.get_tree(last_child,tree)
        
        return tree

# Create tree with the paths and returns the tree
def create_Node(files_list):
    root_copy = root = Node('root')
    
    for file_paths in files_list:    # Loops through each path in the paths list
        file_path = file_paths.split('/')
        for file in file_path:    # Loops throught each level from root to the file to add the child
            root = root.add_child(Node(file))
        root = root_copy
    
    return root.get_tree(True,[])
