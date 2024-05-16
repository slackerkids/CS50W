from django import forms
from .models import Category


# Retrieve categories from database using List comrehension
CHOICES = [(None, 'No Category Listed')] + [(category.id, category.name) for category in Category.objects.all()]

# Form for creating Listing
# TODO style form
class ListingForm(forms.Form):
    title = forms.CharField(
        max_length=64,
        required=True,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px; margin: 10px;',
            'placeholder': 'Listing Title'
        }),
        label=False  # This removes the label for the content field
    )
    description = forms.CharField(
        max_length=300, 
        required=False,
        widget=forms.Textarea(attrs={
            'class': "form-control",
            'style': 'max-width: 300px; height: 100px; margin: 10px;',
            'placeholder': 'Description'
        }),
        label=False
    )
    
    bid = forms.IntegerField( 
        required=True,
        widget=forms.NumberInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px; margin: 10px;',
            'placeholder': 'Bid amount'
        }),
        label=False
    )

    image = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px; margin: 10px;',
            'placeholder': 'Image Url'
        }),
        label=False
    )

    category = forms.ChoiceField(
        choices=CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': "form-control",
            'style': "margin: 10px;"
        }),
        label=False
    )


class CommentForm(forms.Form):
    content = forms.CharField(
        max_length=300,
        required=True,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px; margin-bottom: 10px;',
            'placeholder': 'Enter your comment here'
        }),
        label=False  # This removes the label for the content field
    )