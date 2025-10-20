#imports
import simpy
import statistics
import random


def passenger(env, name, taxi_pool, ride_time_mean, wait_times, queue_lengths, busy_times):
    arrival_time = env.now
    with taxi_pool.request() as req:
        yield req           #waiting for a taxi
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)

        queue_lengths.append(len(taxi_pool.queue))      #recording queue length before getting a taxi

        ride_time = random.expovariate(1.0/ride_time_mean);
        yield env.timeout(ride_time)