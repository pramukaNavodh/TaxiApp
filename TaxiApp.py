#imports
import simpy
import statistics
import random
import matplotlib.pyplot as plt

#passenger
def passenger(env, name, driver_pool, ride_time_mean, reposition_mean, wait_times, 
              queue_at_arrivals, total_busy_time):
    arrival_time = env.now                              # recording the passenger arrival time
    queue_at_arrival = len(driver_pool.queue)           #length of queue at arrival
    queue_at_arrivals.append(queue_at_arrival)

    with driver_pool.request() as req:
        yield req                                       #waiting for a taxi
        wait_time = env.now - arrival_time              #calculating waiting time
        wait_times.append(wait_time)

        #driver assigned - simulation of ride
        ride_time = random.expovariate(1.0/ ride_time_mean);
        yield env.timeout(ride_time)
        total_busy_time[0] += ride_time                 #accumulating busy time

        #reposition the driver after the trip
        reposition_time = random.expovariate(1.0/ reposition_mean)
        yield env.timeout(reposition_time)
        total_busy_time[0] += reposition_time           #reposition time + total busy time

# #driver
# def driver(env, name, driver_pool):
#     while True:
#         yield driver_pool

#taxi system
def system(env, arrival_rate, num_drivers, ride_time_mean, reposition_mean, sim_duration,wait_times,queue_at_arrivals,
           total_busy_time):
    driver_pool = simpy.Resource(env, capacity = num_drivers);  # Creating a pool of available taxis

    # #spawning individual driver processes
    # for i in range(num_drivers):
    #     env.process(driver(env,f'Driver-{i}',driver_pool))

    #generating passengerss
    while True:
        inter_arrival = random.expovariate(arrival_rate);   
        yield env.timeout(inter_arrival)                        #waiting until next passenger
        if env.now >= sim_duration:                             #stop sim when time limit meet
            break
        env.process(passenger(env, f'Passenger-{len(wait_times)+1}', driver_pool,ride_time_mean,reposition_mean,
                          wait_times, queue_at_arrivals, total_busy_time))
        


#full simulation
def run_simulation (arrival_rate, num_drivers,ride_time_mean = 15, reposition_mean = 2,
                sim_duration = 480, seed = 42):
    random.seed(seed)
    env = simpy.Environment()

    #store stats while sim
    wait_times = []
    queue_at_arrivals = []
    total_busy_time = [0.0]

    #starting the main system 
    env.process(system(env,arrival_rate,num_drivers,ride_time_mean,reposition_mean,sim_duration,wait_times,queue_at_arrivals,
                       total_busy_time))
    env.run(until = sim_duration)

    #calculatiion of metrics
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    max_queue = max(queue_at_arrivals) if queue_at_arrivals else 0
    throughput = len(wait_times)                            #total passengers served
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

    # def sim_gen():
    #     yield from system(env, arrival_rate,num_drivers,ride_time_mean,reposition_mean,sim_duration)
    # results = env.run(until=sim_duration, generator = sim_gen)
    # return results;

driver_counts = [10, 25, 50, 75, 120, 300 ]
utilizations =[]


#case 1
if __name__ == "__main__":
    results = run_simulation(arrival_rate=0.5, num_drivers=5, ride_time_mean=15, sim_duration=480)
    print("Simulation results - ")
    for k, v in results.items():
        if isinstance(v, (float, int)):
            print(f"{k}: {v:.2f}")

for d in driver_counts:
    res = run_simulation(arrival_rate=0.5,num_drivers=d,ride_time_mean=15, sim_duration=480)
    utilizations.append(res['utilization'])


#visualization
#1 queue length over the time
plt.plot(results['queue_at_arrivals'])
plt.xlabel("Passenger arrivals")
plt.ylabel("Queue length")
plt.title("Queue length at passenger arrival")
plt.show()

#2 passenger waiting time
plt.figure()
plt.hist(results['all_wait_time'], bins=20)
plt.xlabel("Wait Times(M)")
plt.ylabel("Number of passenger")
plt.title("Passenger waiting time")
plt.show()

#3  utilization vs number of drivers
plt.figure()
plt.plot(driver_counts,utilizations,marker='o')
plt.xlabel("Number of drivers")
plt.ylabel("utilization (%)")
plt.title("Utilization vs Number of Drivers")
plt.show()
