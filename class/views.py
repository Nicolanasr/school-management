from os import name
import os
from django.conf import settings
from django import http
from django.http import JsonResponse
from django.contrib.auth.models import PermissionManager, User
from django.contrib import messages
from django.http import response
from django.http.response import Http404, HttpResponse
from django.shortcuts import redirect, render
from .models import Assignment, Comments, Results, Student, Class, Teacher, Grade, ClassMaterials, ClassMaterialsChapter, ClassMaterialsModule, Files, Times, SubmittedAssignments, Quiz, Answers, Question
import json
from django.http import HttpResponse
from datetime import datetime, timezone, timedelta
import datetime
import re

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
        # print(sched)
        # for s in sched:
        #     print(s, sched[s])
        #     # for time in cl.times_set.all():
        #     #     print('class: ', time.class_name, 'day: ', time.day, 'time: ', time.time)
        grades = []
        gr_int = []
        if(request.user.groups.filter(name='Students').exists()):
            for class_name in classes:
                try:
                    grade = Grade.objects.get(studentName=us, className=class_name)
                    grades.append(grade)
                    gr_int.append(round((grade.grade/grade.number_of_total_grades)*100, 2))
                except:
                    pass
        elif (request.user.groups.filter(name='Teachers').exists()):
            grades = 'not_student'
            print('You are not a student')
        if len(grades) == 0:
            grades = None

        print(grades)
            
        ctx = {'days': dai, 'sched': sched, 'classes': classes, 'grades': grades, 'gr_int': gr_int}
        return render(request, 'class/index.html', ctx)
    else:
        return redirect('index:login')

def class_info(request, class_name):
    if(request.user.groups.filter(name='Teachers').exists()):
        is_teacher = True
    else:
        is_teacher = False
    ctx = {}
    try:
        try:
            className = Class.objects.get(name=class_name)
        except Class.DoesNotExist:
            print('Class Does not exist')
            return redirect('class:index')
        try:
            student = Student.objects.get(user=request.user)
            cl = student.className.all()
            for c in cl:
                if class_name in c.name:
                    student_class = True
        except:
            student_class = False
            pass
        if className.teacher.user == request.user or student_class:
            pass
        else:
            print('you do not have access')
            return redirect('class:index')
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
        quizes = Quiz.objects.filter(class_name=className)
        quizes_list = []
        # print(Student.objects.filter(className=className))
        for quiz in quizes:
            timezone_offset = + 2.0 
            tzinfo = timezone(timedelta(hours=timezone_offset))
            if quiz.max_time_to_take > datetime.datetime.now(tzinfo) and len(quiz.results_set.filter(user=request.user)) == 0:
                quizes_list.append(quiz)
            for student in Student.objects.filter(className=className):
                if quiz.max_time_to_take < datetime.datetime.now(tzinfo) and len(quiz.results_set.filter(user=student.user)) == 0 :
                    Results(user=student.user, quiz=quiz, score=0).save()
                    number_of_total_grades = int(quiz.points)
                    gr = 0
                    try:
                        grade = Grade.objects.get(className=className, studentName=student)
                        number_of_total_grades = grade.number_of_total_grades + int(quiz.points)
                        gr = grade.grade + 0
                    except Grade.DoesNotExist:
                        grade = Grade(className=className, studentName=student)
                        grade.save()
                        print(grade.studentName)
                    Grade.objects.select_for_update().filter(className=className, studentName=student).update(number_of_total_grades=number_of_total_grades, grade=gr)
        
        assignments = Assignment.objects.filter(class_name=className)
        assignments_list = []
        # print(Student.objects.filter(className=className))
        date_now = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
        for assignment in assignments:
            for student in Student.objects.filter(className=className):
                if assignment.due_date < date_now and len(SubmittedAssignments.objects.filter(assignment=assignment, submitted_by=student.user)) == 0 and assignment.noted:
                    SubmittedAssignments(assignment=assignment, submitted_by=student.user, grade=0, status="graded").save()
                    number_of_total_grades = int(assignment.points)
                    gr = 0
                    try:
                        grade = Grade.objects.get(className=className, studentName=student)
                        number_of_total_grades = grade.number_of_total_grades + int(assignment.points)
                        gr = grade.grade + 0
                    except Grade.DoesNotExist:
                        grade = Grade(className=className, studentName=student)
                        grade.save()
                        print(grade.studentName)
                    Grade.objects.select_for_update().filter(className=className, studentName=student).update(number_of_total_grades=number_of_total_grades, grade=gr)



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
                
        ctx = {'className': className, 'chap_mod': chap_mod, 'is_teacher':is_teacher, 'comments': comments, 'class_assignments': class_assignments, 'status_list': status_list, 'quizes': quizes_list}
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
            try:
                cl = Class.objects.get(id=class_id)
            except Class.DoesNotExist:
                print('Class Does not exist')
                return redirect('class:index')
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
        try:
            class_name = Class.objects.get(id=class_name)
        except Class.DoesNotExist:
            print('Class Does not exist')
            return redirect('class:index')
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

def view_all_submitted_assignment(request, class_name):
    try:
        cl = Class.objects.get(name=class_name)
    except Class.DoesNotExist:
        print('Class does not exist')
        return redirect('class:index')
        
    if request.user.groups.filter(name='Teachers').exists() and cl.teacher.user == request.user:
        all_ass = Assignment.objects.filter(class_name=cl)
        ctx = {'all_ass': all_ass, 'class_name': cl}
        return render(request, 'class/view_all_submitted_assignment.html', ctx)
    else:
        print('You do not have access')
        return redirect('class:class_info', class_name)

def view_submitted_assignment(request, class_name, assignment):
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
                submitted_by = SubmittedAssignments.objects.get(id=submitted_id).submitted_by
                try: 
                    student = Student.objects.get(user=submitted_by)
                except Student.DoesNotExist:
                    print('student does not exist')
                    return redirect('class:view_submitted_assignment', class_name, assignment)
                number_of_total_grades = ass.points
                gr = int(points)
                try:
                    grade = Grade.objects.get(className=class_name, studentName=student)
                    number_of_total_grades = grade.number_of_total_grades + ass.points
                    gr = grade.grade + int(points)
                except Grade.DoesNotExist:
                    grade = Grade(className=class_name, studentName=student)
                    grade.save()
                Grade.objects.select_for_update().filter(className=class_name, studentName=student).update(number_of_total_grades=number_of_total_grades, grade=gr)

        assignment = Assignment.objects.filter(id=assignment)
        
        ctx = {'assignment': assignment}
        return render(request, 'class/submitted_assignments.html', ctx)
    else:
        return redirect('class:class_info', class_name)

def new_quiz(request, class_name):
    data = {}
    if request.user.groups.filter(name='Teachers').exists():
        #* to remove
        # teacher = Teacher.objects.get(user=request.user)
        # all_classes = Class.objects.filter(teacher=teacher)

        # if request.method == 'POST':
        #     for key, value in request.POST.items():
        #         print('%s' % (value) )
        
        if request.is_ajax() and request.POST.get('question') is not None:
            print('Question: ', request.POST.get('question'))
            print('quiz_id: ', request.POST.get('quiz_id'))
            quiz_id = request.POST.get('quiz_id')
            quiz = Quiz.objects.get(id=quiz_id)
            quest = Question(text=request.POST.get('question'), quiz=quiz)
            quest.save()
            list = []
            for key, value in request.POST.items():
                if 'choice' in str(key):
                    list.append(value)
            i = 0
            while i < len(list):
                ans = Answers(text=list[i:i+2][0], correct=list[i:i+2][1], question=quest)
                ans.save()
                i = i + 2
            print(list)

        if request.is_ajax() and request.POST.get('question') is None:
            title = request.POST.get('title')
            duration = request.POST.get('duration')
            to_pass = request.POST.get('to_pass')
            max_date = request.POST.get('max_date')
            max_time = request.POST.get('max_time')
            data['title'] = title
            data['duration'] = duration
            data['to_pass'] = to_pass
            data['max_date'] = max_date
            data['max_time'] = max_time
            date_time_str = max_date + ' ' + max_time + ':00'
            print(date_time_str)
            date_time = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            try:
                class_object = Class.objects.get(name=class_name)
            except Class.DoesNotExist:
                print('Class Does not exist')
                return redirect('class:index')
            quiz = Quiz(title=title, class_name=class_object, time=duration, points=to_pass, max_time_to_take=date_time)
            quiz.save()
            quiz = Quiz.objects.get(id=quiz.id)
            data['quiz_id'] = quiz.id
            print(data)
            return JsonResponse(data, safe=False)

        ctx = {'class_name': class_name}
        return render(request, 'class/new_quiz.html', ctx)
    else:
        return redirect('class:class_info', class_name)

def quiz(request, class_name, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        print('quiz Does not exist')
        return redirect('class:class_info', class_name)
    

    
    quiz_class = quiz.class_name
    student_class = False
    try:
        student = Student.objects.get(user=request.user)
        cl = student.className.all()
        for c in cl:
            if class_name in c.name:
                student_class = True
                break
    except:
        student_class = False
        pass
    if quiz_class.teacher.user == request.user or student_class:
        # print(len(quiz.get_questions()))
        if request.method == 'POST':
            answers_list = []
            correct_answers_list = []
            questions_answered_list = []
            total_ans_count = 0
            for quest in quiz.get_questions():
                total_ans_count += len(quest.answers_set.filter(correct=True))
                ans = Answers.objects.filter(question=quest, correct=True)
                for x in range(len(ans)):
                    correct_answers_list.append([ans[x].question.text, ans[x].text])
            # print(total_ans_count)
            correct_count = 0
            for key, value in request.POST.items():
                if key != 'csrfmiddlewaretoken':
                    reg = key.split('_')
                    quest_id = reg[0].strip('question')
                    choice_id = reg[1].strip('choice')
                    answers_list.append([reg[0].strip('question'),reg[1].strip('choice')])
                    answer = Answers.objects.get(id=choice_id)
                    question = Question.objects.get(id=quest_id)
                    # correct_answers_list.append([ans.question, ans.answer])
                    # print(quest_id, questions_answered_list)
                    # if answer.correct and quest_id not in questions_answered_list:
                    #     correct_answers_list.append([question.text, answer.text])
                    #     correct_count += 1
                    #     continue
                    # elif answer.correct and quest_id in questions_answered_list:
                    #     correct_count -= 1
                    #     # correct_answers_list.remove([question.text, answer.text])
                    # else: 
                    #     correct_count -= 1
                    # questions_answered_list.append(quest_id)

            # print('answers_list: ', answers_list)
            # print('----------------------------------')

            your_answers = []
            for q in answers_list:
                quest = Question.objects.get(id=q[0])
                answ = Answers.objects.get(id=q[1])
                your_answers.append([quest.text, answ.text])

            # print(your_answers)
            # print('----------------------------------')
            # print(correct_answers_list)
            # print('----------------------------------')

            score_count = 0
            for ans in your_answers:
                if ans in correct_answers_list:
                    score_count += 1
                else:
                    score_count -= 1
            print(score_count)
            
            if score_count <= 0:
                print('Your score is: ', 0)
                score = 0
            else:
                score = int((quiz.points*score_count)/total_ans_count)
                print('Your score is: ', score, '%')
            
          
            rere = Results.objects.filter(user=request.user, quiz=quiz, score=0)
            print(rere)
            Results.objects.select_for_update().filter(user=request.user, quiz=quiz, score=0).update(score=score)

            number_of_total_grades = int(quiz.points)
            gr = int(score)
            clss = Class.objects.get(name=class_name)
            try:
                try:
                    grade = Grade.objects.get(className=clss, studentName=student)
                    number_of_total_grades = grade.number_of_total_grades + int(quiz.points)
                    gr = grade.grade + int(score)
                except Grade.DoesNotExist:
                    grade = Grade(className=clss, studentName=student)
                    grade.save()
                Grade.objects.select_for_update().filter(className=clss, studentName=student).update(number_of_total_grades=number_of_total_grades, grade=gr)
            except:
                pass
      
            # print(correct_answers_list)
            # print(checks)
            # for c in checks:
            #     if c in correct_answers_list:
            #         print(c, ' correct')
            #     else:
            #         print(c, ' False'

            ctx_quiz = {'correct_answers_list': correct_answers_list, 'answers': your_answers, 'score': score}
            return render(request, 'class/quiz_score.html', ctx_quiz)
        ctx = {'quiz': quiz}
        if len(quiz.results_set.filter(user=request.user)) != 0:
            print('You already took the test')
            return redirect('class:class_info', class_name)
        res = Results(quiz=quiz, user=request.user, score=0)
        res.save()
        return render(request, 'class/quiz.html', ctx)

    else:
        print('you do not have access')
        return redirect('class:class_info', class_name)

def submitted_quizes(request, class_name):
    if request.user.groups.filter(name='Teachers').exists():
        try:
            cl = Class.objects.get(name=class_name)
        except Class.DoesNotExist:
            print('Class Does not exist')
            return redirect('class:index')
        class_quizes = Quiz.objects.filter(class_name=cl)

        if cl.teacher.user == request.user:
            pass
        else:
            print("you do not have access")
            return redirect('class:class_info', class_name)

        for quiz in class_quizes:
            print(quiz, quiz.results_set.all())

        ctx = {'class_quizes': class_quizes, 'class_name': class_name}
        return render(request, 'class/submitted_quizes.html', ctx)
    else:
        print("you do not have access")
        return redirect('class:class_info', class_name)

def view_submitted_quiz(request, class_name, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        print('quiz Does not exist')
        return redirect('class:class_info', class_name)
    
    try:
        cl = Class.objects.get(name=class_name)
    except Class.DoesNotExist:
        print('Class Does not exist')
        return redirect('class:index')
        
    if request.user.groups.filter(name='Teachers').exists():
        if cl.teacher.user == request.user:
            pass
        else:
            print("you do not have access")
            return redirect('class:class_info', class_name)

        submitted = Results.objects.filter(quiz=quiz)
        ctx = {'class_name': class_name, 'quiz': quiz, 'submitted': submitted}
        return render(request, 'class/view_submitted_quiz.html', ctx)
    else:
        print("you do not have access")
        return redirect('class:class_info', class_name)

def class_grades(request, class_name):
    try:
        cl = Class.objects.get(name=class_name)
    except Class.DoesNotExist:
        print('Class Does not exist')
        return redirect('class:index')

    #--------------------------------------------------
    # TODO add so teacher can view all students grades
    #--------------------------------------------------

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        print("You are not a student")
    
    try:
        grades = Grade.objects.get(studentName=student, className = cl)
    except Grade.DoesNotExist:
        print('Studnent has no grades yet')
        grades = ''
    class_quizes = Quiz.objects.filter(class_name=cl)
    res = []
    for quiz in class_quizes:
        try:
            res.append(Results.objects.get(user=request.user, quiz=quiz))
        except:
            pass

    assignemnts = Assignment.objects.filter(class_name=cl, noted=True)
    submitted_ass = []
    for ass in assignemnts:
        try:
            submitted_ass.append(ass.submittedassignments_set.get(submitted_by=request.user, status='graded'))
        except:
            pass
    print(submitted_ass)

    ctx ={'grades': grades, 'res': res, 'submitted_ass': submitted_ass}
    return render(request, 'class/class_grades.html', ctx)











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