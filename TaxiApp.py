#imports
import simpy
import statistics
import random

#passenger
def passenger(env, name, taxi_pool, ride_time_mean, wait_times, queue_lengths, busy_times):
    arrival_time = env.now
    with taxi_pool.request() as req:
        yield req           #waiting for a taxi
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)

        queue_lengths.append(len(taxi_pool.queue))      #recording queue length before getting a taxi

        ride_time = random.expovariate(1.0/ride_time_mean);
        yield env.timeout(ride_time)

#driver
def driver(env, name, driver_pool):
    while True:
        yield driver_pool

#taxi system
def system(env, arrival_rate, num_drivers, ride_time_mean, reposition_mean, sim_duration):
    driver_pool = simpy.Resource(env, capacity = num_drivers);
    wait_time = []
    queue_at_arrivals = []
    total_busy_time = [0.0]

    #spawning individual driver processes
    for i in range(num_drivers):
        env.process(driver(env,f'Driver-{i}',driver_pool))

    #generating drivers
    while True:
        inter_arrival = random.expovariate(arrival_rate);
        yield env.timeout(inter_arrival)
        if env.now >= sim_duration:
            break
        env.process(rider(env, f'Rider-{len(wait_time)+1}', driver_pool,ride_time_mean,reposition_mean,
                          wait_times, queue_at_arrivals, total_busy_time))
        
    #calculatiion of metrics
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    max_queue = max(queue_at_arrivals) if queue_at_arrivals else 0
    throughput = len(wait_times)
    utilization = (total_busy_time[0] / (num_drivers * sim_duration)) * 100 if total_busy_time[0] >0 else 0

    return{
        'avg_wait_time':avg_wait,
        'max_queue_length':max_queue,
        'throughput' : throughput,
        'utilization' : utilization,
        "all_wait_time" : wait_times,
        "queue_at_arrivals" : queue_at_arrivals,
        'total_busy_time' : total_busy_time[0]

    }
