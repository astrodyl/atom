from gcn_kafka import Consumer

from atom.core.io import path_utils, toml_utils


class Kafka:
    """
    Subscribes and streams notices via NASA's GCN Kafka.

    The `secret_id` is required to stream notices over Kafka. However, it is
    only used to connect and is not stored in the class or anywhere else.

    Attributes
    ----------
    client_id : str
        The client ID to connect to Kafka.

    topics : list of str
        The topics to subscribe to.

    consumer : `gcn_kafka.Consumer`
        ??
    """
    def __init__(self, client_id: str, secret_id: str, topics: list[str]):
        self.client_id = client_id
        self.topics = topics
        self.consumer = self._consumer(secret_id)

    def __repr__(self):
        """ Returns `Kafka(client_id=abc..xyz)`. """
        class_name = self.__class__.__name__
        return f"{class_name}(client_id={self.client_id[3:]}..{self.client_id[:-3]})"

    @classmethod
    def from_toml(cls, test: bool = False):
        """

        Parameters
        ----------
        test

        Returns
        -------
        Kafka
            The instantiated Kafka object.
        """
        topics_section = 'test' if test else 'topics'
        tokens = toml_utils.read(path_utils.token_path()).get('kafka')
        topics = toml_utils.read(path_utils.kafka_topics_path())

        return cls(
            tokens.get('client_id'),
            tokens.get('secret_id'),
            topics.get(topics_section).values()
        )

    def subscribe(self):
        """"""
        pass

    def _consumer(self, secret_id: str) -> Consumer:
        """"""
        consumer = Consumer(client_id=self.client_id, secret_id=secret_id)
        consumer.subscribe(self.topics)

        return consumer
