# Create your views here.
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from spy.forms import AnswerForm
from spy.models import TrailStep


class StartView(TemplateView):
    template_name = 'start.html'

    def dispatch(self, request, *args, **kwargs):
        if "restart" in request.GET.keys():
            request.session.clear()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.session.get("current_clue"):
            context['re'] = "Restart"
            context['current'] = self.request.session.get("current_clue")
        return context


class ClueView(FormView):
    template_name = 'clue.html'
    form_class = AnswerForm

    clue = None

    def dispatch(self, request, *args, **kwargs):
        self.clue = get_object_or_404(TrailStep, pk=kwargs.get('clue'))
        if "restart" in request.GET.keys():
            request.session.clear()
        request.session["current_clue"] = self.clue.sequence

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for f in ['directions', 'clue', 'image', 'sequence', 'hint']:
            context[f] = getattr(self.clue, f, None)
        if context['image']:
            context['image_path'] = f"images/clue{context['sequence']}.png"
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['answer'] = self.request.session.get(f"clue_{self.clue.sequence}")
        return initial

    def form_valid(self, form):
        self.request.session[f"clue_{self.clue.sequence}"] = form.cleaned_data.get('answer').upper()
        return super().form_valid(form)

    def get_success_url(self):
        sequence = self.clue.sequence
        try:
            next = TrailStep.objects.get(sequence=sequence + 1)
            url = reverse_lazy("spy:clue", kwargs={'clue': next.sequence})
        except:
            url = reverse_lazy("spy:code")
        return url


class CodeView(TemplateView):
    template_name = 'code.html'

    class Result(object):
        def __init__(self, clue, user_answer=None, correct=None):
            self.clue = clue
            self.user_answer = user_answer
            self.correct = correct

        @property
        def colour(self):
            if self.correct:
                return "success"
            if self.correct == None:
                return "light"
            return "danger"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_results(self):
        clues = TrailStep.objects.all()
        results = []
        total_correct = 0
        for clue in clues:
            user_answer = self.request.session.get(f"clue_{clue.sequence}", "").upper()
            correct = None
            if user_answer:
                if user_answer == clue.answer.upper():
                    correct = True
                    total_correct += 1
                else:
                    correct = False
            results.append(self.Result(clue.sequence, user_answer, correct))
        return results, total_correct, clues

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results, total_correct, clues = self.get_results()
        context['results'] = results
        if any([
            total_correct == clues.count(),
            settings.DEBUG
        ]):
            context['finished'] = True
        return context


class FinishView(CodeView):
    template_name = 'finish.html'

    def dispatch(self, request, *args, **kwargs):
        results, total_correct, clues = self.get_results()
        if total_correct != clues.count():
            if not settings.DEBUG:
                return HttpResponseRedirect(reverse_lazy("spy:code"))
        return super().dispatch(request, *args, **kwargs)


class BriefView(CodeView):
    template_name = 'brief.html'
