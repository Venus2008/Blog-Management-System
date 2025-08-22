from django.utils.translation import gettext_lazy as _ 
from django.db.models import TextChoices

class RoleChioice(TextChoices):
    ADMIN='Admin',_('Admin')
    STAFF='Staff',_('Staff')
    USER='User',_('User')