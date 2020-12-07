from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from .models import Question, Choice

import pandas as pd
import plotly.offline as opy
import plotly.graph_objs as go
import plotly.express as px


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):

        context = super(ResultsView, self).get_context_data(**kwargs)

        # df_questions = pd.DataFrame(Question.objects.all().values())

        question = self.object
        df = pd.DataFrame(question.choice_set.all().values_list(),
                          columns=[field.verbose_name
                                   for field in Choice._meta.fields])

        fig = px.bar(df, x='Choice', y='Votes')

        graph = fig.to_html(full_html=False,
                            default_height=500,
                            default_width=700)
        context['graph'] = graph

        return context


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
