from django.db import models
from account.modelmixin import TimeStampMixin
from account.models import Organisation, CustomUser
from conf.models import Activity, Forms


# class CustomerTask(TimeStampMixin):
#     class TaskStatusChoice(models.TextChoices):
#         PENDING = 'PENDING', 'PENDING'
#         INPROGRESS = 'IN PROGRESS', 'IN PROGRESS'
#         CLOSED = 'CLOSED', 'CLOSED'
#
#     customer = models.ForeignKey("account.Customer", on_delete=models.CASCADE)
#     coordinator = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='coordinator_user')
#     task = models.CharField(max_length=255)
#     due_data = models.DateTimeField()
#     status = models.CharField(max_length=36, choices=TaskStatusChoice.choices, default=TaskStatusChoice.PENDING)
#
#
# class DocumentIssueSheet(TimeStampMixin):
#     customer = models.ForeignKey("account.Customer", on_delete=models.CASCADE)
#     activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
#     form = models.ForeignKey(Forms, on_delete=models.CASCADE)
#     project_details = models.CharField(max_length=255)
#     date_issued = models.DateField()
#     name = models.CharField(max_length=255)
#
#
# class DocumentIssueSheetDocument(TimeStampMixin):
#     issue_sheet = models.ForeignKey(DocumentIssueSheet, on_delete=models.CASCADE)
#     document_title = models.CharField(max_length=255)
#     document_number = models.CharField(max_length=120)
#     revision = models.PositiveIntegerField()

class Employee(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=120, null=True, blank=True)


class Document(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    file = models.FileField(upload_to='documents/')
    approval_date = models.DateField(null=True, blank=True)


class Audit(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    audit_type = models.CharField(max_length=100)
    scheduled_date = models.DateField()
    auditor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50)
    findings = models.TextField(blank=True)


class CAPA(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    issue = models.TextField()
    root_cause = models.TextField()
    corrective_action = models.TextField()
    preventive_action = models.TextField()
    containment_action = models.TextField()
    effectiveness_verified = models.BooleanField(default=False)
    responsible = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    due_date = models.DateField()
    status = models.CharField(max_length=50)


class NonConformance(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)  # Internal or External
    description = models.TextField()
    date_reported = models.DateField(auto_now_add=True)
    severity = models.CharField(max_length=20)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    root_cause_analysis = models.TextField(blank=True)
    status = models.CharField(max_length=50)


class Complaint(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    complaint_details = models.TextField()
    date_received = models.DateField()
    related_nc = models.ForeignKey(NonConformance, on_delete=models.SET_NULL, null=True, blank=True)
    resolution = models.TextField(blank=True)
    status = models.CharField(max_length=50)


class TrainingRecord(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    requirement = models.TextField()
    completion_date = models.DateField()
    status = models.CharField(max_length=50)


class TrainingRecord(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    requirement = models.TextField()
    completion_date = models.DateField()
    status = models.CharField(max_length=50)


class ChangeControl(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    change_description = models.TextField()
    initiated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    affected_area = models.CharField(max_length=255)
    impact_analysis = models.TextField()
    approval_status = models.CharField(max_length=50)
    workflow_step = models.CharField(max_length=100)
    status = models.CharField(max_length=50)


class RiskAssessment(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    risk_type = models.CharField(max_length=50)
    identified_risks = models.TextField()
    impact = models.CharField(max_length=100)
    mitigation_plan = models.TextField()
    control_measures = models.TextField()
    status = models.CharField(max_length=50)