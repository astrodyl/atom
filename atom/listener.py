from atom.core import factories
from atom.core.kafka.kafka import Kafka


"""
    Astronomical Transient Observation Manager (ATOM)

    A rapid-response tool for fast-evolving transient events.

    ATOM listens for notices streamed via NASA's General Coordinates Network
    (GCN) [1] and schedules follow-up observations using UNC-Chapel Hill's
    global robotic telescope network, Skynet [2].

    Additional Information:
        [1] https://gcn.nasa.gov/
        [2] https://www.danreichart.com/skynet
"""


class Listener:
    """
    Listens for GCN notices streams via NASA's GCN.

    Attributes
    ----------
    kafka : Kafka
        The streaming object.
    """
    def __init__(self, kafka: Kafka):
        self.kafka = kafka

    def listen(self):
        """ Listens for GCN notices streamed via Kafka. """
        while True:
            try:
                for message in self.kafka.consumer.consume():
                    factories.responder(message).respond()

            except Exception as ex:
                print('logging exception', ex)  # TODO: log the exception

            finally:
                print('recording notice')  # TODO: Record the notice to the database


if __name__ == '__main__':
    Listener(Kafka.from_toml(test=False)).listen()
