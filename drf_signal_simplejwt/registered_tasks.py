from users.tasks import test_task


def registered_tasks():
    # test_task(repeat=24*60*60)
    # print('-------------')
    test_task(repeat=10)

