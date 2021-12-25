import subprocess

process2 = subprocess.Popen(["python3", "manage.py", "runserver"])
process3 = subprocess.Popen(["python3", "manage.py", "listing_date_checker"])
process2.wait()
process3.wait()

