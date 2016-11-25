from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from btp.models import *

import json
WEEK_MAX = 4
def is_in_past(time):
	return timezone.now() > time
def is_in_future(time):
	return timezone.now() < time

def get_current_week():
	weeks = BTPWeek.objects.all()
	for week in weeks:
		if week.startdate <= timezone.now() and week.enddate >= timezone.now():
			return week.weekno
	return False


def get_submissions_currentweek():
	submissions = BTPSubmission.objects.all()
	SubList = []
	for btps in submissions:
		if btps.week.week.weekno == get_current_week():
			SubList.append(btps)
	return SubList

def check_faculty(user):
	fac = Faculty.objects.all()
	for f in fac:
		if f.user == user:
			return True
	return False

def getFacultyIdByUser(user):
	try:
		fac = Faculty.objects.get(user=user)
		return fac.id
	except KeyError:
		return False
	return False

def getStudentIdByUser(user):
	try:
		student = BTPStudent.objects.get(user=user)
		return student.id
	except KeyError:
		return False
	return False
def getProjectGroupByStudentId(stid):
	try:	
		btpProjectGroup = BTPProjectGroup.objects.get(students__contains=[int(stid)])
		return btpProjectGroup
	except KeyError:
		return False
	return False

def getBTPEvalSetByProjectGroup(group):
	try:
		evalset = BTPEvalSet.objects.get(projectgroups__contains=[group.id])
		return evalset
	except KeyError:
		return False
	return False
def getAllBTPProjectGroupsByEvalSet(evalset):
	ProjectGroups = [] 
	pg_evalset = evalset.projectgroups
	for es in pg_evalset:
		btpgs = BTPProjectGroup.objects.get(id = es)
		ProjectGroups.append(btpgs)
	return ProjectGroups
    
def getUserTypes(user):
	USERTYPELIST = []
	facs = Faculty.objects.all()
	studs = BTPStudent.objects.all()
	evalpanels = BTPEvalPanel.objects.all() 
	for f in facs:
		if user == f.user:
			USERTYPELIST.append("FACULTY")	
			break
	for s in studs:
		if user == s.user:
			USERTYPELIST.append("STUDENT")	
			break
	for ep in evalpanels:
		fac = Faculty.objects.filter(user=user)
		if len(fac) == 1:
			facid = fac[0].id
		else:
			facid = 0
		if facid in ep.members:
			USERTYPELIST.append("EVAL")
	return USERTYPELIST

def getAllProjectGroupsFaculty(facultyid):
	btpProjectGroups = BTPProjectGroup.objects.filter(faculty__contains=[int(facultyid)])
	return btpProjectGroups

def getAllSubmissionsPG(progroup):
	subs = BTPSubmission.objects.filter(projectgroup=progroup)
	return subs

def getAllSubmissionsThisWeek(week):
	SUBS = []
	btpsetweek = BTPSetWeek.objects.filter(week=week)
	for bsw in btpsetweek:
		submissions =BTPSubmission.objects.filter(week=bsw)
		for sb in submissions:
			SUBS.append(sb) 	
	return SUBS
def getCurrentWeek():
	weeks = BTPWeek.objects.all()
	for week in weeks:
    		if week.starttime <= timezone.now() and week.endtime >= timezone.now():
				return week
		elif week.starttime >= timezone.now():
				return BTPWeek.objects.get(weekno=1)
		elif week.endtime <= timezone.now():
				return BTPWeek.objects.get(weekno= WEEK_MAX)
	return 0

def getBTPSetWeek(sets, week):
	btpsetweek =BTPSetWeek.objects.get(sets=sets, week=week)
	return btpsetweek

def getProjectGroupEvalDay(grouplist):
		GPEVALDAY = []
		week = getCurrentWeek()
		for group in grouplist:
			evalset = getBTPEvalSetByProjectGroup(group)
			SetWeek = BTPSetWeek.objects.get(sets = evalset, week=week )
			evalday = SetWeek.evalday
			group_updated = { 'group' : group, 'evalday' : evalday }
			GPEVALDAY.append(group_updated)
		
		return GPEVALDAY

def getMyGroupSubmission(pg,week):
	
	submissions = BTPSubmission.objects.filter(week=week,projectgroup=pg)
	return submissions
def getMyStudentSubmissions(pgs,week):
	SUBS = [] 
	for pg in pgs:
		subs = BTPSubmission.objects.filter( projectgroup=pg)
		if len(subs) >0:
			for x in subs:
				SUBS.append(x)
	return SUBS

def content_file_name(instance, filename):
    return '/'.join(['static/btp/files/evaluation/submissions', str(instance.projectgroup.project.code)+'_Report_'+str(instance.week.week.weekno)+"."+str(filename.split('.')[-1])])
def getContentMail(submission):
	project = submission.projectgroup.project
	week=submission.week.week
	projectsupervisor = project.supervisor
	projectstudents = submission.projectgroup.students
	sup_list = ''
	stu_list = ''
	for ps in projectsupervisor:
		f = Faculty.objects.get(id=ps).user.get_full_name()
		sup_list+=str(f)+' '
	for st in projectstudents:
		s = BTPStudent.objects.get(id=st).user.get_full_name()
		stu_list+=str(s)+ ' '
	content = 'Dear Sir,\n \t This is an auto-generated email to inform you that project group '+ str(project) + ' has submitted their report for ' + str(week)+ '.'+'\nProject Supervisor(s): '+ str(sup_list) +'\nStudents: '+str(stu_list)+'\nRegards,\n no_reply.btpc@iiits.in'
	return content
def getSubjectMail(submission):
	project = submission.projectgroup.project
	week=submission.week.week
	subject = str(project) + ' report for ' +str(week)+ ' submitted'
	return subject
def getMailingList(submission):
  	ML = []
	
  	panelmemids = submission.week.sets.panel.members
  	for memid in panelmemids:
		femail =Faculty.objects.get(id=memid).user.email
		ML.append(femail)

  	students = submission.projectgroup.students
	supervisors = submission.projectgroup.faculty
	
	for sid in students:
		semail = BTPStudent.objects.get(id=sid).user.email
		ML.append(semail)
	for supid in supervisors:
		supemail = Faculty.objects.get(id=supid).user.email
		ML.append(supemail)
	
	return ML
def checkBeforeDeadline(btpsetweek):
		return ( timezone.now() < btpsetweek.submitdeadline )	

def getStudents(project):
	try:
		btps = BTPStudent.objects.filter(btpproject=project)
	except ValueError:
		btps = []	
	try:
		hs =  HonorsStudent.objects.filter(honorsproject=project)
	except ValueError:
		hs = []
	students = ""
	for x in btps:
		students += str(x.user.username) +" "
	for x in hs:
		students += str(x.user.username) + " "
	return students.strip()

def createUG3():
	f = open("/home/user/Classified/ug3_json","r")
	f_line = f.readline()
	j = dict(json.loads(f_line))
	for k in j:
		try:
			name = str(j[k]["name"].encode('utf-8')) 
			password = str(j[k]["password"].encode('utf-8'))
			email = str(k.encode('utf-8'))
			username= str(k.encode('utf-8'))
			print "Creating user... : %s" % (name)
			user = User.objects.create_user(username=username, password=password, first_name=name, email=email)
			user.is_staff = False
			user.is_active = True
			user.groups = [Group.objects.get(name="Student2016")]
			user.save()
			print "User created for %s ..." % (name)

			s = Student.objects.create(user = user, year="2016")

			print "Student created for %s ..." % (name)
		except IntegrityError as err:
			print "User already exist, %s" % str(j[k]["name"])

def s():
	subject = "Would you suggest any changes to the email template ?"
	to = ["sahal.k13@iiits.in", "hvraman@iiits.in"]
	from_email = '[do-not-reply] Cosmos support <no-reply@cosmos.iiits.in>'
	ctx = {
        'username': 'sahal.k13@iiits.in',
        'title':'Welcome to cosmos family.',
        'password':'L4nk3w9jqnk',
        "name":"Sahal Sajjad"
    }

	message = get_template('email/signedup_welcome.html').render(Context(ctx))
	msg = EmailMessage(subject, message, to=to, from_email=from_email)
    	msg.content_subtype = 'html'
    	msg.send()
