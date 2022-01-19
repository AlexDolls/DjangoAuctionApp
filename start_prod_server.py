import subprocess

process2 = subprocess.Popen(["python3", "manage.py", "listing_date_checker"])
process3 = subprocess.Popen(["celery", "-A", "auctsite", "worker", "-l", "INFO", "--logfile=/home/app/web/logs/celery.log"])
process2.wait()
process3.wait()
