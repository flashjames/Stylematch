from django.dispatch import Signal

approved_user_criteria_changed = Signal(providing_args=['request', 'userprofile'])
