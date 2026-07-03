"""Forms for verified-purchase product reviews."""

from django import forms
from django.utils.translation import gettext_lazy as _

from reviews.models import Review


class ReviewForm(forms.ModelForm):
    """Collect a rating and a non-empty review comment."""

    rating = forms.TypedChoiceField(
        label=_("Оцінка"),
        choices=tuple((value, str(value)) for value in range(1, 6)),
        coerce=int,
        empty_value=None,
    )

    class Meta:
        model = Review
        fields = ("rating", "comment")
        labels = {
            "comment": _("Коментар"),
        }
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": _("Поділіться враженнями про гру."),
                }
            ),
        }

    def clean_comment(self) -> str:
        """Reject comments containing whitespace only."""
        comment = self.cleaned_data["comment"].strip()
        if not comment:
            raise forms.ValidationError(
                _("Напишіть коментар до відгуку."),
                code="required",
            )
        return comment
