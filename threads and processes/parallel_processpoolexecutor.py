# SuperFastPython.com
# example of a parallel for loop with the ProcessPoolExecutor class
import concurrent.futures
import random
import time


# execute a task
def task(value):
    # add your work here...
    # ...
    random_num = random.randrange(1, 10) 
    print(f'task {value} would like to sleep for {random_num} seconds')
    time.sleep(random_num)

    # return a result, if needed
    return value


# protect the entry point
if __name__ == '__main__':
    # create the pool with the default number of workers
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as exe:
        # issue some tasks and collect futures
        futures = [exe.submit(task, i) for i in range(50)]
    
        # process results as tasks are completed
        for future in concurrent.futures.as_completed(futures):
            print(f'>got {future.result()}')
        
        # issue one task for each call to the function
        for result in exe.map(task, range(50)):
            print(f'>got {result}')
        
    # report that all tasks are completed
    print('Done')