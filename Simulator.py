from queue import Queue
import numpy as np


def generate_event(actual_time, type):
    if type == 0:
        return round(actual_time + np.random.exponential(scale=1.0), 2)
    elif type == 1:
        return round(actual_time + np.random.exponential(scale=2.0), 2)


class Simulator:
    def __init__(self, simulation_time=20, queue_size=100):
        # parameters
        self.simulation_time = simulation_time
        self.queue_size = queue_size
        self.clock = 0
        self.status = 0
        self.clients_in_queue = 0
        self.arrive_time = Queue(maxsize=queue_size)
        self.last_event_time = 0
        # next events
        self.next_client_arrival = generate_event(0, 0)
        self.next_client_leave = generate_event(self.next_client_arrival, 1)
        # statistics
        self.number_of_delays = 0
        self.total_delay = 0
        self.queue_busy = 0
        self.server_busy = 0

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
        Queue busy: {self.queue_busy}
        Server busy: {self.server_busy}
        ======================'''

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
                self.arrive_time.put(self.clock)
            if self.status == 0:  # przychodzi klient a serwer wolny
                self.number_of_delays += 1  # liczba opoznien
                self.status = 1
                self.next_client_leave = generate_event(self.clock, 1)
            self.next_client_arrival = generate_event(self.clock, 0)  # losowanie przyjscia kolejnego klienta

        elif event_type == 1:
            if not self.arrive_time.empty():  # odchodzi klient, ale w kolejce jest nastepny
                self.next_client_leave = generate_event(self.clock, 1)  # losowanie konca obslugi kolejnego klienta
                self.number_of_delays += 1  # liczba opoznien
                self.total_delay += self.clock - self.arrive_time.queue[0]  # calkowite opoznienie
                self.arrive_time.get()
            else:  # odchodzi klient, a kolejka jest pusta
                self.next_client_leave = float('inf')
                self.status = 0
        self.last_event_time = self.clock  # czas ostatniego zdarzenia

    def start_simulation(self):
        while self.clock < self.simulation_time:
            event_type = self.__time_algorithm()
            print(f"Event type: {event_type}")
            self.__event_algorithm(event_type)
            print(self)
        print("Simulation completed.")


if __name__ == "__main__":
    sim = Simulator()
    sim.start_simulation()
