from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
import threading
import time


class Supervisor:
    """
    Supervises child actors and restarts them if they fail.
    """

    def __init__(self):
        self._child_actors = []
        self._running = True

    def add_child(self, actor):
        self._child_actors.append(actor)

    def start(self):
        for actor in self._child_actors:
            actor.start()

    def supervise(self):
        try:
            while self._running:
                for actor in self._child_actors:
                    if not actor.is_alive():
                        print(f"Actor {actor} has crashed. Restarting...")
                        actor.start()  # Restart the actor
                time.sleep(1)  # Check periodically
        except KeyboardInterrupt:
            print("Supervisor shutting down...")
        finally:
            self.stop()

    def stop(self):
        """Stops the supervisor and all child actors."""
        self._running = False
        for actor in self._child_actors:
            actor.stop()


class Actor:
    """
    Base class for all actors.
    """

    def __init__(self):
        self._mailbox = Queue()
        self._executor = None
        self._running = False

    def receive(self, message):
        """
        Handles incoming messages.
        """
        raise NotImplementedError("Must implement receive method in subclass")

    def send(self, target_actor, message):
        """
        Sends a message to another actor.
        """
        target_actor._mailbox.put(message)

    def start(self):
        """
        Starts the actor's message loop.
        """
        if self._running:
            return  # Avoid starting the actor multiple times

        self._running = True
        self._executor = ThreadPoolExecutor(max_workers=1)

        def message_loop():
            while self._running:
                try:
                    message = self._mailbox.get(timeout=1)
                    self.receive(message)
                except Empty:
                    continue
                except Exception as e:
                    print(f"Error in actor {self}: {e}")

        self._executor.submit(message_loop)

    def stop(self):
        """Stops the actor."""
        self._running = False
        if self._executor:
            self._executor.shutdown(wait=True)

    def is_alive(self):
        """Checks if the actor is running."""
        return self._running


class MyActor(Actor):
    """
    Example actor that prints received messages.
    """

    def receive(self, message):
        print(f"Actor {id(self)} received message: {message}")
        # Simulate failure for demonstration
        if message == "fail":
            raise Exception("Simulated failure")


if __name__ == "__main__":
    actor1 = MyActor()
    actor2 = MyActor()

    supervisor = Supervisor()
    supervisor.add_child(actor1)
    supervisor.add_child(actor2)

    supervisor.start()

    # Simulate sending messages
    actor1.send(actor1, "hello")
    actor2.send(actor2, "fail")
    actor1.send(actor1, "world")

    # Run supervisor loop
    try:
        supervisor.supervise()
    except KeyboardInterrupt:
        print("Exiting...")
