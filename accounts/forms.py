import re

from datetime import timedelta
from django import forms
from . import models
from tinymce.widgets import TinyMCE

# Regex pattern to insure, conatins, lower, upprt, numeric and special
# characters and is at least 14 characters long and no spaces
pattern = ("^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#*$@!%])" +
           "[A-Za-z0-9#*@$!%\d]{14,}$")
password_regex = re.compile(pattern)


# Function to claer all <> tags
def removetags(raw):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw)
    return cleantext


class ProfileForm(forms.ModelForm):
    email = forms.EmailField()
    confirm_email = forms.CharField(required=False)
    date_of_birth = forms.DateField(input_formats=['%Y-%m-%d',
                                                   '%m/%d/%Y',
                                                   '%m/%d/%y'],
                                    widget=forms.DateInput(format='%Y-%m-%d'))
    short_bio = forms.CharField(widget=TinyMCE(attrs={'rows': 10}),
                                min_length=10)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = models.UserProfile
        fields = [
            'first_name',
            'last_name',
            'email',
            'confirm_email',
            'date_of_birth',
            'short_bio',
            'avatar',
            'city',
            'state',
            'country',
            'favorite_animal',
            'hobby',
        ]

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        # Check date is in the Past
        date_of_birth = cleaned_data.get("date_of_birth")
        if date_of_birth.year > 2020:
            adjusted_date = date_of_birth - timedelta(days=36524.25)
            cleaned_data["date_of_birth"] = adjusted_date

        # Work around formatted text length
        short_bio = cleaned_data.get("short_bio")
        if short_bio is None or len(removetags(short_bio)) < 10:
            raise forms.ValidationError("Your Bio must be at least 10 " +
                                        "characters long.")

        # Check email match
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")

        if email != confirm_email:
            raise forms.ValidationError(
                "email and confirm email do not match")

        return cleaned_data


class PasswordChangeCustomForm(forms.Form):
    current_password = forms.CharField(required=True,
                                       widget=forms.PasswordInput())
    new_password = forms.CharField(required=True,
                                   widget=forms.PasswordInput(
                                    attrs={'data-indicator': 'pwindicator'}),
                                   min_length=14)
    confirm_password = forms.CharField(required=True,
                                       widget=forms.PasswordInput(),
                                       min_length=14)

    # Override init to get user and profile
    def __init__(self, data=None, user=None, profile=None, *args, **kwargs):
        self.user = user
        self.profile = profile
        super(PasswordChangeCustomForm, self).__init__(data=data,
                                                       *args, **kwargs)

    def clean(self):
        cleaned_data = super(PasswordChangeCustomForm, self).clean()

        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check current password is correct
        if not self.user.check_password(current_password):
            raise forms.ValidationError('incorrect current password')

        # Check password does not equal current password
        if new_password == current_password:
            raise forms.ValidationError(
                "new password cannot be same as current password")

        # Check password contains:
        # Uppercase, lowercase, numeric and from @ # $
        if re.match(password_regex, new_password) is None:
            raise forms.ValidationError(
                "new password must contain, both upper and lowercase " +
                "letters, numbers and characters from #*$@!%, but no spaces")

        # Check password does not contain, first, last or usernames
        if ((self.profile.first_name.lower() != '' and
                self.profile.first_name.lower() in new_password.lower()) or
                (self.profile.last_name.lower() != '' and
                 self.profile.last_name.lower() in new_password.lower()) or
                self.user.username.lower() in new_password.lower()):
            raise forms.ValidationError(
                "password cannot contain your username, firstname or lastname")

        # Check new passwords match
        if new_password != confirm_password:
            raise forms.ValidationError(
                "new and confirm passwords do not match")

        return cleaned_data


class CropForm(forms.Form):
    """ Hide a fields to hold the coordinates chosen by the user """
    scale = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'display:none'}))
    angle = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'display:none'}))
    x = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    y = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    w = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    h = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
