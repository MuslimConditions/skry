import json
import datetime

from django.views.generic.base import View, TemplateView
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from django.db import transaction

from . import models
from prime.templatetags import markdown


class CategoryView(TemplateView):

    template_name = "news/list.html"
    
    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        category_slug = self.kwargs.get('category')
        all_articles = models.get_published_articles()
        if category_slug:
            category = get_object_or_404(models.Category, slug=category_slug)
            context['category'] = category
            context['articles'] = all_articles.filter(category=category)[:12]
        else:
            context['articles'] = all_articles[:12]
        return context


class ArticleView(CategoryView):
    
    template_name = "news/list.html"

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)
        year = int(self.kwargs.get('year'))
        month = int(self.kwargs.get('month'))
        day = int(self.kwargs.get('day'))
        slug = self.kwargs.get('slug')
        context['article'] = get_object_or_404(models.Article, 
                                               publish_time__year=year, 
                                               publish_time__month=month,
                                               publish_time__day=day,
                                               url_slug=slug)
        return context


class PageView(TemplateView):
    pass


class RelatedArticlesView(View):
    pass


class AjaxView(View):

    def json_response(self, **kwargs):
        return HttpResponse(json.dumps(kwargs), content_type="application/json")

    def success(self, **kwargs):
        return self.json_response(result=0, **kwargs)

    def error(self, error, message):
        return self.json_response(result=1, error=error, message=message)

    def authentication_error(self):
        return self.error("AuthenticationError", "User is not authenticated.")

    def access_error(self, message):
        return self.error("AccessError", message)

    def key_error(self, message):
        return self.error("KeyError", message)

    def does_not_exist(self, message):
        return self.error("DoesNotExist", message)

    def validation_error(self, message):
        return self.error("ValidationError", message)


class AuthenticatedAjaxView(AjaxView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(AuthenticatedAjaxView, self).dispatch(request, *args,
                         **kwargs)
        else:
            return self.authentication_error()


class ArticleJSONView(AjaxView):
    
    def get(self, request):
        article_id = request.GET.get('id')
        if article_id is None:
            return self.key_error('Required key (id) missing from request.')
        article = get_object_or_404(models.Article, pk=article_id)
        response_content = article.as_html()
        return HttpResponse(response_content, content_type="application/json")


class ArticlePositionChangeView(AuthenticatedAjaxView):

    def post(self, request):
        article_id = request.POST.get('id')
        new_position = request.POST.get('new_position')
        if not article_id:
            return self.key_error('Required key (id) missing from request.')
        if not new_position:
            return self.key_error('Required key (new_position) missing from '
                                  'request.')
        new_position = int(new_position) # unicode to int for later comparison
        try:
            article = models.Article.objects.get(pk=article_id)
        except models.Article.DoesNotExist:
            return self.does_not_exist('Article matching id %s was not found.'\
                                        % article_id)
        current_position = article.position
        # (bool) will the displaced adjacent articles be shifted higher in
        # position or lower?
        shift_higher = new_position < current_position
        if shift_higher:
            pos1 = new_position
            pos2 = current_position
            order = '-position'
        else:
            pos1 = current_position
            pos2 = new_position
            order = 'position'
        articles_to_shift = models.Article.objects\
                                  .filter(position__range=(pos1, pos2))\
                                  .exclude(position=current_position)\
                                  .order_by(order)
        print articles_to_shift, shift_higher
        highest_position = models.Article.objects.first().position
        with transaction.atomic():
            # move the article to be rearranged to a temporary holding position, 
            # freeing up its position for another article to shift into
            article.position = highest_position + 1
            article.save()
            for a in articles_to_shift:
                if shift_higher:
                    a.position += 1
                else:
                    a.position -= 1
                a.save()
            article.position = new_position
            article.save()
        return self.success(card=article.pk, new_position=article.position)
