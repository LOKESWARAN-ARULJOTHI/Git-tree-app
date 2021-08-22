from django.shortcuts import render
from django.http import HttpResponse
import requests as r
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import ensure_csrf_cookie
import json

# Create your views here.
no_of_trees_generated = 0
load_dotenv()
@ensure_csrf_cookie
def index(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        repourl = body['repourl']
        link_in_parts = list(map(str, repourl.strip().split('/')))
        github_index = None
        for i in range(len(link_in_parts)):
            if link_in_parts[i] == "github.com":
                github_index = i
                break
        user_name = link_in_parts[github_index+1]
        repository_name = link_in_parts[github_index+2]
        files_list = get_files([], user_name, repository_name, '')
        routes = create_Node(files_list)
        request.session['routes'] = routes
        global no_of_trees_generated
        no_of_trees_generated += 1
        return HttpResponse(json.dumps(routes), content_type="application/json")
    elif request.method == "GET":
        print(request.method)
        routes = request.session.get('routes',False)
        if routes: del request.session['routes']
        return render(request, "dirtree/index.html", context={"routes": routes})
    
def no_of_trees(request):
    return HttpResponse(no_of_trees_generated)

def get_files(paths, user_name, repository_name, path=''):
    response = r.get("https://api.github.com/repos/"+user_name+"/"+repository_name+"/commits", auth=(os.environ.get('GITHUB_USERNAME'), os.environ.get('TOKEN_KEY'))).json()
    trees = r.get(response[0]["commit"]["tree"]["url"]+"?recursive=true").json()["tree"]
    paths=[]
    for tree in trees:
        paths.append(tree["path"])
    return paths


class Node():
    def __init__(self,data):
        self.data = data
        self.children = []
        self.parent = None
    
    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def add_child(self, child):
        if self.children != []:
            for c in self.children:
                # print(c.data)
                if child.data == c.data:
                    return c           
            else:
                child.parent = self
                self.children.append(child)
                return self.children[-1]
        else:
            child.parent = self
            self.children.append(child)
            return self.children[-1]
        
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
    
    def print_Node(self,last_child = True, tree=[]):
        if self.data == "root":
            tree.append('.')
        else:
            prefix = ''
            prefix = self.get_prefix('')
            if last_child:
                full_sentence = prefix + "└── " + self.data
            else:
                full_sentence = prefix + "├── " + self.data
            tree.append(full_sentence)
            
        # last_parent = last_child
        if self.children:
            for child in self.children:
                if child != self.children[-1]:
                    last_child = False
                else:
                    last_child = True
                child.print_Node(last_child,tree)
        
        return tree

def create_Node(files_list):
    root1 = root = Node('root')
    
    for file_paths in files_list:
        file_path = file_paths.split('/')
        for file in file_path:
            root = root.add_child(Node(file))
        root = root1
    
    return root.print_Node(True,[])
