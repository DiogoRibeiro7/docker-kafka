import subprocess
from shlex import quote
from configparser import ConfigParser
from os import environ
from pykafka import KafkaClient
from json import dumps, loads
from time import sleep

__author__ = 'yazan'
__licence__ = 'Apache V2'

class KafkaManager(object):
    """Convenience interface to facilitate CLI interface with the host of a
    running kafka server when kafka is packaged within a docker container.
    Since $KAFKA_HOME/bin scripts can only be run on the host, this class
    will constantly listen to topic <kafka-manager-in> and respond to requests
    such as creating topics, and so forth to topic <kafka-manager-out>. All 
    subscribers to these two topics receive all published messages and are
    able to relate requests between the two topics through transaction IDs.
    """
    def __init__(self):
        # Parse environment variables as DEFAULT configurations
        self.config = ConfigParser(environ)
        self.config.read(environ.get('KAFKA_MANAGER_CONFIG_DIR'))
        self.kafka_home = self.config.get('KAFKA_HOME')
        self.scripts = dict(self.config.items('kafka-cli'))
        self.zkpr = self.config.get('zookeeper', 'gateway')
        self.consumer_grp = self.config.get('kafka', 'default_consumer_group')
        self.kafka_host = config.get('kafka', 'gateway')
        self.client = KafkaClient(hosts=self.kafka_host)
        # Create dictionary of possible request functions - layer of protection
        # against running unverified commands on the host 
        self.func_dict = {'list_topics': self.list_topics,
                          'is_topic': self.is_topic,
                          'get_topic': self.get_topic,
                          'make_topic': self.make_topic,
                          'delete_topic': self.delete_topic}
        # Initialize <kafka-manager> topics
        self.make_topic(topic='kafka-manager-in')
        self.make_topic(topic='kafka-manager-out')

    def health_check(self):
        """Idea, every 30 min run thru tests to ensure cluster is healthy"""
        pass

    def poll(self):
        """Main runtime of KafkaManager - handle incoming requests."""
        # Get topic handles
        in_topic = self.client.topics['kafka-manager-in']
        out_topic = self.client.topics['kafka-manager-out']
        # Subscribe consumer
        balanced_consumer = in_topic.get_balanced_consumer(
                                        consumer_group=self.consumer_grp,
                                        auto_commit_enable=True,
                                        zookeeper_connect=self.zkpr)
        # Continuously poll
        with out_topic.get_producer() as producer:
            for message in balanced_consumer:
                count = 0
                if message is not None:
                    print("Found msg <{}> @ offset {}".format(message.value,
                                                              message.offset))
                    function = message.value['function']
                    kwargs = message.value['kwargs']
                    _id = message.value['id']
                    kwargs = loads(kwargs)
                    if function in self.func_dict:
                        # Execute script with supplied key word args
                        output = self.func_dict[function](**kwargs)
                        # Post response
                        response = dumps({'function': function,
                                          'kwargs': dumps(kwargs),
                                          'output': output,
                                          'id': _id})
                        producer.produce(response, partition_key=str(count))
                    else:
                        print("Request function {} not found".format(function))
                else:
                    print("Found None msg")

    def _get_sh(self, name):
        """Returns shell script by string matching name."""
        if name in self.scripts:
            return os.path.join(self.kafka_home, self.scripts[name])
        else:
            print("{} script not found".format(name))
            return None

    def _run_sh(self, script, args):
        """Run kafka-topics.sh with the provided list of arguments.
           We quote(cmd) for safety.
        """
        script = self._get_sh(script)
        cmd = [script, '--zookeeper', self.zkpr] + args # might need to change
        cmd = ' '.join([str(c) for c in cmd]) # cmd needs to be str
        print("running: {}".format(cmd))
        return subprocess.check_output(quote(cmd))

    def list_topics(self):
        """Returns string formatted newline separated list of topics"""
        args = ['--list']
        response = self._run_sh('topics_sh', args)
        return response.strip().split(b'\n')

    def is_topic(self, topic):
        """Check if topic exists"""
        return topic in self.list_topics()

    def make_topic(self, 
                   topic, 
                   partitions=3, 
                   replication=None):
        """Use kafka-topics.sh to create a topic."""
        if not self.is_topic(topic):
            print("{} topic already exists".format(topic))
            return True
        else:
            print("Creating topic {}".format(topic_name))
            args = ['--create',
                   '--topic', topic_name,
                   '--partitions', num_partitions]
            if replication:
                args.extend(['--replication-factor', replication_factor])
            self._run_sh('topics_sh', args)
            sleep(0.5)
            return self.is_topic(topic)

    def delete_topic(self, topic):
        """Delete single topic by name"""
        print("Deleting topic {}".format(topic))
        args = ['--delete', '--topic', topic_name]
        self._run_sh('topics_sh', args)
        return self.is_topic(topic)

if __name__ == "__main__":
    print('Initializing KafkaManager')
    # Initialize
    kafka_manager = KafkaManager()
    # Start polling to handle requests
    kafka_manager.poll() 
    print('KafkaManager poll exit')