from datetime import datetime, time

from django.db import models


# Create your models here.
class Pass(models.Model):
	objects = models.Manager()

	# Always needed, will be approved by destination teacher if its a teacher pass, or the origin teacher if its an other pass
	approved = models.BooleanField(
		default=False)

	date = models.DateField(null=True, blank=True)
	startTimeRequested = models.TimeField(null=True, blank=True)  # always needed
	endTimeRequested = models.TimeField(null=True, blank=True)  # always needed

	timeLeftOrigin = models.TimeField(null=True, blank=True)  # always needed
	timeArrivedDestination = models.TimeField(null=True, blank=True)
	
	student = models.ForeignKey(
		'Student',
		on_delete=models.CASCADE,
		related_name="pass_student"
	)

	originTeacher = models.ForeignKey(
		'Teacher',
		on_delete=models.CASCADE,
		related_name="pass_origin_teacher"
	)

	#  The String description of the reason for the pass. This is mainly just for the destination teacher to know what the
	# student will need from them.
	description = models.CharField(max_length=960, null=True)

	def __str__(self):
		if self.description is not None:
			return self.description
		else:
			return 'None'

	#todo add for new pass type

	#### methods related to type of pass ####
	def pass_type(self):
		if self.is_location_pass():
			return 'LocationPass'
		elif self.is_srt_pass():
			return 'SRTPass'
		elif self.is_teacher_pass():
			return 'TeacherPass'

	def is_location_pass(self):
		try:
			return self.locationpass is not None
		except:
			return False

	def is_srt_pass(self):
		try:
			return self.srtpass is not None
		except:
			return False

	def is_teacher_pass(self):
		try:
			return self.teacherpass is not None
		except:
			return False

	def child(self):
		if self.is_location_pass():
			return self.locationpass
		elif self.is_srt_pass():
			return self.srtpass
		elif self.is_teacher_pass():
			return self.teacherpass


	#### information ####

	def get_destinationTeacher(self):
		if self.is_location_pass():
			return self.locationpass.get_destinationTeacher()
		elif self.is_srt_pass():
			return self.srtpass.get_destinationTeacher()
		elif self.is_teacher_pass():
			return self.teacherpass.get_destinationTeacher()

	def get_destination(self):
		if self.is_location_pass():
			return self.locationpass.location
		elif self.is_teacher_pass():
			return self.teacherpass.destinationTeacher.__str__()
		elif self.is_srt_pass():
			return self.srtpass.destinationTeacher.__str__()

	def has_left(self):
		return self.timeLeftOrigin is not None

	def has_arrived(self):
		return self.timeArrivedDestination is not None

	def is_permitted(self, user):
		return self in Pass.get_passes(user)

	#### permission checks ####

	def can_approve(self, teacher):
		if self.is_location_pass():
			return self.locationpass.can_approve(teacher)
		elif self.is_srt_pass():
			return self.srtpass.can_approve(teacher)
		elif self.is_teacher_pass():
			return self.teacherpass.can_approve(teacher)

	def can_sign_in(self, teacher):
		if self.is_location_pass():
			return self.locationpass.can_sign_in(teacher)
		elif self.is_srt_pass():
			return self.srtpass.can_sign_in(teacher)
		elif self.is_teacher_pass():
			return self.teacherpass.can_sign_in(teacher)

	def can_sign_out(self, teacher):
		if self.is_location_pass():
			return self.locationpass.can_sign_out(teacher)
		elif self.is_srt_pass():
			return self.srtpass.can_sign_out(teacher)
		elif self.is_teacher_pass():
			return self.teacherpass.can_sign_out(teacher)

	#### actions ####

	def approve(self, teacher):
		if self.is_location_pass():
			return self.locationpass.approve(teacher)
		elif self.is_srt_pass():
			return self.srtpass.approve(teacher)
		elif self.is_teacher_pass():
			return self.teacherpass.approve(teacher)

	def sign_in(self, teacher):
		if self.is_location_pass():
			return self.locationpass.sign_in(teacher)
		elif self.is_srt_pass():
			return self.srtpass.sign_in(teacher)
		elif self.is_teacher_pass():
			return self.teacherpass.sign_in(teacher)

	def sign_out(self, teacher):
		if self.is_location_pass():
			return self.locationpass.sign_out(teacher)
		elif self.is_srt_pass():
			return self.srtpass.sign_out(teacher)
		elif self.is_teacher_pass():
			return self.teacherpass.sign_out(teacher)


	#### pass lists ####

	@staticmethod
	def get_passes(user, dt=None):
		if dt is None:
			if user.profile.is_student():
				student = user.profile.student
				return Pass.get_student_passes(student)
			elif user.profile.is_teacher():
				teacher = user.profile.teacher
				return Pass.get_teacher_passes(teacher)
		else:
			if user.profile.is_student():
				student = user.profile.student
				return Pass.get_student_passes(student, dt)
			elif user.profile.is_teacher():
				teacher = user.profile.teacher
				return Pass.get_teacher_passes(teacher, dt)

	@staticmethod
	def get_student_passes(user, dt=None):
		return Pass.get_students_active_passes(user, dt) | \
			   	Pass.get_students_pending_passes(user, dt) | \
			   	Pass.get_students_old_passes(user, dt)

	@staticmethod
	def get_students_active_passes(user, dt=None):
		profile = user.profile
		if profile.is_student:
			student = profile.student
			passes = Pass.objects.filter(student=student, approved=True, timeArrivedDestination=None).exclude(srtpass__session="1") | \
						Pass.objects.filter(student=student, approved=True, srtpass__session="1", srtpass__timeArrivedOrigin=None)

			if dt is not None:
				passes = passes.filter(date=dt)

			return passes

		else:
			return None

	@staticmethod
	def get_students_pending_passes(user, dt=None):
		profile = user.profile
		if profile.is_student:
			student = profile.student
			passes = Pass.objects.filter(student=student, approved=False)

			if dt is not None:
				passes = passes.filter(date=dt)

			return passes

		else:
			return None

	@staticmethod
	def get_students_old_passes(user, dt=None):
		profile = user.profile
		if profile.is_student:
			student = profile.student
			passes = Pass.objects.filter(student=student, approved=True).exlude(timeArrivedDestination=None).exclude(srtpass__session="1") | \
					 Pass.objects.filter(student=student, approved=True, srtpass__session="1").exclude(srtpass__timeArrivedOrigin=None)

			if dt is not None:
				passes = passes.filter(date=dt)

			return passes

		else:
			return None

	@staticmethod
	def get_teacher_passes(user, dt=None):
		return Pass.get_teachers_unapproved_passes(user, dt) | \
				Pass.get_teachers_old_passes(user, dt) | \
			   	Pass.get_teachers_incoming_student_passes(user, dt) | \
			   	Pass.get_teachers_outgoing_student_passes(user, dt)

	@staticmethod
	def get_teachers_unapproved_passes(user, dt=None):
		profile = user.profile
		if profile.is_teacher:
			teacher = user.profile.teacher
			passes = Pass.objects.filter(approved=False, originTeacher=teacher) | \
						Pass.objects.filter(approved=False, destinationpass__destinationTeacher=teacher) | \
						Pass.objects.filter(approved=False, srtpass__destinationTeacher=teacher)

			if dt is not None:
				passes = passes.filter(date=dt)

			return passes

		else:
			return None

	@staticmethod
	def get_teachers_old_passes(user, dt=None):
		profile = user.profile
		if profile.is_teacher:
			teacher = profile.teacher
			passes = Pass.objects.filter(approved=True, originTeacher=teacher) | \
						 Pass.objects.filter(approved=True, destinationpass__destinationTeacher=teacher) | \
						 Pass.objects.filter(approved=True, srtpass__destinationTeacher=teacher)

			passes = passes.exclude(timeArrivedDestination=None).exclude(srtpass__session="1") | \
					 passes.exclude(timeArrivedOrigin=None)

			if dt is not None:
				passes = passes.filter(date=dt)

			return passes

		else:
			return None

	@staticmethod
	def get_teachers_incoming_student_passes(user, dt=None):
		profile = user.profile
		if profile.is_teacher:
			teacher = profile.teacher
			passes = Pass.objects.filter(approved=True, timeArrivedDestination=None, teacherpass__destinationTeacher=teacher) | \
						Pass.objects.filter(approved=True, timeArrivedDestination=None, srtpass__destinationTeacher=teacher).exclude(srtpass__session="1") | \
						Pass.objects.filter(approved=True, srtpass__timeArrivedOrigin=None, srtpass__destinationTeacher=teacher, srtpass__session="1")

			if dt is not None:
				passes = passes.filter(date=dt)

			return passes

		else:
			return None

	@staticmethod
	def get_teachers_outgoing_student_passes(user, dt=None):
		profile = user.profile
		if profile.is_teacher:
			teacher = profile.teacher
			passes = Pass.objects.filter(approved=True, timeArrivedDestination=None, originTeacher=teacher).exclude(srtpass__session="1") | \
					 Pass.objects.filter(approved=True, srtpass__timeArrivedOrigin=None, originTeache=teacher, srtpass__session="1")

			if dt is not None:
				passes = passes.filter(date=dt)

			return passes

		else:
			return None

	@staticmethod
	def get_locations_old_passes(user, dt=None):
		profile = user.profile
		if profile.is_location:
			location = profile.location
			passes = Pass.objects.filter(approved=True, specialsrtpass__destinationTeacher=location).exclude(teacherArrivedDestination=None)

			if dt is None:
				return passes
			else:
				return passes.filter(date=dt)
		else:
			return None

	@staticmethod
	def get_locations_incoming_student_passes(user, dt=None):
		profile = user.profile
		if profile.is_location:
			location = profile.location
			if dt is None:
				return Pass.objects.filter(approved=True, timeArrivedDestination=None,
				                           specialsrtpass__destinationTeacher=location)
			else:
				return Pass.objects.filter(approved=True, timeArrivedDestination=None,
				                           specialsrtpass__destinationTeacher=location, date=dt)
		else:
			return None




class LocationPass(Pass):
	objects = models.Manager()
	location = models.CharField(max_length=12, null=True, blank=True)

	#### information ####

	def parent(self):
		return Pass.objects.get(locationpass=self)

	def get_destinationTeacher(self):
		return self.originTeacher

	#### actions ####

	def approve(self, teacher):
		if self.can_approve(teacher):
			self.approved = True;
			self.save()

	def sign_in(self, teacher):
		if self.can_sign_in(teacher):
			self.timeArrivedDestination = datetime.now()
			self.save()

	def sign_out(self, teacher):
		if self.can_sign_out(teacher):
			self.timeLeftOrigin = datetime.now()
			self.save()

	#### permissions ####

	def can_approve(self, teacher):
		return teacher == self.originTeacher

	def can_sign_in(self, teacher):
		return teacher == self.originTeacher

	def can_sign_out(self, teacher):
		return teacher == self.originTeacher


class SRTPass(Pass):
	objects = models.Manager()

	destinationTeacher = models.ForeignKey(
		'Teacher',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name="destinationTeacherSRT"
	)

	# Options: "1" is session one, "2" is session two, and "3" is both sessions

	session = models.CharField(max_length=1, null=True, blank=True)

	# If session is "1", the origin teacher will need to fill this in for when they get back
	# Else, this will be null
	timeLeftDestination = models.TimeField(null=True, blank=True)

	timeArrivedOrigin = models.TimeField(null=True, blank=True)

	@staticmethod
	def create(date, student, originTeacher, description, destinationTeacher, session):
		if session == '1':
			startTimeRequested = time(hour=9, minute=50)
			endTimeRequested = time(hour=10, minute=20)
		elif session == '2':
			startTimeRequested = time(hour=10, minute=20)
			endTimeRequested = time(hour=11, minute=00)
		elif session == '3':
			startTimeRequested = time(hour=9, minute=50)
			endTimeRequested = time(hour=11, minute=00)

		return SRTPass(date=date,
		               student=student,
		               originTeacher=originTeacher,
		               description=description,
		               destinationTeacher=destinationTeacher,
		               session=session,
		               approved=True,
		               startTimeRequested=startTimeRequested,
		               endTimeRequested=endTimeRequested)

	#### information ####

	def sessionStr(self):
		if self.session == '1':
			return "Session 1"
		elif self.session == '2':
			return "Session 2"
		elif self.session == '3':
			return "Both sessions"

	def parent(self):
		return Pass.objects.get(srtpass=self)


	def get_destinationTeacher(self):
		return self.destinationTeacher

	#### actions ####


	def approve(self, teacher):
		if self.can_approve(teacher):
			self.approved = True;
			self.save()

	def sign_in(self, teacher):
		if self.can_sign_in(teacher):
			if self.originTeacher == teacher:
				self.timeArrivedOrigin = datetime.now()
			else:
				self.timeArrivedDestination = datetime

			self.save()

	def sign_out(self, teacher):
		if self.can_sign_out(teacher):
			if self.originTeacher == teacher:
				self.timeLeftOrigin = datetime.now()
			else:
				self.timeLeftDestination = datetime

			self.save()

	#### permissions ####

	def can_approve(self, teacher):
		return teacher == self.originTeacher or teacher == self.destinationTeacher

	def can_sign_in(self, teacher):
		return teacher == self.destinationTeacher or (self.session == "1" and teacher == self.originTeacher)

	def can_sign_out(self, teacher):
		return teacher == self.originTeacher or (self.session == "1" and teacher == self.destinationTeacher)


class TeacherPass(Pass):
	objects = models.Manager()
	destinationTeacher = models.ForeignKey(
		'Teacher',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name="destinationTeacher"
	)

	#### information ####

	def parent(self):
		return Pass.objects.get(teacherpass=self)

	def get_destinationTeacher(self):
		return self.destinationTeacher

	#### actions ####

	def approve(self, teacher):
		if self.can_approve(teacher):
			self.approved = True;
			self.save()

	def sign_in(self, teacher):
		if self.can_sign_in(teacher):
			self.timeArrivedDestination = datetime
			self.save()

	def sign_out(self, teacher):
		if self.can_sign_out(teacher):
			self.timeLeftOrigin = datetime.now()
			self.save()

	#### permissions ####

	def can_approve(self, teacher):
		return teacher == self.originTeacher or teacher == self.destinationTeacher

	def can_sign_in(self, teacher):
		return teacher == self.destinationTeacher

	def can_sign_out(self, teacher):
		return teacher == self.originTeacher


class SpecialSRTPass(Pass):
	objects = models.Manager()
	destinationTeacher = models.ForeignKey(
		'Location',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name="destinationTeacher"
	)
	initiatingTeacher = models.ForeignKey(
		'Teacher',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name="initiatingTeacher"
	)
	# Options: "1" is session one, "2" is session two, and "3" is both sessions

	session = models.CharField(max_length=1, null=True, blank=True)

	# If session is "1", the origin teacher will need to fill this in for when they get back
	# Else, this will be null
	timeLeftDestination = models.TimeField(null=True, blank=True)

	timeArrivedOrigin = models.TimeField(null=True, blank=True)

	@staticmethod
	def create(date, student, srtTeacher, description, destination, session, initiatingTeacher):
		if session == '1':
			startTimeRequested = time(hour=9, minute=50)
			endTimeRequested = time(hour=10, minute=20)
		elif session == '2':
			startTimeRequested = time(hour=10, minute=20)
			endTimeRequested = time(hour=11, minute=00)
		elif session == '3':
			startTimeRequested = time(hour=9, minute=50)
			endTimeRequested = time(hour=11, minute=00)

		return SpecialSRTPass(date=date,
		               student=student,
		               originTeacher=srtTeacher,
		               description=description,
		               destinationTeacher=destination,
		               session=session,
		               approved=True,
		               startTimeRequested=startTimeRequested,
		               endTimeRequested=endTimeRequested,
					   initiatingTeacher=initiatingTeacher)


class Location(models.Model):
	profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)

	def __str__(self):
		return self.profile.user.get_full_name()


class Administrator(models.Model):
	profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)


class Student(models.Model):
	profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)

	teachers = models.ManyToManyField('Teacher', related_name="teacher_list")

	defaultOrgin = models.ForeignKey(
		'Teacher',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name="srt_teacher"
	)

	def __str__(self):
		return self.profile.user.get_full_name()

	def get_deforgin(self):
		return self.defaultOrgin


class Teacher(models.Model):
	profile = models.OneToOneField('accounts.Profile', on_delete=models.CASCADE)
	name = models.CharField(max_length=250, default='stuff')

	def __str__(self):
		return self.profile.user.get_full_name()

	def get_students(self):
		pass
