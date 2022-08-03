from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from users.forms import add_course_form, add_content_form, QuizForm, QuestionForm
from users.models import Section, register_table, add_course, cart, Order, Content, Quiz, Question, Result, add_shedule
from django.db.models import Q
from datetime import datetime
from django.core.mail import EmailMessage
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.template import RequestContext
import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from operator import itemgetter
import json
import time
from plyer import notification

def home(request):
	
	context = {}
	

	all_courses = add_course.objects.all()
	context["courses"] = all_courses
	top = [1,2,3,4]
	context["top"] = top
	if "user_id" in request.COOKIES:
		uid = request.COOKIES["user_id"]
		usr = get_object_or_404(User,id=uid)
		login(request,usr)
		if usr.is_active:
			return HttpResponseRedirect("/profile")
	if request.method == "POST":
		pass
	#em = EmailMessage("Greetings","Hello everyone", to=["email@gmail.com"])
	#em.send()
		#un = request.POST["username"]
		#em = request.POST["email_address"]
		#pw = request.POST["password"]
		#print("username=" + un,em,pw)

		#data = Reg(username=un,email_address=em,password=pw)
		#data.save()
		#return render(request, "users/section.html")
		#if data.is_valid():
		#	data.save()
		#	return render(request, "users/section.html")
	#	if data.is_valid():
	#		data.save()
	#		res = "thank you {}".format(un)
	#	    return render(request,"users/section.html",{"status":res})
	#	    return HttpResponse("<h1 style='color:green;'>Dear {} Data Saved Successfully!</h1>".format(un))
	#	username = request.POST.get('username')
	#	email_address = request.POST.get('email_address')
	#	form = RegForm(username=username,email_address=email_address)
	#	form = RegForm(request.POST)
	#	if form.is_valid():
	#		form.save()
	#		return redirect('home')
		#form = RegForm(request.POST)
	    #if form.is_valid():
	    #    form.save()
		#    return redirect('home')
	#	models.form.objects.create(
	#	username = request.POST.get['username'],
	#	email_address = request.POST.get['email_address']
	#	)
	#	print(username)

	#	return redirect('home')
	#	form = RegForm(request.POST)
	#	if form.is_valid():
	#		form.save()
	#		email = form.cleaned_data.get('email_address')
	#		messages.success(request, f'Hi {email}, account created')
	#		return redirect('home')
	
	#else:
	#	form = RegForm()
	#data = register_table.objects.get(user__id=request.user.id)	
	return render(request, 'users/home.html',context)


def register(request):
	if request.method == "POST":
	    form = UserRegisterForm(request.POST)
	    #con = request.POST["contact"]
	    #print(con)
	    if form.is_valid():
	    	user = form.save()
	    	user.refresh_from_db()
	    	user.register_table.contact_number = form.cleaned_data.get('contact_number')
	    	user.save()
	    	#usr = User.objects.create_user()
	    	#last_name = form.cleaned_data.get('last_name')
	    	#reg = register_table(user=usr, contact_number=con)
	    	#reg.save()
	    	username = form.cleaned_data.get('username')
	    	messages.success(request, f'Hi {username}, your account was created successfully')
	    	return redirect('home')
	else:
	    form = UserRegisterForm()
	return render(request, 'users/register.html', {'form':form})


def user_login(request):
	if request.method=="POST":
		un = request.POST["username"]
		pwd = request.POST["password"]
		print(un,pwd)
		user = authenticate(username=un,password=pwd)
		
		if user:
			login(request,user)
			if user.is_superuser:
				return HttpResponseRedirect("/admin")
			#if user.is_staff:
			#	return HttpResponseRedirect("/tutor_profile")
			#if user.is_active:
			else:
				res = HttpResponseRedirect("/")
				if "rememberme" in request.POST:
					res.set_cookie("user_id",user.id)
					res.set_cookie("date_login",datetime.now())
				return res

		else:
			return render(request,'users/login.html')
	return render(request,'users/login.html')

@login_required
def user_logout(request):
	logout(request)
	res = HttpResponseRedirect("/")
	res.delete_cookie("user_id")
	res.delete_cookie("date_login")
	return res


#@staff_member_required
#def tut_profile(request):
#	return HttpResponse("<h1>hi tutor</h1>")

@login_required()
def profile(request):

	#if User.is_superuser:
	#	return HttpResponseRedirect("/admin")
	#elif User.is_staff:
	#	return HttpResponse("<h1>Welcome tutor</h1>")
	context = {}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	return render(request, 'users/profile.html',context)
	#return HttpResponse("called")

@login_required()
def tut_profile(request):
	return render(request, 'users/tut_profile.html')

def edit_profile(request):
	context = {}
	try:
		data = register_table.objects.get(user__id=request.user.id)
	except register_table.DoesNotExist:
		data = None
	context["data"]=data
	if request.method=="POST":
		fn = request.POST["fname"]
		ln = request.POST["lname"]
		em = request.POST["email"]
		con = request.POST["contact"]
		occ = request.POST["occ"]
		abt = request.POST["about"]

		usr = User.objects.get(id=request.user.id)
		usr.first_name = fn
		usr.last_name = ln
		usr.email = em
		usr.save()

		data.contact_number = con
		data.occupation = occ
		data.about = abt
		data.save()

		if "image" in request.FILES:
			img = request.FILES["image"]
			data.profile_pic = img
			data.save()

		context["status"] = "Changes Saved Successfully"
	return render(request,"users/edit_profile.html",context)

def all_sections(request):
	context = {}
	all_courses = add_course.objects.all()
	context["courses"] = all_courses
	secs = Section.objects.all()
	context["section"] = secs
	top = [1,2,3,4]
	context["top"] = top
	return render(request, 'users/section.html',context)

def course(request):
	return render(request, 'users/coursepage.html')

def change_password(request):
	context={}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	if request.method=="POST":
		current = request.POST["cpwd"]
		new_pas = request.POST["npwd"]

		user = User.objects.get(id=request.user.id)
		un = user.username
		check = user.check_password(current)
		if check==True:
			user.set_password(new_pas)
			user.save()
			context["msz"] = "Password Changed Successfully!"
			context["col"] = "alert-success"
			user = User.objects.get(username=un)
			login(request,user)
		else:
			context["msz"] = "Incorrect Current Password"
			context["col"] = "alert-danger"
	return render(request,"users/change_password.html",context)

def add_course_view(request):
	context={}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	form = add_course_form()
	if request.method == "POST":
		form = add_course_form(request.POST,request.FILES)
		if form.is_valid():
			data = form.save(commit=False)
			login_user = User.objects.get(username=request.user.username)
			data.tutor = login_user
			data.save()
			context["status"] = "{} added successfully".format(data.course_name)
	context["form"] = form
	return render(request,"users/add_course.html",context)

def my_courses(request):
	context = {}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	all = add_course.objects.filter(tutor__id=request.user.id)
	context["courses"] = all
	return render(request,"users/my_courses.html",context)

def single_course(request):
	context = {}
	id = request.GET["pid"]
	obj = add_course.objects.get(id=id)
	context["course"] = obj

	check = register_table.objects.filter(user__id=obj.tutor.id)
	if len(check)>0:
		prf = get_object_or_404(register_table, user__id=obj.tutor.id)
		context["profile_pic"] = prf.profile_pic
		context["contact"] = prf.contact_number


	cont = Content.objects.filter(course__id=id).order_by("module_no","chapter_no")
	conten = Content.objects.filter(course__id=id).order_by("chapter_no")
	mod = Content.objects.filter(course__id=id).order_by("module_no").values("module_no").distinct()
	#mod2 = Content.objects.filter(course__id=id).values("module_no").annotate(dcount=Count("module_no")).order_by("module_no")
	#print(mod2)
	cont1 = Content.objects.filter(Q(course__id=id)&Q(module_no=1)).order_by("chapter_no")
	context["content"] = cont
	context["modules"] = cont1
	mods = len(mod)
	context["some"] = mod
	return render(request,"users/single_course.html",context)

def update_course(request):
	context = {}
	secs = Section.objects.all().order_by("sec_name")
	context["section"] = secs

	pid = request.GET["pid"]
	course = get_object_or_404(add_course,id=pid)
	context["course"] = course

	if request.method=="POST":
		pn = request.POST["pname"]
		ct_id = request.POST["pcat"]
		pr = request.POST["pp"]
		sp = request.POST["sp"]
		des = request.POST["des"]

		sec_obj = Section.objects.get(id=ct_id)

		course.course_name =pn
		course.course_section =sec_obj
		course.course_price =pr
		course.sale_price =sp
		course.details =des
		if "pimg" in request.FILES:
			img = request.FILES["pimg"]
			course.course_image = img
		course.save()
		context["status"] = "Changes saved successfully"
		context["id"] = pid

	return render(request,"users/update_course.html",context)

def delete_course(request):
	context={}
	if "pid" in request.GET:
		pid = request.GET["pid"]
		prd = get_object_or_404(add_course, id=pid)
		context["course"] = prd

		if "action" in request.GET:
			prd.delete()
			context["status"] = str(prd.course_name)+" deleted successfully"
	return render(request,"users/delete_course.html",context)


def all_courses(request):
	context = {}
	all_courses = add_course.objects.all().order_by("course_name")
	context["courses"] = all_courses

	if "qry" in request.GET:
		q = request.GET["qry"]
		#p = request.GET["price"]
		prd = add_course.objects.filter(Q(course_name__contains=q)|Q(course_section__sec_name__contains=q))
		#prd = add_course.objects.filter(Q(course_name__icontains=q)&Q(sale_price__lt=p))
		context["courses"] = prd
		context["abcd"] = "search"

	if "sec" in request.GET:
		cid = request.GET["sec"]
		prd = add_course.objects.filter(course_section__id=cid)
		context["courses"] = prd
		context["abcd"] = "search"

	return render(request,"users/all_courses.html",context)

def add_to_cart(request):
	context={}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	items = cart.objects.filter(user__id=request.user.id,status=False)
	context["items"] = items
	if request.user.is_authenticated:
		if request.method=="POST":
			pid = request.POST["pid"]
			is_exist = cart.objects.filter(course__id=pid,user__id=request.user.id,status=False)
			if len(is_exist)>0:
				context["msz"] = "Item already exists in your cart"
				context["cls"] = "alert alert-warning"
			else:
				course = get_object_or_404(add_course,id=pid)
				usr = get_object_or_404(User,id=request.user.id)
				c = cart(user=usr,course=course)
				c.save()
				context["msz"] = "{} added in your cart".format(course.course_name)
				context["cls"] = "alert alert-success"


	else:
		context["status"] = "Please Login to view your cart"
	return render(request,"users/cart.html",context)

def get_cart_data(request):
	items = cart.objects.filter(user__id=request.user.id, status=False)
	sale,total=0,0
	for i in items:
		sale += float(i.course.sale_price)
		total += float(i.course.course_price)

	res = {
	     "total":total, "offer":sale,
	}
	return JsonResponse(res)

def del_cart(request):
	if "delete_cart" in request.GET:
		id = request.GET["delete_cart"]
		cart_obj = get_object_or_404(cart,id=id)
		cart_obj.delete()
		return HttpResponse(1)


def process_payment(request):
	items = cart.objects.filter(user_id__id=request.user.id,status=False)
	courses =""
	amt=0
	inv = "INV-"
	cart_ids = ""
	p_ids = ""
	for j in items:
		courses += str(j.course.course_name)+"\n"
		p_ids += str(j.course.id)+","
		amt += float(j.course.sale_price)
		inv += str(j.id)
		cart_ids += str(j.id)+","
	paypal_dict = {
	'business': settings.PAYPAL_RECEIVER_EMAIL,
	'amount': str(amt),
	'item_name': courses,
	'invoice': inv,
	'notify_url': 'http://{}{}'.format("127.0.0.1:8000", reverse('paypal-ipn')),
	'return_url': 'http://{}{}'.format("127.0.0.1:8000",reverse('payment_done')),
	'cancel_return': 'http://{}{}'.format("127.0.0.1:8000",reverse('payment_cancelled')),

	}
	usr = User.objects.get(username=request.user.username)
	ordr = Order(cust_id=usr,cart_ids=cart_ids,course_ids=p_ids)
	ordr.save()
	ordr.invoice_id = str(ordr.id)+inv
	ordr.save()
	request.session["order_id"] = ordr.id

	form = PayPalPaymentsForm(initial=paypal_dict)
	return render(request, 'users/process_payment.html', {'form': form})

def payment_done(request):
	if "order_id" in request.session:
		order_id = request.session["order_id"]
		ord_obj = get_object_or_404(Order,id=order_id)
		ord_obj.status = True
		ord_obj.save()

		for i in ord_obj.cart_ids.split(",")[:-1]:
			#print(i)
			cart_object = cart.objects.get(id=i)
			cart_object.status = True
			cart_object.save()
	return render(request,"users/payment_success.html")

def payment_cancelled(request):
	return render(request,"users/payment_failed.html")

def order_history(request):
	context = {}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data

	all_orders = []
	orders = Order.objects.filter(cust_id__id=request.user.id).order_by("-id")
	#for i in orders:
	#	print(i.cart_ids)
	for order in orders:
		courses = []
		for id in order.course_ids.split(",")[:-1]:
			crs = get_object_or_404(add_course, id=id)
			courses.append(crs)
		ordr = {
		"order_id":order.id,
		"courses":courses,
		"invoice":order.invoice_id,
		"status":order.status,
		"date":order.processed_on,
		}
		all_orders.append(ordr)
	context["order_history"] = all_orders

	return render(request,"users/order_history.html",context)


def my_learners(request):
	context = {}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data

	courses = cart.objects.filter(course__tutor__id=request.user.id, status=True)
	learn = []
	ids = []
	for i in courses:
		us = {
		"username": i.user.username,
		"first_name": i.user.first_name,
		"last_name": i.user.last_name,
		"email": i.user.email,
		"join" : i.user.date_joined,
		}
		check = register_table.objects.filter(user__id=i.user.id)
		if len(check)>0:
			prf = get_object_or_404(register_table, user__id=i.user.id)
			us["profile_pic"] = prf.profile_pic
			us["contact"] = prf.contact_number
		#learn.append(us)
		ids.append(i.user.id)
		count = ids.count(i.user.id)
		if count<2:
			learn.append(us)

	context["learners"] = learn


	return render(request,"users/my_learners.html",context)

def add_content_view(request):
	context={}
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	id = request.GET["pid"]
	obj = add_course.objects.get(id=id)
	context["course"] = obj
	print(obj)
	form = add_content_form()
	if request.method == "POST":
		form = add_content_form(request.POST,request.FILES)
		if form.is_valid():
			data = form.save(commit=False)
			login_user = User.objects.get(username=request.user.username)
			data.tutor = login_user
			data.course = obj
			data.save()
			context["status"] = "added successfully"
	context["form"] = form
	return render(request,"users/add_content.html",context)


def content_view(request):
	context = {}
	id = request.GET["pid"]
	obj = add_course.objects.get(id=id)
	context["course"] = obj
	quizzes = Quiz.objects.filter(course__id=id)
	context["quizzes"]= quizzes
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	form = add_content_form()
	if request.method == "POST":
		form = add_content_form(request.POST,request.FILES)
		if form.is_valid():
			data = form.save(commit=False)
			login_user = User.objects.get(username=request.user.username)
			data.tutor = login_user
			data.course = obj
			data.save()
			context["status"] = "added successfully"
	context["form"] = form

	quizForm = QuizForm()
	if request.method =="POST":
		quizForm = QuizForm(request.POST,request.FILES)
		if quizForm.is_valid():
			data1 = quizForm.save(commit=False)
			data1.course = obj
			data1.save()
			context["status"] = "added successfully"
			#quizForm.save()
		else:
			print("form is invalid")
		#url = reverse('content/', kwargs={ 'pid': id })
		#return HttpResponseRedirect(url)
		context["quizForm"] = quizForm
	
	cont = Content.objects.filter(course__id=id).order_by("module_no","chapter_no")
	conten = Content.objects.filter(course__id=id).order_by("chapter_no")
	mod = Content.objects.filter(course__id=id).order_by("module_no").values("module_no").distinct()
	#mod2 = Content.objects.filter(course__id=id).values("module_no").annotate(dcount=Count("module_no")).order_by("module_no")
	#print(mod2)
	cont1 = Content.objects.filter(Q(course__id=id)&Q(module_no=1)).order_by("chapter_no")
	context["content"] = cont
	context["modules"] = cont1
	mods = len(mod)
	context["some"] = mod
	for co in cont:
		print(co.module_no)
		print(co.tutor.id)
		#tut = int(co.tutor.id)
	obj2 = add_course.objects.filter(id=id)
	for cors in obj2:
		print(cors.tutor.id)
		tut = cors.tutor.id
	context["tut"] = tut
	return render(request,"users/content.html",context)


def del_content(request):
	if "delete_content" in request.GET:
		id = request.GET["delete_content"]
		cont_obj = get_object_or_404(Content,id=id)
		cont_obj.delete()
		return HttpResponse(1)

def workshops(request):
	return render(request, 'users/workshop.html')

def about(request):
	return render(request, 'users/about.html')

def add_quiz(request):
	context = {}
	quizForm=QuizForm()
	id = request.GET["pid"]
	obj = add_course.objects.get(id=id)
	context["course"] = obj
	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data
	if request.method=='POST':
		quizForm=QuizForm(request.POST)
		if quizForm.is_valid():
			data = quizForm.save(commit=False)
			data.course = obj
			data.save()
			context["status"] = "added successfully"
			#quizForm.save()
		else:
			print("form is invalid")
		#url = reverse('content/', kwargs={ 'pid': id })
		#return HttpResponseRedirect(url)
		context["quizForm"] = quizForm
	return render(request,'users/add_quiz.html',{'quizForm':quizForm})

def add_question(request):
	context={}
	if "pid" in request.GET:
		pid = request.GET["pid"]
		obj = add_course.objects.get(id=pid)
	if "qid" in request.GET:
		qid = request.GET["qid"]
		obj2 = Quiz.objects.get(id=qid)
	questions = Question.objects.all().filter(quiz__id=qid)
	context["questions"]= questions
	context["course"] = obj
	context["quiz"] = obj2
	questionForm = QuestionForm()
	if request.method=="POST":
		questionForm = QuestionForm(request.POST)
		if questionForm.is_valid():
			question = questionForm.save(commit=False)
			#quiz = Quiz.objects.get(id=request.POST.get('quizID'))
			question.quiz = obj2
			question.course = obj
			question.save()
			context["status"] = "added successfully"
		else:
			print("form is invalid")
	context["questionForm"] = questionForm
	return render(request,'users/add_question.html',context)

# def del_question(request):
# 	if "pid" in request.GET:
# 		id = request.GET["pid"]
# 		cont_obj = Question.objects.get(id=id)
# 		cont_obj.delete()
# 		return render(request,'users/add_question.html')

def del_question(request):
	if "delete_question" in request.GET:
		#print("yes")
		id = request.GET["delete_question"]
		cont_obj = get_object_or_404(Question,id=id)
		cont_obj.delete()
		return HttpResponse(1)

def del_quiz(request):
	if "delete_quiz" in request.GET:
		id = request.GET["delete_quiz"]
		cont_obj = get_object_or_404(Quiz,id=id)
		cont_obj.delete()
		return HttpResponse(1)

def start_quiz(request):
	csrfContext = RequestContext(request)
	context={}
	if "pid" in request.GET:
		pid = request.GET["pid"]
		obj = add_course.objects.get(id=pid)
	if "qid" in request.GET:
		qid = request.GET["qid"]
		obj2 = Quiz.objects.get(id=qid)
	questions = Question.objects.all().filter(quiz__id=qid)
	context["questions"]= questions
	context["course"] = obj
	context["quiz"] = obj2

	if request.method=='POST':
		pass
	response= render(request,'users/start_exam.html',context)
	response.set_cookie('quiz_id',obj2.id)
	return response

def calculate_marks(request):
	if request.COOKIES.get('quiz_id') is not None:
		quiz_id = request.COOKIES.get('quiz_id')
		quiz=Quiz.objects.get(id=quiz_id)
		total_marks=0
		questions=Question.objects.all().filter(quiz=quiz)
		for i in range(len(questions)):

			selected_ans = request.COOKIES.get(str(i+1))
			actual_answer = questions[i].answer
			if selected_ans == actual_answer:
				total_marks = total_marks + questions[i].marks
		learner = models.register_table.objects.get(user_id=request.user.id)
		result = Result()
		result.marks=total_marks
		result.quiz=quiz
		request.learner=learner
		result.save()
		print("marks=")
		print(total_marks)

		return HttpResponseRedirect('view-result')

def view_result_view(request):
	quizzes=Quiz.objects.all()
	return render(request,'users/view_result.html',{'quizzes':quizzes})




class KNearestNeighbours:
	def __init__(self, data, target, test_point, k):
		self.data = data
		self.target = target
		self.test_point = test_point
		self.k = k
		self.distances = list()
		self.categories = list()
		self.indices = list()
		self.counts = list()
		self.category_assigned = None

	@staticmethod
	def dist(p1, p2):
		"""Method returns the euclidean distance between two points"""
		return np.linalg.norm(np.array(p1) - np.array(p2))

	def fit(self):
		"""Method that performs the KNN classification"""
		# Create a list of (distance, index) tuples from the test point to each point in the data
		self.distances.extend([(self.dist(self.test_point, point), i) for point, i in zip(self.data, [i for i in range(len(self.data))])])
		# Sort the distances in ascending order
		sorted_li = sorted(self.distances, key=itemgetter(0))
		# Fetch the indices of the k nearest point from the data
		self.indices.extend([index for (val, index) in sorted_li[:self.k]])
		# Fetch the categories from the train data target
		for i in self.indices:
			self.categories.append(self.target[i])
		# Fetch the count for each category from the K nearest neighbours
		self.counts.extend([(i, self.categories.count(i)) for i in set(self.categories)])
		# Find the highest repeated category among the K nearest neighbours
		self.category_assigned = sorted(self.counts, key=itemgetter(1), reverse=True)[0][0]


def KNN_Movie_Recommender(test_point, k):
	course = add_course.objects.all()
	x = []
	y = []
	for item in course:
		x = [item.id,item.course_name,item.course_section,item.topics]
		y+=[x]
	courses_df = pd.DataFrame(y,columns=['courseId','course_name','course_section','topics'])
	all_topics = [courses_df.loc[j]['topics'].split(',') for j in courses_df.index]
	topics = sorted(list(set([item for sublist in all_topics for item in sublist])))
	full_data = []
	course_titles = []
	for i in courses_df.index:
		course_titles.append((courses_df.loc[i]['course_name'].strip(), i, courses_df.loc[i]['courseId']))
		course_data = [1 if topic in courses_df.loc[i]['topics'].split(',') else 0 for topic in topics]
		full_data.append(course_data)

	# Create dummy target variable for the KNN Classifier
	target = [0 for item in course_titles]
	# Instantiate object for the Classifier
	model = KNearestNeighbours(full_data, target, test_point, k=k)
	# Run the algorithm
	model.fit()
	# Print list of 10 recommendations < Change value of k for a different number >
	table = []
	for i in model.indices:
		# Returns back movie title and imdb link
		#table.append([course_titles[i][0], course_titles[i][2],full_data[i][-1]])
		table.append(course_titles[i][2])
	print(table)
	return table

def recommend(request):
	context = {}
	course = add_course.objects.all()
	x = []
	y = []
	for item in course:
		x = [item.id,item.course_name,item.course_section,item.topics]
		y+=[x]
	courses_df = pd.DataFrame(y,columns=['courseId','course_name','course_section','topics'])
	#print("couse dataframe")
	#print(courses_df)
	#print(courses_df.dtypes)
	print(courses_df.head())
	all_topics = [courses_df.loc[j]['topics'].split(',') for j in courses_df.index]
	topics = sorted(list(set([item for sublist in all_topics for item in sublist])))
	print(topics)
	context["topics"] = topics
	#print(len(topics))

	full_data = []
	course_titles = []
	for i in courses_df.index:
		course_titles.append((courses_df.loc[i]['course_name'].strip(), i, courses_df.loc[i]['courseId']))
		course_data = [1 if topic in courses_df.loc[i]['topics'].split(',') else 0 for topic in topics]
		full_data.append(course_data)
	#print(course_titles[1])
	#print(full_data[0])
	#print(course_titles)
	print(full_data)

	courses = [title[0] for title in course_titles]
	topics2test = []

	if request.method=='POST':
		chosen=request.POST.getlist('chosen')
		print(chosen)
		for t in topics:
			if t in chosen:
				topics2test.append(int(1))
			else:
				topics2test.append(0)
		print(topics2test)

		test_points = topics2test
		print("this topic")
		#print(topics)
		table = KNN_Movie_Recommender(test_points, 3)


		rec_courses = add_course.objects.filter(id__in=table)
		print(rec_courses)
		#context["courses"]= rec_courses

		rec =[]

		for j in table:
			crs = add_course.objects.filter(id = j)
			#print(crs)
			#rec = rec | crs
			rec.append(crs)
		print(rec)
		context["courses"]= rec
	#print(table)
	return render(request,"users/enter_topics.html",context)


def shedule(request):
	context = {}
	


	ch = register_table.objects.filter(user__id=request.user.id)
	if len(ch)>0:
		data = register_table.objects.get(user__id=request.user.id)
		context["data"] = data

	all_orders = []
	orders = Order.objects.filter(cust_id__id=request.user.id).order_by("-id")
	#for i in orders:
	#	print(i.cart_ids)
	for order in orders:
		courses = []
		for id in order.course_ids.split(",")[:-1]:
			crs = get_object_or_404(add_course, id=id)
			courses.append(crs)
		ordr = {
		"order_id":order.id,
		"courses":courses,
		"invoice":order.invoice_id,
		"status":order.status,
		"date":order.processed_on,
		}
		all_orders.append(ordr)
	context["order_history"] = all_orders

	if request.method=="POST":
		usr = User.objects.get(id=request.user.id)
		chosencourses=request.POST.getlist('chosencourse')
		duration = request.POST["duration"]
		reminder = request.POST["reminder"]
		print(usr)
		print(chosencourses)
		print(duration)
		print(reminder)
		thesecourse = ",".join(str(x) for x in chosencourses)
		#thesecourse = str(chosencourses)
		print(thesecourse)
		task = add_shedule(user=usr, courses=thesecourse, duration=duration, reminder=reminder)
		task.save()

	allshedules = []

	try:
		shedules = add_shedule.objects.filter(user__id=request.user.id)
		for i in shedules:
			allcrs=i.courses.split(',')
			allcrs= [int(x) for x in allcrs]
			crss = add_course.objects.filter(id__in =allcrs)
			shed={
			"id" : i.id,
			"crss" : crss,
			"dur" : i.duration,
			"start" : i.added_on
			}
			print(shed)
			allshedules.append(shed)
	except add_shedule.DoesNotExist:
		shedules = None

	context["shedules"] = allshedules
	#print(allshedules)


	return render(request,"users/add_shedule.html",context)

def progress(request):
	context = {}
	notif = 1
	if notif == 1:
		notification.notify(
			title = "Continue learning",
			message = "Reminder to complete your courses as per shedule"
			
			)
		
	id = request.GET["pid"]
	obj = add_shedule.objects.get(id=id)
	allcrs=obj.courses.split(',')
	allcrs= [int(x) for x in allcrs]
	print(allcrs)
	content = Content.objects.filter(course__id__in = allcrs)
	print(content)
	content_ids = []
	for con in content:
		content_ids.append(con.id)
	length = len(content)
	print(len(content))
	print(obj.duration)
	dur = int(obj.duration)
	num = int(length/(dur*7))
	print(num)
	lis = []
	#7*1=7/num, num=15/7=2, = 7/2=3
	weekly = []
	for r in range(dur):
		daily = []
		for s in range(7):
			topics = []
			for c in range(num):
				topics.append(content_ids[0])
				content_ids.pop(0)
			daily.append(topics)
		weekly.append(daily)
	print(weekly)
	mod = length%(dur*7)
	print(mod)
	for week in weekly:
		if len(content_ids)==0:
			break
		for day in week:
			if len(content_ids)!=0:
				day.append(content_ids[0])
				content_ids.pop(0)
			else:
				break
	print(weekly)
	context["content"] = weekly

	# for i in range(int((7*dur)/num)):
	# 	lis2 = []
	# 	for j in range(num):
	# 		lis2.append(content[i+j].id)
	# 	lis.append(lis2)
	# 	print(lis2)
	# print(i)
	# print(lis)
	# mod = length%(dur*7)
	# print(mod)
	# for k in range(mod):
	# 	if lis:
	# 		lis[k].append(content[i+k+1].id)
	# 	else :
	# 		lis.append(content[i+k+1].id)
	# print(lis)
	# context["content"] = lis
	context["duration"] = dur
	range1 = range(dur)
	context["range"] = range1

	return render(request,"users/progress.html",context)

def plan(request):
	ti = time.localtime()
	now = time.strftime("%H:%M", ti)
	print("now = ",now)
	sheds = add_shedule.objects.filter(user__id=request.user.id)
	rems = []
	for rem in sheds:
		rems.append(rem.reminder)
	print(rems)

	if now in rems:
		notification.notify(
			title = "Continue learning",
			message = "Reminder to complete your courses as per shedule")
	else :
		print("no")
	context = {}
	url = request.GET["pid"]
	print(url)
	print(type(url))
	url = json.loads(url)
	print(type(url))
	print(url)
	content = Content.objects.filter(id__in = url)
	context["content"] = content
	print(content)
	return render(request,"users/plan.html",context)