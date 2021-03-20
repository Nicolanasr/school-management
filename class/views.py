from os import name
import os
from django.conf import settings
from django import http
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import response
from django.http.response import Http404, HttpResponse
from django.shortcuts import redirect, render
from .models import Assignment, Comments, Student, Class, Teacher, Grade, ClassMaterials, ClassMaterialsChapter, ClassMaterialsModule, Files, Times, SubmittedAssignments
import json
from django.http import HttpResponse
import datetime 

def index(request):
    if request.user.is_authenticated:
        time = ''
        try:
            us = Student.objects.get(user=request.user)
            classes = us.className.all()
        except:
            us = Teacher.objects.get(user=request.user)
            classes = us.class_set.all()
        dai = []
        sched = {}
        # for days in Times.get_all_days():
        #     for cl in classes:
        #         if len(cl.times_set.filter(day=days[0])) > 0:
        #             if days[0] not in dai:
        #                 # print(days[0], ': ')
        #                 dai.append(days[0])
        #                 sched[days[0]] = [{cl.name: cl.times_set.filter(day=days[0])[0].time}]
        #             else:
        #                 sched[days[0]].append({cl.name: cl.times_set.filter(day=days[0])[0].time})
        #                 pass
        for days in Times.get_all_days():
            times = Times.objects.filter(day=days[0])
            for time in times:
                if us == time.class_name.teacher or us in time.class_name.student_set.all():
                    print(days[0], time.class_name, time.time)
                    if days[0] not in dai:
                        dai.append(days[0])
                        sched[days[0]] = [{time.class_name: time.time}]
                    else:
                        sched[days[0]].append({time.class_name: time.time})
                        pass
        print(sched)
        for s in sched:
            print(s, sched[s])
            # for time in cl.times_set.all():
            #     print('class: ', time.class_name, 'day: ', time.day, 'time: ', time.time)
        return render(request, 'class/index.html', {'days': dai, 'sched': sched, 'classes': classes})
    else:
        return redirect('index:login')

def class_info(request, class_name):
    if(request.user.groups.filter(name='Teachers').exists()):
        is_teacher = True
    else:
        is_teacher = False
    ctx = {}
    try:
        className = Class.objects.get(name = class_name)
        class_assignments = Assignment.objects.filter(class_name=className)
        status_list = []
        for cl in class_assignments:
            try:
                stat = cl.submittedassignments_set.get(submitted_by=request.user)
                status_list.append(stat.status)
            except:
                if cl.due_date < datetime.date.today():
                    status_list.append('missed')
                else:
                    status_list.append('awaiting submission')

        chapters = ClassMaterialsChapter.objects.filter(className = className).order_by('-date_added')
        chap_mod = {}
        for chapter in chapters:
            module = ClassMaterialsModule.objects.filter(chapter=chapter)
            # print('chapter: ', chapter, ' module: ', module)
            chap_mod[chapter] = module
        # print(chap_mod)

        # for c in chap_mod:
        #     for m in chap_mod[c]:
        #         print(m.files_set.all())

        comments = Comments.objects.filter(class_name=className, parent=None)
        if request.method == 'POST':
            parent_obj = None
            new_comment = request.POST.get('new_comment')
            try:
                parent_id = request.POST.get('parent_id')
            except:
                parent_id = None

            if parent_id:
                parent_qs = Comments.objects.get(id=parent_id)
                if parent_qs:
                    print(parent_qs)
                    parent_obj = parent_qs

            print('parent_id', parent_id)
            new_c = Comments(author=request.user, text=new_comment, class_name=className, parent=parent_obj)
            new_c.save()
            return redirect('class:class_info', class_name)
                
        ctx = {'className': className, 'chap_mod': chap_mod, 'is_teacher':is_teacher, 'comments': comments, 'class_assignments': class_assignments, 'status_list': status_list}
    except Class.DoesNotExist:
        ctx = {}
        print('class Does not exist')
    return render(request, 'class/class.html', ctx)

def add_new_mat(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        classes = Class.objects.filter(teacher=teacher)
        ctx= {'classes': classes}
        return render(request, 'class/add_new_material.html', ctx)
    except:
        return redirect('class:index')

def getdetails(request):
    data = {}
    if request.is_ajax():
        class_id = request.POST.get('class_name')
        chapter_id = request.POST.get('chapter')

        title = request.POST.get('name')
        url = request.POST.get('url_name')
        module_id = request.POST.get('module')
        if class_id != None and chapter_id != None and module_id != None:
            module = ClassMaterialsModule.objects.get(id=module_id)
            files = Files(ClassMaterialsModule=module, file_name=title, url=url)
            files.save()
            cl = Class.objects.get(id=class_id)
            print('saving')
            messages.success(request, "New material added successfully!")
            return redirect('class:class_info', cl)

        class_name = request.POST.get('class')
        data['class_name'] = class_name
        print("ajax class_name ", data)

        result_set = []
        all_chapters = []
        answer = str(class_name[1:-1])
        try:
            selected_class = Class.objects.get(name=answer)
            all_chapters = selected_class.classmaterialschapter_set.all()
            print("selected class name ", selected_class)
        except:
            try:
                selected_chapter = ClassMaterialsChapter.objects.get(id=class_name)
                all_chapters = selected_chapter.classmaterialsmodule_set.all()
            except:
                return JsonResponse('', safe=False)
            
        
        for chapter in all_chapters:
            result_set.append({'name': chapter.name, 'id': chapter.id})
        print(result_set)

        return JsonResponse(result_set, safe=False)
        # return HttpResponse(json.dumps(result_set), mimetype='application/json',     content_type='application/json')

    else:
        return redirect('class:add_new_mat')

def new_chapter(request):
    if request.method == 'POST':
        class_name = request.POST.get('class_id_for_new_chapter')
        new_chapter = request.POST.get('new_chapter')
        new_chapter_desc = request.POST.get('new_chapter_desc')
        class_name = Class.objects.get(id=class_name)
        if class_name.classmaterialschapter_set.filter(name=new_chapter):
            messages.warning(request, "Chapter name: \'" + str(new_chapter) + "\' already exists in this class")
            return redirect('class:add_new_mat')
        else:
            if class_name.teacher.user == request.user:
                new_chap = ClassMaterialsChapter(name=new_chapter, className=class_name, description=new_chapter_desc)
                new_chap.save()
                class_name = class_name.name
                messages.success(request, str(new_chapter) + " Added successfully to " + str(class_name))
                return redirect('class:add_new_mat')
            else:
                messages(request, 'You do not have access to this class')
                return redirect('class:add_new_mat')
    else:
        return redirect('class:add_new_mat')

def new_module(request):
    if request.method == 'POST':
        chapter_id = request.POST.get('chapter_id_for_new_module')
        new_module = request.POST.get('new_module')
        new_module_desc = request.POST.get('new_module_desc')
        chapter = ClassMaterialsChapter.objects.get(id=chapter_id)
        print(chapter.classmaterialsmodule_set.filter(name=new_module))
        if chapter.classmaterialsmodule_set.filter(name=new_module):
            messages.warning(request, "Module name: \'" + str(new_module) + "\' already exists in this chapter")
            return redirect('class:add_new_mat')
        else:
            teacher = chapter.className.teacher
            if teacher.user == request.user:
                new_mod = ClassMaterialsModule(name=new_module, chapter=chapter, description=new_module_desc)
                new_mod.save()
                messages.success(request, str(new_module) + " Added successfully to " + str(chapter.name))
                return redirect('class:add_new_mat')
            else:
                messages(request, 'You do not have access to this chapter')
                return redirect('class:add_new_mat')
    else:
        return redirect('class:add_new_mat')
        
def class_assignment(request, class_name, class_assignment_id):
    # if request.method == 'POST':

    assignment = Assignment.objects.get(id=class_assignment_id)
    try:
        submitted = SubmittedAssignments.objects.get(assignment=assignment, submitted_by=request.user)
        stat = submitted.status
        grade = submitted.grade
    except:
        stat = 'awaiting submission'
        grade = ''
    ass_class = assignment.class_name
    try:
        student = Student.objects.get(user=request.user)
        cl = student.className.all()
        for c in cl:
            if class_name in c.name:
                student_class = True
    except:
        student_class = False
        pass
    if ass_class.teacher.user == request.user or student_class:
        if request.method == 'POST':
            file_posted = request.FILES.get('file')
            print(request.FILES.get('file'))
            file = SubmittedAssignments(submitted_by=request.user, assignment=assignment, files=file_posted, status='submitted')
            file.save()
            return redirect('class:class_info', class_name)
    else:
        return redirect('class:index')
    ctx = {'assignment': assignment, 'status': stat, 'grade': grade, 'class_name': class_name}
    return render(request, 'class/assignment.html', ctx)

def new_assignment(request, class_name):
    try: 
        Class.objects.get(name=class_name)
    except:
        return redirect('class:index')
    if request.method == 'POST':
        class_name = Class.objects.get(name=class_name)
        title = request.POST.get('title')
        description = request.POST.get('description')
        noted = request.POST.get('noted')
        points = request.POST.get('points')
        if points == '':
            points = None
        due_date = request.POST.get('due_date')
        assignment = Assignment(title=title, description=description, noted=noted, points=points, class_name=class_name, due_date=due_date)
        assignment.save()
        return redirect('class:class_info', class_name.name)
    return render(request, 'class/new_assignment.html')

def submitted_assignment(request, class_name, assignment):
    try: 
        class_name = Class.objects.get(name=class_name)
    except:
        return redirect('class:index')
    if request.user.groups.filter(name='Teachers').exists():
        if request.method == 'POST':
            ass = Assignment.objects.get(id=assignment)
            points = request.POST.get('points')
            submitted_id = request.POST.get('submitted_id')
            if int(points) > ass.points:
                print('you cant do that')
            else:
                print(points)
                SubmittedAssignments.objects.select_for_update().filter(id=submitted_id).update(
                    grade=points, status='graded'
                )

        assignment = Assignment.objects.filter(id=assignment)
        for a in assignment[0].submittedassignments_set.all():
            print(a.files)
        ctx = {'assignment': assignment}
        return render(request, 'class/submitted_assignments.html', ctx)
    else:
        return redirect('class:class_info', class_name)



# def new_for_class(request):
#     groups = request.user.groups.all()
#     ctx = {}
#     if (request.user.groups.filter(name='Teachers').exists()):
#         teacher = Teacher.objects.get(user=request.user)
#         teacher_classes = Class.objects.filter(teacher=teacher)

#         ctx = {'teacher_classes': teacher_classes}
#     if request.method == 'POST':
#         classe = request.POST.get('class')
#         print(classe)
#         try:
#             Class.objects.get(id=classe)
#         except:
#             messages.error(request, 'Please Select a class first') 
#             return render(request, 'class/test.html', ctx)

#         return redirect('class:new_for_chapter', classe)

#     return render(request, 'class/test.html', ctx)

# def new_for_chapter(request, classe):
#     print(classe)
#     ctx = {}
#     try:
#         classe = Class.objects.get(id=classe)
#         ctx = {'class':classe}
#     except:
#         messages.error(request, 'Please Select a class first')
#         return redirect('class:new_for_class')
#     if request.method == 'POST':
#         chapter = request.POST.get('chapter')
#         try:
#             ClassMaterialsChapter.objects.get(id=chapter)
#         except:
#             messages.error(request, 'Please Select a chapter first') 
#             return render(request, 'class/test.html', ctx)
        
#         return redirect('class:new_for_module', chapter)
       
#     return render(request, 'class/test.html', ctx)

# def new_for_module(request, chapter):
#     try:
#         chapter = ClassMaterialsChapter.objects.get(id=chapter)
#         ctx = {'chapter': chapter}
#     except:
#         messages.error(request, 'Please Select a class first') 
#         return redirect('class:new_for_class')    

#     if request.method == 'POST':
#         module = request.POST.get('module')
#         try:
#             module = ClassMaterialsModule.objects.get(id=module)
#         except:
#             messages.error(request, 'Please Select a module first')
#         return redirect('class:adding_materials', module.chapter.className, module.chapter, module)

#     return render(request, 'class/test.html', ctx)

# def adding_materials(request, class_name, chapter_name, module_name):
#     ctx = {'all_info':(class_name, chapter_name, module_name)}
#     try:
#         classe = Class.objects.get(name=class_name)
#         if classe.teacher.user.username != request.user.username:
#             messages.error(request, 'You do not have access to that page')
#             return redirect('class:index')
        
#         c = classe.classmaterialschapter_set.all()
#         for clas in c:
#             if chapter_name == clas.name:
#                 c = clas
#                 break
#         mod = c.classmaterialsmodule_set.all()
#         for m in mod:
#             if module_name == m.name:
#                 modu = m
#                 break
#     except:
#         messages.error(request, 'Something went wrong')

#     if request.method == 'POST':
#         mat_name = request.POST.get('name')
#         mat_url = request.POST.get('url')
        
#         f = Files(file_name=mat_name, url=mat_url, ClassMaterialsModule=modu)
#         f.save()
#         return redirect('class:index')
        

#     return render(request, 'class/test.html', ctx)