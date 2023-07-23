from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import drf_signal_simplejwt.base_functions as base_f
from django.utils import timezone


# Timestamp is always unique. Though the below code is not timestamp.
def return_timestamped_user_code():
        last_user_code = UserDetail.objects.all().order_by('id').last()
        # import pdb; pdb.set_trace()
        if not last_user_code:
            return 'UC0001'
        else:
            timestamped_id = last_user_code.user_code
            timestamped_id = int(timestamped_id.split('UC')[-1])
            width = 4
            new_unique_int = timestamped_id + 1
            formatted = (width - len(str(new_unique_int))) * "0" + str(new_unique_int)
            new_unique_id = 'UC' + str(formatted)
            # print('new_unique_id-------->', new_unique_id)
            return new_unique_id


class UserDetail(AbstractUser):
    GENDER_CHOICE = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    USER_TYPE_CHOICE = (
        ('admin', 'admin'),
        ('teacher', 'teacher'),
        ('student', 'student'),
    )
    user_type = models.CharField(choices=USER_TYPE_CHOICE, max_length=20, default='student')
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=70,) # unique=True
    user_code = models.CharField(default=return_timestamped_user_code, max_length=255, blank=True, null=True, unique=True)
    gender = models.CharField(choices=GENDER_CHOICE, max_length=10, blank=True, null=True)
    phone_no = models.CharField(max_length=10, blank=True, null=True)
    password_to_know = models.CharField(max_length=200, blank=True, null=True)
    profile_img = models.FileField(upload_to=base_f.get_directory_path, blank=True, null=True)
    class_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='u_class_teacher')
    session = models.CharField(max_length=20, blank=True, null=True)
    semester = models.CharField(max_length=20, blank=True, null=True)
    stream = models.CharField(max_length=20, blank=True, null=True)
    course = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    #is_admin = models.BooleanField(default=False)
    # college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='u_college', blank=True, null=True)
    # department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='u_dept', blank=True, null=True)
    # sub_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='u_sub_dept', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    registered_on = models.DateTimeField(default=timezone.now)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='u_registered_by')
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='u_updated_by')
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='u_deleted_by')

    def __str__(self):    # ? Shows the details of specific fields if a user prints the 'instance' of this model.
        # return str(self.id)
        # return f"{self.first_name} - {self.last_name}"
        return str(self.first_name + ' ' + self.last_name)
    
    # ? Used to show name of foreign key in django admin. (Not Working Though)
    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)
        
    # ? Custom field by taking existing fields from this model. We can call `full_name` just like any other normal fields.
    @property
    def full_name(self):
        "Returns the person's full name."
        return '%s %s %s' % (self.first_name, self.middle_name, self.last_name) if self.middle_name else '%s %s' % (self.first_name, self.last_name)


    class Meta:
        db_table = 'user_detail'

        # ! After adding indexing in the model, we need to run `python manage.py makemigrations` and `python manage.py migrate` to create the index in the database.
        # ? Columns frequently used in WHERE clauses, JOIN conditions, and ORDER BY clauses are good candidates for indexing.
        # * Primary Key, Foreign Keys and fields with unique=True in the model are automatically indexed by Django.
        indexes = [
            models.Index(fields=['user_type'], name='idx_user_detail_user_type'),  # ? idx_<table_name>_<field_name>[_<sequence_number>]
            models.Index(fields=['user_code']),                                    # Index for unique constraint
            models.Index(fields=['class_teacher']),                                # Index for ForeignKey field
            models.Index(fields=['session', 'semester', 'stream', '-course']),     # ? Composite Index for frequent filtering in sequencial order of indexing (1,2,3,4), with descending order for `course`.
            models.Index(fields=['dob']),                                          # Index for frequent date filtering
            models.Index(fields=['is_deleted']),                                   # Index for frequent filter on boolean field
            models.Index(fields=['registered_on']),                                # Index for frequent date filtering
            models.Index(fields=['registered_by']),                                # ? If manually indexing ForeignKey field, then index the field with the same name as the field, not the _id suffix. Also, automatically indexed fields are replaced with the manually indexed fields in the database.
        ]

        '''
        ## ! Rebuild indexes for a specific app's models
        # python manage.py sqlsequencereset app_name | python manage.py dbshell

        ## ! Rebuild all indexes for the entire database
        # python manage.py sqlsequencereset | python manage.py dbshell

        ## ? The `sqlsequencereset` command generates the SQL commands to reset sequences for the specified app or the entire database, and the `dbshell` command allows executing SQL commands directly in the database.
        ### Index maintenance in MySQL is generally done using the `OPTIMIZE TABLE` statement to rebuild an index or the `ANALYZE TABLE` statement to analyze and update index statistics.
        '''

    def save(self, *args, **kwargs):
        super(UserDetail, self).save(*args, **kwargs)
        try:
            # from drf_signal_simplejwt.base_functions import save_face_data_while_creating_user
            pk = self.pk
            action = 'create'
            if pk:
                # action = 'update'
                # save_face_data_while_creating_user(pk, self, action=action)
                pass
        except:
            pass

