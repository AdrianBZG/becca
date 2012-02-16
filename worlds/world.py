'''
Created on Jan 11, 2012

@author: brandon_rohrer

The only methods that a world is required to implement are:

    step() -advances the world by one time step
    
    final_performance() -returns a performance value for the 
        agent in the world once the termination condition for the 
        world has been met

A number of methods for internal use have been found to be convenient as well:

    set_agent_parameters() -configures BECCA
        parameters specifically for the task at hand, when necessary

    display() -displays progress to the user

    log() -logs task progress and saves the current state of the world and 
        agent to disk
'''

import logging
import pickle

import numpy as np
#import matplotlib.pyplot as plt

class World(object):
    '''
    the base class for creating a new world
    '''

    def __init__(self):
        ''' default constructor
        '''


        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Initializing world ...')

        self.timestep = 0


        self.timestep = 0
        self.REPORTING_PERIOD = pow(10, 3)
        self.LIFESPAN = pow(10, 4)

        self.reward = 0

        self.cumulative_reward = 0
        self.reward_history = np.array([])

        self.display_features = False


        # initialise num_sensors, num_primitives and num_actions in subclass
        #self.num_sensors = 1
        #self.num_primitives = 1
        #self.num_actions = 1
        
        
    def load(self, pickle_filename):
        loaded = False
        try:
            with open(pickle_filename, 'rb') as world_data:
                self = pickle.load(world_data)
            self.logger = logging.getLogger(self.__class__.__name__)                
            self.logger.info('World restored at timestep ' + str(self.timestep))

        # otherwise initializes from scratch     
        except IOError:
            # world not found
            self.logger.warn("Couldn't open %s for loading" % pickle_filename)
        except pickle.PickleError, e:
            self.logger.error("Error unpickling world: %s" % e)
        else:
            loaded = True

        return loaded


    def save(self, pickle_filename):
        success = False
        try:
            with open(pickle_filename, 'wb') as world_data:
                # unset the logger before pickling and restore afterwards since it can't be pickled
                logger = self.logger
                del self.logger
                pickle.dump(self, world_data)
                self.logger = logger
            self.logger.info('world data saved at ' + str(self.timestep) + ' time steps')

        except IOError as err:
            self.logger.error('File error: ' + str(err) + ' encountered while saving data')
        except pickle.PickleError as perr: 
            self.logger.error('Pickling error: ' + str(perr) + ' encountered while saving data')        
        else:
            success = True
            
        return success
        
    

    def set_agent_parameters(self, agent):
        ''' sets parameters in the BECCA agent that are specific to a particular world.
        Strictly speaking, this method violates the minimal interface between the 
        agent and the world (observations, action, and reward). Ideally, it will 
        eventually become obselete. As BECCA matures it will be able to handle 
        more tasks without changing its parameters.
        '''
        pass

    
    def display(self):
        ''' provides an intuitive display of the current state of the World 
        to the user
        '''
        if (self.display_features):
            print('Display the world state: world timestep ' + str(self.timestep))
            
        if (np.mod(self.timestep, self.REPORTING_PERIOD) == 0):
            self.reward_history = np.append(self.reward_history, self.cumulative_reward)
            self.cumulative_reward = 0
            #plt.plot(self.reward_history)


    def log(self):
        ''' logs the state of the world into a history that can be used to
        evaluate and understand BECCA's behavior
        '''
        self.cumulative_reward += self.reward
                
    
    def step(self, action):
        ''' advances the World by one timestep.
        '''
        self.timestep += 1

        self.log()
        self.display()
 
        
    def final_performance(self):
        '''
        when the world terminates, this returns the performance 
        of the agent, a real value between -1 and 1. Before reaching
        the termination condition, it returns a value less than -1.
        Any terminating activities or reports should be included
        in this method too.
        '''
        if (self.timestep > self.LIFESPAN):
            performance = np.mean(self.reward_history[-3:]) / self.REPORTING_PERIOD
            #plt.ioff()
            #plt.show()
            
            assert(performance >= -1.)
            return performance
        
        return -2
    
