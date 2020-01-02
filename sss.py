from celery.worker.control import revoke
from sample import add, app
import time

#result = add.delay(4, 4)

#print(result.ready)
result = add.delay(4, 99)
time.sleep(3)
result.revoke(terminate=True)
#r = revoke(state=result.state, task_id=result.id, terminate=True, signal="SIGKILL")
#app.control.revoke(state=result.state, task_id=result.id, terminate=True, signal="SIGKILL")
while not result.ready():
    print("waiting")
    pass


s = result.get()
print(s)



