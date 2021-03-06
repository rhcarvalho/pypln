#-*- coding:utf-8 -*-
"""
Created on 28/09/11
by flavio
"""
__author__ = 'flavio'
__docformat__ = "restructuredtext en"


from pypln.stores.mongostore import conn,databases,collection
import zmq
from base import BaseSink

context = zmq.Context()

class MongoUpdateSink(BaseSink):
    """
    Sink to update documents in MongoDb
    """

    def start(self):
        """
        Apply update to Documents in any MongoDB collection
        expects a JSON message with the following structure:
        {"database":"mydb","collection":"mycolection","spec":{"_id":"some_id"},"update":{"$set":{"x":2}},"multi":False}
        spec is a dict or SON instance specifying elements which must be present for a document to be updated
        """
        num_tasks = int(self.hear.recv().split("|")[-1])
        # Process tasks forever
        print "Sink starting, waiting for %s tasks"%num_tasks
        total_results = 1
        for i in range(num_tasks):
            msg = self.receiver.recv_json()
            if 'fail' in msg:
                print "failed task #%s"%total_results
            else:
                self.process(msg)
            total_results += 1

        self.pub.send("sink-finished:%s"%total_results)
        print "==> sink-finished:%s"%total_results

    def process(self, msg):
        """
        Update documents in the database in batches of size
        self.batchsz
        """
        #FIXME: broken code: replace check below by try/except using explicit Exceptions from Pymongo
        if not (msg['database'] in databases and msg['collection'] in collections):
            print "Either database %s or collection %s do not exist."%(msg['database'],msg['collection'])
            return
        coll = conn[msg['database']][msg['collection']]
        try:
            coll.update(msg['spec'],msg['update'],multi=msg['multi'])
        except TypeError:
            print "bad spec or update command."
        except OperationFailure:
            print "failed updating document: %s"%t['_id']


if __name__=="__main__":
    S=MongoUpdateSink()
    S.start()
