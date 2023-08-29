- Copy the [django_launcher.service](django_launcher.service) file at: `/etc/systemd/system/django_launcher.service`.
- Then run:
    * `chmod +x django_launcher.sh`
    * `systemctl start django_launcher`
    * `systemctl enable django_launcher`
