from django.db import models

class College(models.Model):
    code = models.CharField(max_length=255, unique=True)    # Non-Editable
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        # return f"Log - ID: {self.id}"
        return str(self.id)

    def get_name(self):
        return str(self.name)

    class Meta:
        db_table = 'college'


class Plan(models.Model):
    code = models.CharField(max_length=255, unique=True)    # Non-Editable
    name = models.CharField(max_length=255)
    users_limit = models.IntegerField(default=0)    # 0 means unlimited
    plan_amount = models.FloatField(default=0.0)

    def __str__(self):
        # return f"Log - ID: {self.id}"
        return str(self.id)

    def get_name(self):
        return str(self.name)

    class Meta:
        db_table = 'plan'


class CollegePlanMapping(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='cpm_plan')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='cpm_college')
    plan_start_date = models.DateTimeField(blank=True, null=True)
    plan_valid_until = models.DateTimeField(blank=True, null=True)    # * If this field is null then the plan is valid forever.
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)    # * If this field is false then the plan is expired.
    is_trial = models.BooleanField(default=False)
    trial_start_date = models.DateTimeField(blank=True, null=True)
    trial_end_date = models.DateTimeField(blank=True, null=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        # return f"Log - ID: {self.id}"
        return str(self.id)

    def get_name(self):
        return str(self.name)

    class Meta:
        # * `unique_together`: set of fields that, when taken together, must have unique values across all the rows in the database table. It is used to enforce a database-level constraint that ensures the combination of values in the specified fields is unique.
        # * So, no two rows in the table can have the same combination of values for the specified fields.
        unique_together = ('plan', 'college')    # ? For one college only one plan can be active.
        db_table = 'college_plan_mapping'


