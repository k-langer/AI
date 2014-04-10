#!/usr/bin/python

#Kevin Langer
# A2 - CS4100
# Wumpus

# Regex for parsing 
import re
# For opening prover9
import subprocess
# For command line args
import sys

#Global Score Keep
scream = False
score = 0
haveArrow = True
prover9Path = "" 

#At a given cell, grab gold
#Check aginst unknown world
#Change gold value to 2, to prevent repicking up same gold
def grabGold(world,cell):
    if world[cell[0]-1][cell[1]-1]['gold'] == 1:
        world[cell[0]-1][cell[1]-1]['gold']=2
        print "Gold procured at",cell
        global score 
        score += 1000
        return True
    #print "Agent failed to pick up gold"
    return False
#At a given 'location', shoot arrow
#Predictied at 'cell'
#Verify prediciton and facing against unkown 'world'
def shootArrow(world,cell,location):
    global score
    global scream
    global haveArrow
    if not haveArrow:
        return scream
    haveArrow = False
    scream = 1 
    score -= 100
    direction = getFacing(cell,location)
    if ( world[cell[0]-1][cell[1]-1]['wumpus'] == 1 and location[direction] == cell[direction]):
        print "Wumpus killed and Scream Heard"
        world[cell[0]-1][cell[1]-1]['wumpus'] = 2
        scream = True
        return True
    print "Wumpus not killed"
    return False
#Only method used to move around the world
#w_map is unkown map, squares here are uncovered ONLY WHEN moved to
#a_map is agent's known map
# a_to is location from which the agent moves
# a_from is location from which the agent comes from
#NOTE: If agent attempts to move to its current spot, it will not be deducted score
#NOTE: This is where the agent can die from walking into a pit or wumpus
def goToOnMap(w_map,a_map,  a_from, a_to):
    oldCell = w_map[a_from[0]-1][a_from[1]-1]
    if a_to == a_from:
        return oldCell
    oldCell["agent"] = 0
    newCell = w_map[a_to[0]-1][a_to[1]-1]
    if newCell["pit"] == 1 or (newCell["wumpus"] == 1 and not scream):
        print a_to
        print "Agent has died!!!"
        raise NameError('Agent has died due to failed inference')
    newCell["agent"] = 1
    newCell["visited"] = 1
    newCell["Safe"] = 1
    a_map[a_to[0]-1][a_to[1]-1] = newCell
    global score
    score -= 1
    print "Agent moved from",a_from," to ",a_to
    return newCell
#Generic method for submiting any proof to Prover9
# Path to prover9
# formulas to prove
def prover9(formulas):
    if not prover9Path:
        path = "prover9"
    else:
        path = prover9Path
    options = "set(binary_resolution).\n"+\
    "clear(print_initial_clauses).\n"+\
    "clear(print_kept).\n"+\
    "clear(print_given).\n"+\
    "assign(max_seconds,10).\n"+\
    "assign(stats,none).\n"
    #print formulas
    p = subprocess.Popen(path, shell=True, stdin=subprocess.PIPE, \
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(options + formulas)
    (inpt, errpt) = p.communicate()
    try:
        p.kill()
    except OSError:
        pass
    if "THEOREM PROVED" in inpt:
        return 1
    return 0
# Method used to create an empty world map
# world map is a two demensional array of dicts
# Each dict uses hashes to store items in a cell
# Way more flexible than tuples at minimial hit to efficency     
def init_map(wumpus_map,field, know):
    wumpus_map = [[0 for x in xrange(field[2])] for x in xrange(field[1])] 
    numcols = len(wumpus_map)
    numrows = len(wumpus_map[0])
    for j in xrange(numrows):
        for i in xrange(numcols):
            wumpus_map[i][j] = {}
            modify = wumpus_map[i][j]
            modify['agent'] = 0
            modify['gold'] = 0
            modify['Goal'] = 0
            modify['pit'] = 0
            modify['wumpus'] = 0 
            modify['visited'] = 0
            modify['Safe'] = 0
            modify['cor'] = (i+1,j+1) 
            if (know):
                modify['breeze'] = -1
            else:
                modify['breeze']=0
            if (know):
                modify['stench'] = -1
            else: 
                modify['stench'] = 0
    return wumpus_map
# Choose what items in a cell are relevant for display
# on the world map display representaiton 
# As a cell in a world map can hold anything arbitrary
# this is needed to make sure the map display doesn't get 
# out of control
def valid_display(v_str):
    if (v_str == "agent" or \
        v_str == "breeze"or \
        v_str == "gold"  or\
        v_str == "Goal"  or\
        v_str == "pit"   or\
        v_str == "stench"or\
        v_str == "wumpus"or\
        v_str == "visited"):
            return 1
# Fill wumpus_map with unknown/hidden info
# Fill agent_map with known info (agent loc, goal, and map size)
# qu(eue) of items to fill. Done this way, because map size could be anywhere
# in the input file. But I cannot start adding items until the map is created
def fill_map(wumpus_map,agent_map,qu):
    for item in qu:
        modify = wumpus_map[item[1]-1][item[2]-1]
        a_modify = agent_map[item[1]-1][item[2]-1]
        if (item[0] == "A"):
            modify['agent'] = 1
            modify['visited'] = 1
            modify['Safe'] = 1
            agent_map[item[1]-1][item[2]-1] = modify
        elif (item[0] == "B"):
            modify['breeze'] = 1
        elif (item[0] == "G"):
            modify['gold'] = 1
        elif (item[0] == "GO"):
            modify['Goal'] = 1
            #agent_map[item[1]-1][item[2]-1] = modify
        elif (item[0] == "P"):
            modify['pit'] = 1
        elif (item[0] == "S"):
            modify['stench'] = 1
        elif (item[0] == "W"):
            modify['wumpus'] = 1
        else: 
            print "ERROR"
# Print a text representaiton of any wumpus map item
def print_map(w_map):
    numcols = len(w_map)
    numrows = len(w_map[0])
    for j in xrange(numrows):
        for i in xrange(numcols):
            cell = w_map[i][numrows-j-1]
            for key, value in cell.items():
                if(value == 1 and valid_display(key)):
                    print key[0],
                else:
                    print " ",
            print "|",
        print ""
# Parse the file wumpus_world.txt into two maps 
# agent map and wumpus map
def parse():
    f = open('wumpus_world.txt')
    field = []
    wumpus_map = []
    agent_map = []
    build_qu = []
    for line in f:        
        is_match = re.match(r"^([a-zA-Z]+)(\d+),(\d+)",line)
        if is_match:
            field = is_match.group(1),int(is_match.group(2)),int(is_match.group(3))
            if field[0]=="M":
                wumpus_map = init_map(wumpus_map,field,1)
                agent_map = init_map(agent_map,field,0)
            else:
                build_qu.append(field)
            continue
        is_match = re.match(r"^([a-zA-Z]+)(\d)(\d)",line)
        if is_match:
            field = is_match.group(1),int(is_match.group(2)),int(is_match.group(3))
            if field[0]=="M":
                wumpus_map = init_map(wumpus_map,field,1)
                agent_map = init_map(agent_map,field,0)
            else:
                build_qu.append(field)
    fill_map(wumpus_map,agent_map,build_qu)
    f.close()
    return wumpus_map,agent_map
#Return adjacent cors to any single point. Not in formal (prover9) notation
def adjacent(w_map, x,y):
    adj = set()
    r_x = x-1
    r_y = y-1
    cor = ""
    if (r_x -1 >= 0):
        cor = '[' + str(x-1) + ',' + str(y) + ']'
        adj.add(cor)
    if (r_y-1 >= 0):
        cor = '[' + str(x) + ',' + str(y-1) + ']'
        adj.add(cor)
    if (r_x + 1 < len(w_map)):
        cor = '[' + str(x+1) + ',' + str(y) + ']'
        adj.add(cor)
    if (r_y + 1 < len(w_map[0])): 
        cor = '[' + str(x) + ',' + str(y+1) + ']'
        adj.add(cor)
    return adj
#Turn any real cordinate into a formal cordinate
def toCor(x,y):
    return '[' + str(x) + ',' + str(y) + ']'
perm_adj = ""
#return all adjacent rules in a given map. 
#NOTE: in formal prover9 format
def all_adjacent(w_map):
    global perm_adj
    if not perm_adj:
        adj_KB = "% Adjacent rules\n"
        numcols = len(w_map)
        numrows = len(w_map[0])
        for j in xrange(numrows):
            for i in xrange(numcols):
                cor = adjacent(w_map,i+1,j+1)
                for each in cor:
                    adj_KB += "adjacent(" + toCor(i+1,j+1) + "," + each + "). "
                adj_KB += "\n"
        perm_adj = adj_KB
    return perm_adj
# Return any notAdjacent square to a specific cor
# Used to prove existance of wumpus
#Given in formal prover9 format
def notAdjacent(agent_map, cor):
    numcols = len(agent_map)
    numrows = len(agent_map[0])
    no_adj = ""
    for j in xrange(numrows):
        for i in xrange(numcols):
            if (i > cor[0]+1 or i < cor[0]-1 or j > cor[1]+1 or j < cor[1]-1):
                no_adj += "-adjacent([" + str(cor[0]+1) + \
                    "," + str(cor[1]+1) + "],[" + str(i+1) + \
                    "," + str(j+1)  + "]). "
    return no_adj + "\n"
# Compile the agent's knowlege base
# Add additional rules to prove a wumpus (findingWumpus)
# Because of the lack of math operations in prover9, this required
# hard coding both -adjacent() and adjacent() into the KB. 
# This means that it is best to seperate finding safe squares
# and finding wumpuses 
# Also allows scream to be added to KB if there is a confirmed wumpus kill!
def all_agentKB(agent_map,scream,findingWumpus):
    agen_KB = "% Agent's KB\n"
    if findingWumpus:
        # Additional rule used for finding wumpus
        agen_KB += "stench(x) & -adjacent(x,y) -> -wumpus(y).\n"
    numcols = len(agent_map)
    numrows = len(agent_map[0])
    wumpus = ""
    if (scream):
        agen_KB += "scream(1).\n"
    # check all cells
    for j in xrange(numrows):
        for i in xrange(numcols):
            nl = '' 
            cell = agent_map[i][j]
            for key, value in cell.items():
                # Add visited rules
                if (key == "visited" and value == 1):
                    nl = '\n'
                if key== "wumpus" and value == 1 and not findingWumpus:
                    continue
                if (findingWumpus and key == "stench" and value == 1):
                    wumpus += notAdjacent(agent_map,(i,j))
                    # Encode not adjacent information 
                    # Provide implied stench
                    wumpus +=  "stench(" + toCor(i+1,j+1) + " ) -> "
                    first = True
                    for cor in rawAdjacent(agent_map, (i+1,j+1)):
                        if first:
                            wumpus+= "wumpus(" + toCor(cor[0]+1,cor[1]+1) + ")"
                            first = False
                        else:
                            wumpus+= " | " + "wumpus(" + toCor(cor[0]+1,cor[1]+1) + ")"
                    wumpus += ".\n"
                # Encode all other valid_display information about square
                # NOTE: some of this is irrelevant info, but none contridictory
                if(value==1 and valid_display(key) ):
                    agen_KB += key + '(' + toCor(i+1,j+1) + '). '
                elif(value==-1):
                    agen_KB += '-' + key + '(' + toCor(i+1,j+1) + '). '
            agen_KB += nl
    agen_KB += wumpus
    return agen_KB
# Rules that get called on every prover9 proof. Just a static string
# NOTE: these are not the only prover9 rules, just the ones that are common
def staticRules():
    rules = "% Static FOL rules\n"
    rules += "(pit(x) & adjacent(x,y)) -> breeze(y).\n"+ \
            "(wumpus(x) & adjacent(x,y)) -> stench(y).\n"+ \
            "visited(x) -> (-pit(x) & -wumpus(x)).\n"+ \
            "(-pit(x) & -wumpus(x)) -> safe(x).\n"+\
            "(scream(x) & (wumpus(y) | stench(y))) -> safe(y).\n"+\
            "-stench(x) & adjacent(x,y) -> -wumpus(y).\n"+\
            "% Below are only inlucded with finding wumpus.\n" + \
            "% stench(x) & -adjacent(x,y) -> -wumpus(y).\n" 
    return rules
# Check all squares for safety.
# Only gets called after a wumpus death, otherwise
# checking just adjacent squares is MUCHHHHHH faster
# uses prover9
def prover9_checkAllSquares(agent_map,scream):
    numcols = len(agent_map)
    numrows = len(agent_map[0])
    for j in xrange(numrows):
        for i in xrange(numcols):
            cell = agent_map[i][j]
            for key, value in cell.items():
                if (key == "Safe" and value == 0):
                    prove = prover9("formulas(sos).\n"+ \
                    all_adjacent(agent_map) + \
                    all_agentKB(agent_map,scream,False) + \
                    staticRules() + "end_of_list.\n" + 
                    "formulas(goals).\nsafe(" + toCor(i+1,j+1) + ").\n" + \
                    "end_of_list.\n") 
                    if prove:
                        cell = agent_map[i][j]
                        cell["Safe"] = 1
# Check for safe squares adjacent to loc
# Use prover9 to verify all these adjacent squares
# save safety back into the cell on the wumpus map  
def prover9_safeSquares(agent_map,scream,loc):
    for cell in rawAdjacent(agent_map, loc):
        i = cell[0]
        j = cell[1]
        if agent_map[i][j]["Safe"] == 0:
            prove = prover9("formulas(sos).\n"+ \
            all_adjacent(agent_map) + \
            all_agentKB(agent_map,scream,False) + \
            staticRules() + "end_of_list.\n" + 
            "formulas(goals).\nsafe(" + toCor(i+1,j+1) + ").\n" + \
            "end_of_list.\n") 
            if prove:
                cell = agent_map[i][j]
                cell["Safe"] = 1
# Check ALL squareas for a wumpus, only called after stench is felt
# and before the wumpus is killed. By far the slowest method in the
# program
def prover9_wheresWumpus(agent_map):
    numcols = len(agent_map)
    numrows = len(agent_map[0])
    for j in xrange(numrows):
        for i in xrange(numcols):
            cell = agent_map[i][j]
            for key, value in cell.items():
                if (key == "Safe" and value == 0):
                    prove = prover9("formulas(sos).\n"+ \
                    all_adjacent(agent_map) + \
                    all_agentKB(agent_map,False,True) + \
                    staticRules() + "end_of_list.\n" + 
                    "formulas(goals).\nwumpus(" + toCor(i+1,j+1) + ").\n" + \
                    "end_of_list.\n") 
                    if prove:
                        cell = agent_map[i][j]
                        cell["wumpus"] = 1
                        return cell
                        #print toCor(i+1,j+1)
    return ""
# Returns the cost of moving from one square to another
# Same square=0
# adjacent(square)=1
# -adjacent(square)>1
# Is manhattan distance
def heuristicCostEstimate(cor_to,cor_from):
    return (abs(cor_to[0]-cor_from[0])+abs(cor_to[1]-cor_from[1]))

# Given a cordinate, return the likely closest safe square based on the 
# manhattan distance between the two cells
def goalHeuristic(agent_map,agent_cor):
    x = agent_cor[0]
    y = agent_cor[1]
    numcols = len(agent_map)
    numrows = len(agent_map[0])
    minDis = numcols*numrows
    minCell = ()
    for j in xrange(numrows):
        for i in xrange(numcols):
            cell = agent_map[i][j]
            if (cell["Safe"] == 1 and cell["visited"] == 0):
                dis = heuristicCostEstimate((i,j),(x,y))
                if ( dis < minDis):
                    minDis = dis
                    minCell = (i+1,j+1)
    return minCell
# Return adjacent squares in world format
# Basicall the same as previous all adjacent, just not 
# in formal prover9 format
def rawAdjacent(w_map, i_cor):
    adj = set()
    r_x = i_cor[0]-1
    r_y = i_cor[1]-1
    cor = ""
    if (r_x -1 >= 0):
        cor = (r_x-1,r_y)
        adj.add(cor)
    if (r_y-1 >= 0):
        cor = (r_x,r_y-1)
        adj.add(cor)
    if (r_x + 1 < len(w_map)):
        cor = (r_x+1,r_y)
        adj.add(cor)
    if (r_y + 1 < len(w_map[0])): 
        cor = (r_x,r_y+1)
        adj.add(cor)
    return adj
# Astar algorithm adapated from wikipedia pseudocode
# Modifications are used to suit this problem (only go to safe squares)
# Used python sets and dicts
# NOTE: watching graph search at work is like watching magic
def Astar(world,start,goal):
    g_score = {}
    f_score = {}
    came_from = {} 
    closedset = set()
    openset = set()
    openset.add(start)
    g_score[start] = 0
    f_score[start] = g_score[start] + heuristicCostEstimate(start,goal)
    while openset:
        current = min(f_score,key=f_score.get)
        if current == goal:
            return Astar_path(came_from,current)
        closedset.add(current)
        openset.remove(current)
        del f_score[current]
        neighbors = rawAdjacent(world,current)
        for sq in neighbors:
            neighbor = (sq[0]+1,sq[1]+1)
            cell = world[sq[0]][sq[1]]
            if (cell["Safe"] == 1):
                if neighbor in closedset:
                    continue
                tentative_g_score = g_score[current] + 1
                if neighbor not in openset or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] +heuristicCostEstimate(neighbor,goal)
                    if neighbor not in openset:
                        openset.add(neighbor)
    return "fail"
#Astar path algorithm written from the ground up to be itterative instead of recursive
def Astar_path(came_from, current_node):
    node = current_node
    l = []
    while node in came_from:
        l.append(node)
        node = came_from[node]
    l.reverse()
    return l
# Return hte agent location in formal cordinates suitable for prover9
def getAgentLoc(world):
    numcols = len(world)
    numrows = len(world[0])
    for j in xrange(numrows):
        for i in xrange(numcols):
            nl = '' 
            cell = world[i][j]
            if (cell['agent'] == 1):
                return (i+1,j+1)
    raise NameError('Agent Location Not Defined')
    return 0
# Just return the known goal in the world
# NOTE: The agent MUST BE ABLE to get to the goal or an exception WILL be thrown
def getGoal(world):
    numcols = len(world)
    numrows = len(world[0])
    for j in xrange(numrows):
        for i in xrange(numcols):
            nl = '' 
            cell = world[i][j]
            if (cell['Goal'] == 1):
                return (i+1,j+1)
    raise NameError('Goal not  Defined')
    return 0
# Get facing before shooting the wumpus
def getFacing(cell,location):
    if(cell[1] > location[1]):
        print "Face North at",location
        return 0
    if (cell[1] < location[1]):
        print "Face South at",location
        return 0
    if (cell[0] > location[0]):
        print "Facing East at",location
        return 1
    if (cell[0] < location[0]):
        print "Face West at", location
        return 1
# After a wumpus is deduced, travel to a square where it can be shoot
# (because it is possible to deduce a wumpus when agent(x) & -adjacent(x,y) -> wumpus(y)
# e.g: prediction([*,y]) or prediction([x,*]) (use heuristic to find closest)
# Send this to game engine and check if it hit
# After a hit it is a good idea to refresh ALL safe squares. As a max of 4 will appear
def shootWumpus(world,agent_world,prediction,location):
    numcols = len(world)
    numrows = len(world[0])
    goal = 0 
    cell = prediction['cor']
    goalCost = numcols*numrows
    print "deduced wumpus at",cell
    for x in xrange(numrows):
        if agent_world[cell[0]-1][x]['Safe'] == 1:
            temp = heuristicCostEstimate( (cell[0],x+1) ,location)
            if (temp < goalCost):
                goalCost = temp
                goal = (cell[0],x+1)
    for x in xrange(numcols):
        if agent_world[x][cell[1]-1]['Safe'] == 1:
            temp = heuristicCostEstimate( (x+1,cell[1]) ,location)
            if (temp < goalCost):
                goalCost = temp
                goal = (x+1,cell[1])
    while location != goal:
        moveTo = Astar(agent_world,location,goal)
        goToOnMap(world,agent_world,location,moveTo[0])
        location = moveTo[0]
    outcome =  shootArrow(world,cell,location)
    prover9_checkAllSquares(agent_world,outcome)    
    return outcome
# Run the game
def play(world,agent_world):  
    global scream
    # Start the agent at the start location, get safe squares from there
    start = getAgentLoc(agent_world)
    prover9_safeSquares(agent_world,False,start)
    goal = goalHeuristic(agent_world,start) 
    current_loc = start
    stenches = 0
    steps = 0
    #No negative effects for speculatively grabbing gold
    # As a result, do it here. Just incase the Agent has no where to go
    grabGold(world,start) 
    # Run loop while there are still unexplored safe squares
    while goal:
        steps += 1
        moveTo = Astar(agent_world,current_loc,goal)
        precepts = goToOnMap(world,agent_world,current_loc,moveTo[0])
        current_loc = moveTo[0]
        #print_map(agent_world)
        if precepts["stench"] == 1:
            print "Stench at",current_loc
            stenches+=1
        if precepts["breeze"] == 1:
            print "Breeze at",current_loc
        if precepts["gold"] == 1:
            grabGold(world,current_loc)
        if stenches and not scream:
            predicted_wumpus = prover9_wheresWumpus(agent_world)
            if predicted_wumpus:
                scream = shootWumpus(world,agent_world,predicted_wumpus,current_loc)
        prover9_safeSquares(agent_world,scream,current_loc)
        goal = goalHeuristic(agent_world,current_loc)
    goal = getGoal(world)
    if not goal:
        # Raise exception if the agent can't get to goal
        raise NameError('Goal not reachable')
    print "Agent belives it has explored all safe squares, seeks goal"
    #Go to goal after all safe spaces are exaushted
    while current_loc != goal:
        steps += 1
        moveTo = Astar(agent_world,current_loc,goal)
        goToOnMap(world,agent_world,current_loc,moveTo[0])
        current_loc = moveTo[0]
    print "Score: ",score
# Lets dump the FOL KB to a file for debugging outside of python
def saveFOLKB(KB):
    kb_str = "% Below is entire FOL KB\n" + \
            "% Note this includes both finding wumpus and safe squares\n" + \
            "% These things are very different! The rules are run seperately in this program\n" + \
            "% But are presented here, together, as reference\n"
    kb_str += KB
    f = open("FOL.p9", "w")
    f.write(kb_str)
    f.close()
# Parse the file, run the game, dump the FOL rules to a file
def main():
    global prover9Path
    if len(sys.argv)-1:
        prover9Path = sys.argv[1]
    (world,agent_world) = parse()
    play(world,agent_world)
    saveFOLKB(all_adjacent(world) + \
        staticRules() + \
        all_agentKB(agent_world,True,True))
    print "Final Map:"
    print_map(agent_world)
if __name__ == "__main__":
    main()
