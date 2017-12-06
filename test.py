import random
from sklearn import svm
import sys
import math
import matplotlib.pyplot as plt

CONVERGENCE = 0.01
NUM_STATES = 10
NUM_TRANSITIONS = 3
NUM_FEATURES = 5
SIGMA = 20.0
EPSILON = 0.1
LEARNING_RATE = 0.1

def innerProduct(list1, list2):
    return sum(list1[i]*list2[i] for i in range(len(list1)))

def gaussianKernel(x, xk):
    return math.exp(-(innerProduct(x,x) - 2*innerProduct(x,xk) + innerProduct(xk,xk))/(2*SIGMA*SIGMA))

# Returns the random list of states that we use to test the system
def getListOfStates(numStates, numTransitions, sizeOfFeatureVector):
    states = []
    # Random reward generation for everything
    for _ in range(numStates):
        state = State(random.uniform(-1, 1)) # Sets reward of state
        states.append(state)
        # Initialize all state featureVectors at random
        state.featureVector = [random.randint(1, 100) for _ in range(sizeOfFeatureVector)]
    # Fully connected DAG, cause what the hell
    for i in range(numStates):
        state = states[i]
        for j in range(i):
            transition = Transition(state, sizeOfFeatureVector)
            states[j].transitions.append(transition)
    return states

def getUserWeights(model, sizeOfFeatureVector):
    weights = {}
    for state in model.states:
        for transition in state.transitions:
             weights[transition] = [random.randint(1, 100) for _ in range(sizeOfFeatureVector)]
    return weights

def main(argv):
    states = getListOfStates(NUM_STATES, NUM_TRANSITIONS, NUM_FEATURES)
    graph = GraphModel(states, states[0])

    user = User(getUserWeights(graph, NUM_FEATURES))

    # This is an online algorithm, so we only need to repeat until we've got some results to show
    runIterations = 50

    rewardLog = []

    for _ in range(runIterations):
        for state in graph.reverseTPS():
            state.expectationMaximization()

        userPath = user.getTraversal(graph.startState) # list of (state, action) tuples

        reward = 0.0
        for state, action in userPath:
            reward += state.reward
        state.observe(action)
        rewardLog.append(reward)
    plt.plot(rewardLog)
    plt.ylabel('reward over time')
    plt.show()


#class for creating User with optimal theta. User makes actions according to state and feature vector of state.
class User:
    def __init__(self, goldenWeights):
        self.goldenWeights = goldenWeights #map of transition to golden theta

    def getRandomAction(self, state):
        sumOfInnerProducts = 0
        fencePost=[]
        for action in range(len(state.transitions)):
            product = gaussianKernel(state.featureVector, self.goldenWeights[state.transitions[action]])
            sumOfInnerProducts += product
            fencePost.append(sumOfInnerProducts)

        dart = random.random()*sumOfInnerProducts;
        for x in range(len(fencePost)):
            if fencePost[x] > dart:
                return x;

        assert (False);

    def getTraversal(self, startState):
        currentState = startState;
        path = []; #list of (state, action)
        while not currentState.isTerminal():
            action = self.getRandomAction(currentState);
            path.append((currentState,action));
            currentState = currentState.transitions[action].nextState;
        return path;


class State:
    def __init__(self, reward):
        self.transitions = []
        self.featureVector = []
        self.numFeatures = None
        self.reward = reward
        self.expectedValue = 0.0

    def getFeatures(self):
        return self.featureVector

    def isTerminal(self):
        return len(self.transitions) == 0

    def observe(self, action):
        for i in range(len(self.transitions)):
            self.transitions[i].observe(self.featureVector, 1.0 if i == action else 0.0)

    def recalculateReward(self):
        self.reward = self.expectedValue

    def expectationMaximization(self):
        if random.uniform(0,1) > EPSILON and len(self.transitions) > 0:
            self.featureVector = [0 for _ in range(len(self.featureVector))]
        lastSumSquaredError = -1
        adaGrad = [0 for _ in range(len(self.featureVector))]
        while True:
              sumVector = [0 for _ in range(len(self.featureVector))]
              for transition in self.transitions:
                  # dualCoef = y*alpha
                  for (supportVector, dualCoef) in transition.supportVectors:
                      scaleFactor = dualCoef * gaussianKernel(supportVector, self.featureVector) * 1.0 # transition.nextState.reward
                      for x in range(len(sumVector)):
                          sumVector[x] += scaleFactor * (supportVector[x] - self.featureVector[x]) / (SIGMA*SIGMA)
              for i in range(len(sumVector)):
                  if sumVector[i] != 0:
                      adaGrad[i] += sumVector[i]*sumVector[i]
                      self.featureVector[i] -= sumVector[i] * LEARNING_RATE / math.sqrt(adaGrad[i])
              sumSquaredError = innerProduct(sumVector, sumVector)
              deltaError = lastSumSquaredError - sumSquaredError
              lastSumSquaredError = sumSquaredError
              print ('numtransitions '+str(len(self.transitions)))
              print ('error '+str(sumSquaredError))
              print ('delta '+str(sumVector))
              print ('feature '+str(self.featureVector))
              if deltaError >= 0 and deltaError < CONVERGENCE:
                  break
        else:
            self.featureVector = [random.randint(1,100) for _ in range(len(self.featureVector))]
    self.recalculateReward()

class Transition:
    def __init__(self, nextState, numFeatures):
        self.nextState = nextState
        self.observationsX = []
        self.observationsY = []
        self.clf = svm.SVR(kernel='rbf',gamma=(1/(SIGMA*SIGMA)))
        self.supportVectors = []

    def observe(self, x, taken):
        self.observationsX.append(x)
        self.observationsY.append(taken)
        self.clf.fit(self.observationsX, self.observationsY)
        self.supportVectors = []
        for i in range(len(self.clf.support_vectors_)):
            self.supportVectors.append((self.clf.support_vectors_[i], self.clf.dual_coef_[0][i]))

class GraphModel:
    def __init__(self, states, startState):
        self.states = states #list of the states
        self.startState = startState

    def reverseTPS(self):
        statesVisited = []
        while len(statesVisited) < len(self.states):
            for state in self.states:
                count = len(filter(lambda x: x.nextState in statesVisited, state.transitions))
                if count == 0:
                    statesVisited.append(state)
        return statesVisited

if __name__ == "__main__":
    main(sys.argv)
