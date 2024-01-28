from datetime import datetime, time

morn_time = time(10, 0)
even_time = time(17, 0)
curr_time = datetime.now().time()
print(curr_time)

if morn_time <= curr_time < even_time:
    print("Its morning ")
else:
    print("Its Evening ")

