from subprocess import Popen

# filename = "tc/sync.py"
#
# while True:
#     print("\nStarting " + filename)
#     p = Popen("/usr/local/bin/python3.9 " + filename, shell=True)
#     p.wait()

filename = "run python3 evotor/sync.py"

while True:
    print("\nStarting " + filename)
    p = Popen("/Library/Frameworks/Python.framework/Versions/3.10/bin/poetry  " + filename, shell=True)
    p.wait()
