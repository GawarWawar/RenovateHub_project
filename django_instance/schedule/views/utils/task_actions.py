import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

import json

from django_instance.settings import JS_TIME_FORMAT
from schedule import models

def get_all_tasks(project:models.Project):    
    tasks = models.Task.objects.filter(project_instance = project)
    all_tasks = []
    for task in tasks:
        proj_dict = task.dict_with_convert_time_field_to_json()
        all_tasks.append(proj_dict)
    return HttpResponse(json.dumps(all_tasks))

def create_new_task(task_info:dict, project:models.Project):
    try:
        task_description = task_info["description"]
    except MultiValueDictKeyError:
        return HttpResponse(json.dumps({"error": "Bad POST"}), status = 422)
        
    if task_description != "" and len(task_description) < 1000:
        new_task = models.Task.objects.create(
            project_instance = project,
            description = task_description,
            priority = 0,
        )
        new_task.save()
        return HttpResponse(new_task.dict_with_convert_time_field_to_json())
    else:
        return HttpResponse(json.dumps({"error": "Bad POST"}), status=422)
    
def get_task(task:models.Task):
    HttpResponse(json.dumps(task.dict_with_convert_time_field_to_json()))
        
def edit_task(task:models.Task, task_info: dict):
    try:
        description = task_info["description"]
    except MultiValueDictKeyError:
        description = task.description
    else:
        if 0 < len(description) < 1000: 
            task.description = description
        else:
            return HttpResponse(json.dumps({"error": "Bad POST"}), status=422)
        
    try:
        expire_date = task_info["expire_date"]
    except MultiValueDictKeyError:
        expire_date = task.expire_date
    else:
        if expire_date == "" or expire_date is None:
            expire_date = None
        else:
            expire_date = datetime.datetime.strptime(expire_date, JS_TIME_FORMAT)
            task.expire_date = expire_date
    
    try:
        task.is_completed = task_info["is_completed"]
    except MultiValueDictKeyError:
        pass
    
    task.save()
    return HttpResponse(task.dict_with_convert_time_field_to_json())

def delete_task(task:models.Task):
    respnse = HttpResponse(json.dumps(task.dict_with_convert_time_field_to_json()))
    task.delete()
    return respnse