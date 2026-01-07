# events/forms.py
from django import forms
from .models import Event
from athletes.models import Athlete
from core.models import Statistic, Team
from django.db.models import Q
#from django.utils import timezone


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # We will handle 'participants' separately
        fields = ['name', 'description', 'start_time', 'end_time', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            # Use HTML5 date/time input for better UX
            'schedule': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

       # --- DELETE OR COMMENT OUT THIS ENTIRE METHOD ---
    # def clean_schedule(self):
    #     """
    #     This method is no longer needed as the form field now correctly
    #     provides a timezone-aware datetime.
    #     """
    #     schedule_time = self.cleaned_data.get('schedule')
    #     if schedule_time:
    #         return timezone.make_aware(schedule_time, timezone.get_current_timezone())
    #     return schedule_time



class ParticipantManagementForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=Athlete.objects.none(), # Start with an empty queryset
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="" # Hide the default label
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The queryset will be set dynamically in the view
        # We set the full queryset here as a fallback
        self.fields['participants'].queryset = Athlete.objects.all().select_related('user', 'sport', 'campus')

        
    class Meta:
        model = Event
        fields = ['participants']


class EventScheduleForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'start_time', 'end_time', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


class GameReportForm(forms.Form):
    """
    A dynamic form for a game report. It builds its fields based on the sport
    and adds special data attributes to the widgets to enable automatic front-end
    calculations for points and percentages.
    """
    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        super().__init__(*args, **kwargs)

        if sport:
            # Get all relevant stats, excluding the automated Win/Loss
            all_stats_for_sport = Statistic.objects.filter(
                Q(sport__isnull=True) | Q(sport=sport)
            ).exclude(short_name__in=['wins', 'losses'])
            
            for stat in all_stats_for_sport:
                # Base attributes for all numeric input fields
                attrs = {
                    'class': 'form-control form-control-sm text-center stat-input',
                    'min': '0',
                    'value': '0' # Start all fields at 0 for a clean UI
                }
                
                stat_name_lower = stat.name.lower()

                # --- LOGIC FOR AUTO-CALCULATING POINTS ---
                # Add a 'data-points-worth' attribute to any stat that scores points
                if '3-point made' in stat_name_lower:
                    attrs['data-points-worth'] = '3'
                elif '2-point made' in stat_name_lower:
                    attrs['data-points-worth'] = '2'
                elif 'free throw made' in stat_name_lower:
                    attrs['data-points-worth'] = '1'
                
                # If this is the main 'Points' stat, make it read-only
                if stat.short_name.lower() == 'pts':
                    attrs['readonly'] = True
                    attrs['class'] += ' bg-light fw-bold' # Style it to look calculated
                # --- END OF POINTS LOGIC ---

                # --- LOGIC FOR AUTO-CALCULATING PERCENTAGES ---
                # Add 'data-stat-type' and 'data-stat-group' for made/attempted pairs
                if 'made' in stat_name_lower:
                    attrs['data-stat-type'] = 'made'
                    # Creates a group name like '3-pointers'
                    attrs['data-stat-group'] = stat_name_lower.replace(' made', '').replace(' ', '-')
                elif 'attempted' in stat_name_lower:
                    attrs['data-stat-type'] = 'attempted'
                    attrs['data-stat-group'] = stat_name_lower.replace(' attempted', '').replace(' ', '-')
                # --- END OF PERCENTAGE LOGIC ---
                
                self.fields[stat.short_name] = forms.IntegerField(
                    label=stat.name,
                    required=False,
                    widget=forms.NumberInput(attrs=attrs)
                )

class EventOutcomeForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['our_score', 'opponent_score']
        labels = {
            'our_score': "Our Team's Score (Auto-Calculated)", # Update label
            'opponent_score': "Opponent's Score",
        }
        widgets = {
            # --- THIS IS THE CHANGE ---
            # Make the 'our_score' field read-only
            'our_score': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            # --- END OF CHANGE ---
            'opponent_score': forms.NumberInput(attrs={'class': 'form-control'}),
        }