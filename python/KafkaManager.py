import subprocess
from shlex import quote
from configparser import ConfigParser
from os import environ

__author__ = 'yazan'
__licence__ = 'Apache V2'

class KafkaManager(object):
    """Convenience interface to facilitate CLI interface with the host of a
    running kafka server.
    Since $KAFKA_HOME/bin scripts can only be run on the host, this class
    will constantly listen to topic <kafka-manager-in> and respond to requests
    such as creating topics, and so forth to topic <kafka-manager-out>. All 
    subscribers to these two topics receive all published messages.
    """
    def __init__(self):
        # Parse environment variables as DEFAULT configurations
        self.config = ConfigParser(environ)
        self.config.read(environ.get('KAFKA_MANAGER_CONFIG_DIR'))
        self.kafka_home = self.config.get('KAFKA_HOME')
        self.scripts = dict(self.config.items('kafka-cli'))
        self.zkpr = self.config.get('zookeeper', 'gateway')
        # Initialize <kafka-manager> topics
        self.make_topic(topic='kafka-manager-in')
        self.make_topic(topic='kafka-manager-out')
        # start polling to handle requests
        self.poll()

    def poll(self):
        while True:
            pass

    def fetch(self):
        pass

    def post(self):
        pass

    def _get_sh(self, name):
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
        args = ['--list']
        response = self._run_sh('topics_sh', args)
        return response.strip().split(b'\n')

    def is_topic(self, topic):
        """Check if topic exists"""
        return topic in self.list_topics()

    def get_topic(self, 
                  topic,
                  autocreate=True, 
                  partitions=3, 
                  replication=None):
        if not self.is_topic(topic):
            print("Topic not found: {}".format(topic))
            if autocreate:
                self.make_topic(topic, partitions, replication)
            else:
                return None
        return self.topics[topic]

    def make_topic(self, 
                   topic, 
                   partitions=3, 
                   replication=None):
        """Use kafka-topics.sh to create a topic."""
        if self.is_topic(topic):
            print("{} topic already exists".format(topic))
        else:
            print("Creating topic {}".format(topic_name))
            args = ['--create',
                   '--topic', topic_name,
                   '--partitions', num_partitions]
            if replication:
                args.extend(['--replication-factor', replication_factor])
            self._run_sh('topics_sh', args)
            time.sleep(1)

    def delete_topic(self, topic):
        """Delete single topic by name"""
        print("Deleting topic {}".format(topic))
        args = ['--delete', '--topic', topic_name]
        self._run_sh('topics_sh', args)