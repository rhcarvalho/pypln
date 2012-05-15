#-*- coding:utf-8 -*-
"""
Basic application setup classes
"""
__docformat__ = "restructuredtext en"
__author__ = 'fccoelho'

from multiprocessing import Process, ProcessError
import nmap




class TaskVentilator(object):
    """
    Class that sets up a task ventilator pattern
    """
    def __init__(self,ventilator_class,worker_class,sink_class,nw,ports={}):
        """
        Starts all the processes necessary for the ventilator pattern.

        :param ventilator_class: Class which will serve as ventilator.
        :param worker_class: Class which will serve as workers
        :param sink_class: Class which will serve as  sink
        :param nw: Number of workers
        :param ports: Dictionary with ports for all processes: {'ventilator':(pushport,pubport,subport),
        'worker':(pushport,pullport,subport),
        'sink':(pullport,pubport,subport)}
        :return: None
        """
        if not ports:
            ports = self.find_ports()
        self.ventilator = ventilator_class(pushport=ports['ventilator'][0],pubport=ports['ventilator'][1],subport=ports['ventilator'][2])
        self.workers = [worker_class(pushport=ports['worker'][0],pullport=ports['worker'][1],subport=ports['worker'][2]) for i in xrange(nw)]
        self.sink = sink_class(pullport=ports['sink'][0],pubport=ports['sink'][1],subport=ports['sink'][2])

    @classmethod
    def find_ports(self, range=(5500,5600)):
        """
        Generate port set for this pattern by searching available ports
        :param range: tuple with range of ports to search
        :return: Dictionary with ports for all processes: {'ventilator':(pushport,pubport,subport),
        'worker':(pushport,pullport,subport),
        'sink':(pullport,pubport,subport)}
        """
        nm = nmap.PortScanner()
        nm.scan('127.0.0.1', '%s-%s'%range)
        allp = nm['127.0.0.1'].all_protocols()
        openports = {} if 'tcp' not in allp else nm['127.0.0.1'][tcp]
        ports = {}
        ports


        ports = {'ventilator':(5557,5559,5559), # pushport,pubport,subport
             'worker':(5564,5561,5563),          # pushport,pullport,subport
             'sink':(5564,5563,5562)   # pullport,pubport,subport
    }

    def spawn(self):
        """
        Start the subprocesses.

        :return: (ventilator,[w1,w2,...,wn],sink) All but ventilator are Process objects
        """
#        v= Process(target=self.ventilator, name="ventilator")
        w =[Process(target=w,name="worker-%d"%i) for i,w in enumerate(self.workers)]
        [p.start() for p in w]
        s = Process(target=self.sink,name="sink")
        s.start()
        return self.ventilator,w,s