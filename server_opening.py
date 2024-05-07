from subprocess import Popen


filename = "tc/schedules/__init__.py"

while True:
    print("\nStarting " + filename)
    p = Popen("/usr/local/bin/python3.8 " + filename, shell=True)
    p.wait()
