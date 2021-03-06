import cms_app
from cms.models import CMSPlugin
from django.db import models
import multilingual
import slughifi


def get_current_language():
    from django.utils.translation import get_language
    return get_language()


class SimpleNewsCategory(models.Model):
    
    """
    
    @todo: make slugs on save
    """ 
    
    class Translation(multilingual.translation.TranslationModel):
        name = models.CharField(max_length=100)
        slug = models.SlugField(max_length=100, editable=False, blank=True)
    
    class Meta:
        verbose_name_plural = 'Simple news categories'
        
    def __unicode__(self):
        return unicode(self.name or 'Not translated #%d' % self.pk)
    

class SimpleNews(models.Model):
    
    category = models.ForeignKey(SimpleNewsCategory)
    published = models.DateTimeField()
    
    objects = multilingual.manager.MultilingualManager()
    
    class Translation(multilingual.translation.TranslationModel):
        title = models.CharField(max_length=255)
        subtitle = models.CharField(max_length=255, blank=True)
        image = models.ImageField(upload_to='simple_news')
        lead = models.TextField()
        content = models.TextField()
        slug = models.SlugField(max_length=100, editable=False, blank=True)
    
    class Meta:
        verbose_name_plural = 'Simple news'
    
    def __unicode__(self):
        return unicode(self.title or 'Not translated #%d' % self.pk)
    
    def get_absolute_url(self):
        url = '/' + cms_app.calculate_hook() + '/'
        if self.slug:
            url += self.slug + '/'
        else:        
            url += str(self.pk) + '/'
        return url
    
    def save(self, force_insert=False, force_update=False):
        if not self.slug:
            self.slug = '%04d/%02d/%02d/%s' % (
                self.published.year, 
                self.published.month, 
                self.published.day, 
                slughifi.slugify(self.title),
            ) 
        return super(SimpleNews, self).save(force_insert, force_update)

    
class SimpleNewsExcerptPlugin(CMSPlugin):
    
    categories = models.ManyToManyField('SimpleNewsCategory')
    limit = models.PositiveSmallIntegerField()
    
    def get_news_set(self):
        """Return queryset of news"""
        category_ids = [category.pk for category in self.categories.all()]
        news = SimpleNews.objects.filter(
            category__in=category_ids,
            translations__language_code=get_current_language()
        ).order_by('-published')
        return news[:self.limit]
