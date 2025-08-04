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
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=120, null=True, blank=True, verbose_name="Job Title")
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    employee_id = models.CharField(max_length=50, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.name} ({self.designation or 'No Title'})"


class Document(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        UNDER_REVIEW = 'Under Review', 'Under Review'
        APPROVED = 'Approved', 'Approved'
        ARCHIVED = 'Archived', 'Archived'
        REJECTED = 'Rejected', 'Rejected'

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='uploaded_documents'
    )
    file = models.FileField(upload_to='documents/')
    approval_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        unique_together = ('organisation', 'title', 'version')

    def __str__(self):
        return f"{self.title} (v{self.version}) - {self.status}"


class Audit(models.Model):
    class AuditTypeChoices(models.TextChoices):
        INTERNAL = 'Internal', 'Internal'
        EXTERNAL = 'External', 'External'
        SUPPLIER = 'Supplier', 'Supplier'
        CUSTOMER = 'Customer', 'Customer'
        OTHER = 'Other', 'Other'

    class StatusChoices(models.TextChoices):
        SCHEDULED = 'Scheduled', 'Scheduled'
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'
        CLOSED = 'Closed', 'Closed'
        CANCELLED = 'Cancelled', 'Cancelled'

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='audits')
    title = models.CharField(max_length=255)
    audit_type = models.CharField(max_length=100, choices=AuditTypeChoices.choices, default=AuditTypeChoices.INTERNAL)
    scheduled_date = models.DateField()
    auditor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_audits'
    )
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.SCHEDULED)
    findings = models.TextField(blank=True, verbose_name="Audit Findings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Audit"
        verbose_name_plural = "Audits"

    def __str__(self):
        return f"{self.title} - {self.audit_type} - {self.status}"


class CAPA(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'Open', 'Open'
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'
        VERIFIED = 'Verified', 'Verified'
        CLOSED = 'Closed', 'Closed'

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='capas')
    issue = models.TextField(verbose_name="Issue Description")
    root_cause = models.TextField(verbose_name="Root Cause")
    corrective_action = models.TextField()
    preventive_action = models.TextField()
    containment_action = models.TextField()
    effectiveness_verified = models.BooleanField(default=False)
    responsible = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_capas'
    )
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']
        verbose_name = "CAPA"
        verbose_name_plural = "CAPAs"

    def __str__(self):
        return f"CAPA - {self.issue[:30]}... ({self.status})"


class NonConformance(models.Model):
    class SourceChoices(models.TextChoices):
        INTERNAL = 'Internal', 'Internal'
        EXTERNAL = 'External', 'External'

    class SeverityChoices(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'
        CRITICAL = 'Critical', 'Critical'

    class StatusChoices(models.TextChoices):
        OPEN = 'Open', 'Open'
        UNDER_INVESTIGATION = 'Under Investigation', 'Under Investigation'
        RESOLVED = 'Resolved', 'Resolved'
        CLOSED = 'Closed', 'Closed'

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='non_conformances')
    source = models.CharField(max_length=100, choices=SourceChoices.choices, default=SourceChoices.INTERNAL)
    description = models.TextField()
    date_reported = models.DateField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=SeverityChoices.choices, default=SeverityChoices.LOW)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_non_conformances')
    root_cause_analysis = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_reported']
        verbose_name = "Non-Conformance"
        verbose_name_plural = "Non-Conformances"

    def __str__(self):
        return f"{self.source} - {self.severity} - {self.status}"


class TrainingRecord(models.Model):
    class StatusChoices(models.TextChoices):
        COMPLETED = 'completed', 'Completed'
        IN_PROGRESS = 'in_progress', 'In Progress'
        OVERDUE = 'overdue', 'Overdue'

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='training_records')
    employees = models.ManyToManyField('Employee', related_name='training_records')
    topic = models.CharField(max_length=255)
    requirement = models.TextField()
    completion_date = models.DateField()
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.IN_PROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-completion_date']
        verbose_name = "Training Record"
        verbose_name_plural = "Training Records"

    def __str__(self):
        return f"{self.topic} - {self.get_status_display()}"


class ChangeControl(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        APPROVED = 'Approved', 'Approved'
        REJECTED = 'Rejected', 'Rejected'

    class StatusChoices(models.TextChoices):
        OPEN = 'Open', 'Open'
        IN_PROGRESS = 'In Progress', 'In Progress'
        CLOSED = 'Closed', 'Closed'

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='change_controls')
    change_description = models.TextField(verbose_name="Description of the Change")
    initiated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='initiated_changes')
    affected_area = models.CharField(max_length=255)
    impact_analysis = models.TextField(verbose_name="Impact Analysis")
    approval_status = models.CharField(max_length=50, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    workflow_step = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Change Control"
        verbose_name_plural = "Change Controls"

    def __str__(self):
        return f"{self.affected_area} - {self.approval_status}"


class RiskAssessment(models.Model):
    class RiskType(models.TextChoices):
        OPERATIONAL = 'Operational', 'Operational'
        FINANCIAL = 'Financial', 'Financial'
        COMPLIANCE = 'Compliance', 'Compliance'
        STRATEGIC = 'Strategic', 'Strategic'
        OTHER = 'Other', 'Other'

    class ImpactLevel(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'
        CRITICAL = 'Critical', 'Critical'

    class StatusChoices(models.TextChoices):
        OPEN = 'Open', 'Open'
        MONITORING = 'Monitoring', 'Monitoring'
        RESOLVED = 'Resolved', 'Resolved'
        CLOSED = 'Closed', 'Closed'

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='risk_assessments')
    title = models.CharField(max_length=255)
    risk_type = models.CharField(max_length=50, choices=RiskType.choices, default=RiskType.OTHER)
    identified_risks = models.TextField(verbose_name="Identified Risks")
    impact = models.CharField(max_length=100, choices=ImpactLevel.choices, default=ImpactLevel.MEDIUM)
    mitigation_plan = models.TextField()
    control_measures = models.TextField()
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Risk Assessment"
        verbose_name_plural = "Risk Assessments"

    def __str__(self):
        return f"{self.title} ({self.risk_type}) - {self.status}"


class ManagementReview(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='management_reviews')
    date = models.DateField()
    attendees = models.ManyToManyField(Employee, related_name='review_attendance')
    agenda = models.TextField()
    minutes = models.TextField()
    actions = models.TextField()

    class Meta:
        ordering = ['-date']
        verbose_name = "Management Review"
        verbose_name_plural = "Management Reviews"

    def __str__(self):
        return f"Review on {self.date}"


class QualityPolicy(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='quality_policies')
    content = models.TextField()
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_policies')
    approval_date = models.DateField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-approval_date']
        verbose_name = "Quality Policy"
        verbose_name_plural = "Quality Policies"

    def __str__(self):
        return f"Policy approved on {self.approval_date}"