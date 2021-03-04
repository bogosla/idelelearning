import redis
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView ,FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db import models
from .forms import CourseEnrollForm
from courses.models import Course, Quiz, ModuleAccess, Module
from courses.forms import RegisterForm

class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = RegisterForm
    success_url = reverse_lazy('student_course_list')
    

    def form_valid(self, form):
        res = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'], password=cd['password1'])
        login(self.request, user)
        return res

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None 
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.save()
        self.request.user.course_joined.add(self.course)
        # self.course.students.add(self.request.user)
        ModuleAccess.objects.create(user=self.request.user, course=self.course, mod_id=self.course.modules.first().id)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])
        
class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course 
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

def next_module(request, module, course_id, access):
    all_modules, m = modules(course_id)
    try:
        module.m_quiz
    except models.ObjectDoesNotExist:
        print('No quiz', all_modules, module.id)
        _next = all_modules[all_modules.index(module.id) + 1]
        if not access.mod_id > _next:
            access.mod_id = _next
            access.save()
    
class StudentCourseDetailView(DetailView):
    model = Course 
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get(self, *args, **kwargs):
        course = self.get_object()
        access = ModuleAccess.objects.get(user=self.request.user, course=course)

        if 'module_id' in self.kwargs:
            module = course.modules.get(Q(id=self.kwargs['module_id'])&Q(id__lte=access.mod_id))
        else:
            m = r.get(f"course#{course.pk}:{self.request.user.pk}")        

            module = course.modules.get(id=int(m.decode())) if m and int(m) <= access.mod_id else course.modules.all()[0]
            
        try:
            module.m_quiz
        except models.ObjectDoesNotExist:
            next_module(self.request, module, course.id, access)
            print("No EXISTED")
        else:
            pass

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        m_id = 0
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        access = ModuleAccess.objects.get(user=self.request.user, course=course)
        context['last_mod'] = access.mod_id
    
        context['last_module'] = access.mod_id == course.modules.last().id + 1
        print("LAST : ", context['last_mod'], context['last_module'], access.mod_id, course.modules.last().id)
        # r.delete(f"course#{course.pk}:{self.request.user.pk}")

        if 'module_id' in self.kwargs:
            context['module'] = course.modules.get(Q(id=self.kwargs['module_id'])&Q(id__lte=access.mod_id))
            m_id = r.set(f"course#{course.pk}:{self.request.user.pk}", self.kwargs['module_id'])
        else:
            m = r.get(f"course#{course.pk}:{self.request.user.pk}")
            context['module'] = course.modules.get(id=int(m.decode())) if m else course.modules.all()[0]

        return context
import random
def modules(course_id):
    modules = Course.objects.get(id=course_id).modules
    all_modules = list(modules.all().values_list('id', flat=True))
    all_modules += [all_modules[-1] + 1]
    return all_modules, modules

# class StudentCourseDetailView(DetailView):

#     model = Course 
#     template_name = 'students/course/detail.html'

#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(students__in=[self.request.user])

#     def get(self, *args, **kwargs):        
#         return super().get(*args, **kwargs)

        
       
#     def get_context_data(self, **kwargs):
#         m_id = 0
#         context = super().get_context_data(**kwargs)
#         course = self.get_object()
#         access = ModuleAccess.objects.get(user=self.request.user, course=course)

#         # new
#         all_modules, m = modules(self.get_object().id)
        
#         context['last_mod'] = access.mod_id
#         context['last_module'] = access.mod_id == course.modules.last().id + 1
#         # r.delete(f"course#{course.pk}:{self.request.user.pk}")

#         x = course.modules.filter(Q(id__lte=access.mod_id))
#         paginator = Paginator(x, 1)

#         try:
#             module = paginator.page(self.request.GET.get('chapter', 0))
#             r.set(f"course#{course.pk}:{self.request.user.pk}", self.request.GET.get('chapter', 1))
#         except PageNotAnInteger:
#             module = paginator.page(paginator.num_pages)
#         except EmptyPage:
#             last_page = r.get(f"course#{course.pk}:{self.request.user.pk}")

#             module = paginator.page(last_page if last_page else 1)

#         context['module'] = module[0]
       
#         context['page'] = module
    
#         return context

def quiz(request, quiz_id, course_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz_questions = list(quiz.questions.all())
    score = 0
    last = False
    total_score = ((quiz.questions.count() * quiz.score_for_each) * quiz.pourcent) // 100
    all_modules, m = modules(course_id)
    
    if request.method == 'POST':
        data = request.POST
        for x in quiz_questions:
            if data.get(str(x.id)) == str(quiz.questions.get(id=x.id).response):
                score += quiz.score_for_each

        if (score >= total_score and request.user not in quiz.passes.all()):
            print("PASSES COURSE WITH: ", score)
            quiz.passes.add(request.user)
            module = request.user.access.get(course__id=course_id)

            # Eseye gad si gen lot module, si ajoute denye id module sa...
            try:
                next_module_id = all_modules[all_modules.index(module.mod_id) + 1] 
                module.mod_id = next_module_id
                module.save()
                print("INDEX :", next_module_id)
            except:
                pass 

            # print("Module : ", module.mod_id)
            # module.mod_id = module.mod_id + 1
            m_id = module.mod_id
            f_mod = quiz.course.modules.first().id

            last_module_id = quiz.course.modules.last().id
            if m_id == last_module_id :
                m_id = last_module_id
                last = True
            print(last)
            return redirect(request.GET.get('rnext'))
            return render(request,'students/course/quiz.html', {'quiz': quiz_questions, 'q': quiz,
                    'course_id': quiz.course.id, "module_id":m_id, "score": score, "last": last, 'f_id': f_mod})

    # Afiche questions quiz.
    random.shuffle(quiz_questions)
    return render(request,'students/course/quiz.html', {'quiz': quiz_questions, 'q': quiz})



def pass_module(request, module_id, course_id):
    all_modules, m = modules(course_id)
    print(m.get(id=module_id))
    try:
        m.get(id=module_id).m_quiz
    except models.ObjectDoesNotExist:
        print('No quiz', all_modules, module_id)
        _next = all_modules[all_modules.index(module_id) + 1]
        module = request.user.access.get(course_id=course_id)
        module.mod_id = _next
        module.save()
        return redirect(request.GET['next'])
    return HttpResponse('KOKO')

