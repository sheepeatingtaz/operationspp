from django import forms

from spy.models import TrailStep


class AnswerForm(forms.ModelForm):
    class Meta:
        model = TrailStep
        fields = ['answer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].label = ""
        self.fields['answer'].widget.attrs['placeholder'] = "Answer"
        self.fields['answer'].widget.attrs['autocomplete'] = 'off'
