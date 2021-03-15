from django import http
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .models import Student, Class, Teacher, Grade, ClassMaterials, ClassMaterialsChapter, ClassMaterialsModule, Files
import json
from django.http import HttpResponse

def index(request):
    if request.user.is_authenticated:
        return render(request, 'class/index.html')
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
                
        ctx = {'className': className, 'chap_mod': chap_mod, 'is_teacher':is_teacher}
    except Class.DoesNotExist:
        ctx = {}
        print('class Does not exist')
    return render(request, 'class/class.html', ctx)

def add_new_mat(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        classes = Class.objects.filter(teacher=teacher)
        ctx= {'classes': classes}
        return render(request, 'class/dependant_test.html', ctx)
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
            messages.success(request, "New material added successfully!")
            return redirect('class:add_new_mat')

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