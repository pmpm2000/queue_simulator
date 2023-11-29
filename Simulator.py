from queue import Queue
import numpy as np


class Simulator:
    def __init__(self, simulation_time=20, queue_size=100, packet_limit=1000):
        # params for lambda and mi
        self.total_lambda = 0
        self.number_of_lambda = 0
        self.avg_lambda = 0
        self.total_mi = 0
        self.number_of_mi = 0
        self.avg_serve_time = 0
        self.rho = 0
        # parameters
        self.simulation_time = simulation_time
        self.queue_size = queue_size
        self.packet_limit = packet_limit
        self.clock = 0
        self.status = 0
        self.clients_in_queue = 0
        self.arrive_time = Queue(maxsize=queue_size)
        self.last_event_time = 0
        # next events
        self.next_client_arrival = self.__generate_event(0, 0)
        self.next_client_leave = self.__generate_event(self.next_client_arrival, 1)
        # statistics
        self.number_of_delays = 0
        self.total_delay = 0
        self.queue_busy = 0
        self.server_busy = 0
        self.packets_served = 0
        self.simulation_percent = 0


    def __str__(self):
        return f'''
        Clock: {self.clock}
        Status: {self.status}
        Clients in queue: {self.arrive_time.qsize()}
        Next client arrival: {self.next_client_arrival}
        Next client leave: {self.next_client_leave}
        Last event time: {self.last_event_time}
        Number of delays: {self.number_of_delays}
        Total delay: {self.total_delay}
        Queue busy: {self.queue_busy/self.clock}
        Server busy: {self.server_busy/self.clock}
        Packets served: {self.packets_served}
        Average lambda: {self.avg_lambda}
        Average serve time (1/mi): {self.avg_serve_time}
        Rho: {self.rho}
        B(t)/t: {self.server_busy/self.clock}
        ======================'''

    def __generate_event(self, actual_time, type):
        if type == 0:
            time_between_clients = round(np.random.exponential(scale=1.0), 2)
            self.total_lambda += time_between_clients
            self.number_of_lambda += 1
            return actual_time + time_between_clients  # scale = lamdba (intensywnosc naplywu)
        elif type == 1:
            serving_time = round(np.random.exponential(scale=0.1), 2) # scale = 1/mi
            self.total_mi += serving_time
            self.number_of_mi += 1
            return actual_time + serving_time

    def __time_algorithm(self):
        if self.next_client_arrival < self.next_client_leave:
            self.clock = self.next_client_arrival
            return 0
        else:
            self.clock = self.next_client_leave
            return 1

    def __event_algorithm(self, event_type):
        self.clients_in_queue = self.arrive_time.qsize()  # liczba klientow w kolejce w poprzedniej iteracji
        self.queue_busy += (self.clock - self.last_event_time) * self.clients_in_queue  # obszar ponizej Q(t)
        self.server_busy += (self.clock - self.last_event_time) * self.status  # obszar ponizej B(t)
        if event_type == 0:
            if self.status == 1:  # przychodzi klient, ale serwer zajety
                if not self.arrive_time.full():
                    self.arrive_time.put(self.clock)
                else:
                    print("Queue is full! Dropping packet...")
            elif self.status == 0:  # przychodzi klient a serwer wolny
                self.number_of_delays += 1  # liczba opoznien
                self.status = 1
                self.next_client_leave = self.__generate_event(self.clock, 1)
            self.next_client_arrival = self.__generate_event(self.clock, 0)  # losowanie przyjscia kolejnego klienta

        elif event_type == 1:
            if not self.arrive_time.empty():  # odchodzi klient, ale w kolejce jest nastepny
                self.next_client_leave = self.__generate_event(self.clock, 1)  # losowanie konca obslugi kolejnego klienta
                self.number_of_delays += 1  # liczba opoznien
                self.total_delay += self.clock - self.arrive_time.queue[0]  # calkowite opoznienie
                self.arrive_time.get()
            else:  # odchodzi klient, a kolejka jest pusta
                self.next_client_leave = float('inf')
                self.status = 0
        self.last_event_time = self.clock  # czas ostatniego zdarzenia
        self.packets_served += 1

    def start_simulation(self, arg):
        if arg == 'packet':
            self.simulation_time = float('inf')
        elif arg == 'time':
            self.packet_limit = float('inf')
        else:
            return -1

        while self.clock < self.simulation_time and self.packets_served < self.packet_limit:
            event_type = self.__time_algorithm()
            # print(f"Event type: {event_type}")
            self.__event_algorithm(event_type)
            self.avg_lambda = self.total_lambda/self.number_of_lambda
            self.avg_serve_time = self.total_mi/self.number_of_mi
            self.rho = self.avg_lambda * self.avg_serve_time
            last = self.simulation_percent
            self.simulation_percent = round(self.packets_served/self.packet_limit*100, 0)
            if self.simulation_percent != last:
                os.system('cls')
                print("Simulation in progress...")
                print(f"{self.simulation_percent}%")
        print("Simulation completed.")
        print(self)


if __name__ == "__main__":
    sim = Simulator(packet_limit=1000*1000)
    sim.start_simulation('packet')
