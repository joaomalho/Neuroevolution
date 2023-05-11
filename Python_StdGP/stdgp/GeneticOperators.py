from .Individual import Individual
from .Node import Node

# 
# By using this file, you are agreeing to this product's EULA
#
# This product can be obtained in https://github.com/jespb/Python-StdGP
#
# Copyright ©2019-2022 J. E. Batista
#

def tournament(rng, population, n):
	'''
	Selects "n" Individuals from the population and return a 
	single Individual.

	Parameters:

	population (list): A list of Individuals, sorted from best to worse.
	'''
	candidates = [rng.randint(0,len(population)-1) for i in range(n)]
	return population[min(candidates)]

def fit_tournament(rng, population, Sf, n_comp, first_tournament=True):
    '''
	Performs fit tournaments "Sf" times and return a list of
	winners of each.

	Parameters:

	population (list): A list of Individuals, sorted from best to worse.
    Sf (int): Number of fit tournaments to perform.
	n_comp (int): Number of random competitors per tournament.
	first_tournament (bool): Checks if size tournament is the first to be performed.
	'''
    if first_tournament:
        # list to store winners from Sf tournaments 
        candidates = [population[min([rng.randint(0, len(population)-1) for _ in range(n_comp)])] for _ in range(Sf)]
        # returning an ordered list of winners for second tournament by fitness (ascending)
        return sorted(candidates, key=lambda x: x.fitness)
    else:
        # performs one tournament with Sf random winners without replacement from first size tournament for diversity purposes
		# assumes ordered pop from best to worst 
        candidates = rng.sample([i for i in range(len(population))], Sf)
        return population[min(candidates)]

		

def size_tournament(rng, population, Sp, n_comp, first_tournament=True):
    '''
	Performs size tournaments "Sp" times and return a list of
	winners of each.

	Parameters:

	population (list): A list of Individuals.
    Sp (int): Number of size tournaments to perform.
	n_comp (int): Number of random competitors per tournament.
	first_tournament (bool): Checks if size tournament is the first to be performed.
	'''
	# ordering by size for tournament
    sorted_population = sorted(population, key=lambda x: x.size)
    
    if first_tournament:
        # list to store winners from Sp tournaments
        candidates = [sorted_population[min([rng.randint(0, len(population)-1) for _ in range(n_comp)])] for _ in range(Sp)]
        return sorted(candidates, key=lambda x: x.fitness) # sorted by fitness to enter fit_tournament function
    else:
        # performs one tournament with Sp random winners without replacement from first size tournament for diversity purposes
        # assumes ordered pop from best to worst 
        candidates = rng.sample([i for i in range(len(population))], Sp)
        return sorted_population[min(candidates)]

def double_tournament(rng, population, Sf, Sp, n_comp, switch=False):
    '''
    Implements Double Tournament Selection with Parsimony Tournament and Switch Phase.

    Parameters:
    
    population (list): A list of Individuals, sorted from best to worst.
    Sf (int): Tournament size for the first round based on fitness.
    Sp (int): Tournament size for the second round based on parsimony.
    switch (bool): A boolean indicating whether to perform the switch phase.
    '''
    # If switch is True, use size as primary criterion and fitness as secondary criterion
    if switch:
        assert (Sp >= Sf), "Sp needs to be higher than Sf"

        qualifiers = size_tournament(rng, population, Sp=Sp, n_comp=n_comp, first_tournament=True)
        parent = fit_tournament(rng, qualifiers, Sf=Sf, n_comp=n_comp, first_tournament=False)

    # If switch is False, use fitness as primary criterion and size as secondary criterion
    else:
        assert (Sf >= Sp), "Sf needs to be higher than Sp"
	
        qualifiers = fit_tournament(rng, population, Sf=Sf, n_comp=n_comp, first_tournament=True)
        parent = size_tournament(rng, qualifiers, Sp=Sp, n_comp=n_comp, first_tournament=False)
	
    return parent


def getElite(population,n):
	'''
	Returns the "n" best Individuals in the population.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	return population[:n]


def getOffspring(rng, population, tournament_size, double, Sf, Sp, Switch):
	'''
	Genetic Operator: Selects a genetic operator and returns a list with the 
	offspring Individuals. The crossover GOs return two Individuals and the
	mutation GO returns one individual. Individuals over the LIMIT_DEPTH are 
	then excluded, making it possible for this method to return an empty list.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	isCross = rng.random()<0.5

	desc = None

	if isCross:
		desc = STXO(rng, population, tournament_size, double, Sf, Sp, Switch)
	else:
		desc = STMUT(rng, population, tournament_size, double, Sf, Sp, Switch)

	return desc


def discardDeep(population, limit):
	ret = []
	for ind in population:
		if ind.getDepth() <= limit:
			ret.append(ind)
	return ret


def STXO(rng, population, tournament_size, double, Sf, Sp, Switch):
	'''
	Randomly selects one node from each of two individuals; swaps the node and
	sub-nodes; and returns the two new Individuals as the offspring.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	if not double:
		ind1 = tournament(rng, population, tournament_size)
		ind2 = tournament(rng, population, tournament_size)

	else: 
		ind1 = double_tournament(rng, population, Sf=Sf, Sp=Sp, n_comp=tournament_size, switch=Switch)
		ind2 = double_tournament(rng, population, Sf=Sf, Sp=Sp, n_comp=tournament_size, switch=Switch)

	h1 = ind1.getHead()
	h2 = ind2.getHead()

	n1 = h1.getRandomNode(rng)
	n2 = h2.getRandomNode(rng)

	n1.swap(n2)

	ret = []
	for h in [h1,h2]:
		i = Individual(ind1.operators, ind1.terminals, ind1.max_depth, ind1.model_name, ind1.fitnessType)
		i.copy(h)
		ret.append(i)
	return ret


def STMUT(rng, population, tournament_size, double, Sf, Sp, Switch):
	'''
	Randomly selects one node from a single individual; swaps the node with a 
	new, node generated using Grow; and returns the new Individual as the offspring.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	if not double:
		ind1 = tournament(rng, population, tournament_size)

	else: 
		ind1 = double_tournament(rng, population, Sf=Sf, Sp=Sp, n_comp=tournament_size, switch=Switch)

	h1 = ind1.getHead()
	n1 = h1.getRandomNode(rng)
	n = Node()
	n.create(rng, ind1.operators, ind1.terminals, ind1.max_depth)
	n1.swap(n)


	ret = []
	i = Individual(ind1.operators, ind1.terminals, ind1.max_depth, ind1.model_name, ind1.fitnessType)
	i.copy(h1)
	ret.append(i)
	return ret
