import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

import json

from django_instance.settings import JS_TIME_FORMAT
from schedule import models

def get_all_projects(user: User):
    projects = models.Project.objects.filter(user_instance = user)
    all_projects = []
    for project in projects:
        proj_dict = project.dict_with_convert_time_field_to_json()
        all_projects.append(proj_dict)
    return HttpResponse(json.dumps(all_projects))

def create_new_project(project_info:dict, user: User):
    try:
        name = project_info["name"]
        expire_date = project_info["expire_date"]
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps({"error": "Bad POST"}), status = 422)
    
    if name == "":
        name = "PlaceHolder"  
        
    if expire_date == "" :
        expire_date = None
    else:
        expire_date = datetime.datetime.strptime(expire_date, JS_TIME_FORMAT)

    new_project = models.Project.objects.create(
        user_instance = user,
        name = name,
        expire_date = expire_date
    )
    new_project.save()
    return HttpResponse(json.dumps(new_project.dict_with_convert_time_field_to_json()))

def get_project(project_id: int):
    try:
        project = models.Project.objects.get(id = project_id)
    except ObjectDoesNotExist:
        return HttpResponse(
            json.dumps({"error": "Bad ID"}), 
            status = 404
        )
    else:
        return HttpResponse(
            json.dumps(project.dict_with_convert_time_field_to_json())
        )
        
def edit_project(project_id:int, project_info: dict):
    try:
        name = project_info["name"]
        expire_date = project_info["expire_date"]
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps({"error": "Bad POST"}), status = 422)
    
    try:
        project = models.Project.objects.get(id = project_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"error": "Bad ID"}), status = 404)

    if 0 < len(name) <= 100: 
        project.name = name
    else:
        return HttpResponse(json.dumps({"error": "Bad POST"}), status=422)
    
    if expire_date == "" :
        expire_date = None
    else:
        expire_date = datetime.datetime.strptime(expire_date, JS_TIME_FORMAT)
    project.expire_date = expire_date
    
    project.save()
    return HttpResponse(project.dict_with_convert_time_field_to_json())

def delete_project(project_id:int):
    try:
        project_to_delete = models.Project.objects.get(pk = project_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"error": "Bad ID"}), status = 404)
    response = HttpResponse(json.dumps(project_to_delete.dict_with_convert_time_field_to_json()))
    project_to_delete.delete()
    return response