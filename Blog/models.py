from django.db import models
from datetime import datetime
from django.urls import reverse
from User.models import Profile
from titlecase import titlecase
from django.utils.text import slugify
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from mptt.models import MPTTModel, TreeForeignKey


# article model
class Article(models.Model):
	thumbnail = models.ImageField(upload_to="thumbnails", blank=True)
	attribution = models.CharField(max_length=100, blank=True)
	date = models.DateTimeField(default=datetime.now, blank=True)
	libraries = models.ManyToManyField(Profile, related_name="library", blank=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	content = models.TextField()
	slug = models.SlugField()
	tags = TaggableManager()
	featured = models.BooleanField(default=False)

	# show self as title when queried
	def __str__(self):
		return self.title

	# when saving article
	def save(self): 
		# capitalize title 
		self.title = titlecase(self.title)
		# create slug
		self.slug = slugify(self.title)
		# save 
		super().save() 
	
	# get this article's absolute url
	def get_absolute_url(self):
		return reverse('article-detail', kwargs={"pk": self.pk, "slug": self.slug})


# comment model
class Comment(MPTTModel):
	content = models.TextField()
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateTimeField(default=datetime.now, blank=True)
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

	# order comments by new
	class MPTTMeta:
		order_insertion_by = ["-date"]


# announcement model
class Announcement(models.Model):
	date = models.DateTimeField(default=datetime.now, blank=True)
	content = models.TextField()