# -*- coding: utf-8 -*-
"""FinalEvaluation

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VXM7HwVvSVw-shXj5DkFNtofDdaWPNvQ
"""

# This is the final evaluation notebook. 
# DONE:
# (1) Tree construction for conditionals
# (2) Facts simplification and adding their truth values in vardict
# (3) Question processing to get the variables in question into quesVars
# (4) Conditional Tree evaluation and truth values updated in vardict
# (5) Evaluate question Tree 
# TO DO:
# (1) Tree construction for question  (done by model)

class Et:

	def __init__(self , value):
		self.value = value
		self.left = None
		self.right = None
		self.parent = None
		self.expression = None # unused
		self.truth = None
		self.visited = False

def isOperator(c):
	if (c == 'v' or c == '^' or c == '-' or c == '~'):
		return True
	else:
		return False

def inorder(t):
	if t is not None:
		if (t.value == '~'):
			print(t.value, end = " ")
			inorder(t.left)
		else:
			inorder(t.left)
			print(t.value, end = " ")
			inorder(t.right)

# Returns root of constructed tree for
# given postfix expression
def constructTree(postfix , vardict):
	stack = []

	# Traverse through every character of input expression
	for char in postfix :
		# if operand, simply push into stack
		if not isOperator(char):
			t = Et(char)
			t.expression = char
			if(char not in vardict):
				vardict[char] = [None , []]
				
			vardict[char][1].append(t)
		# Operator
		elif (char.strip() == '~'):
			t = Et(char)
			t1 = stack.pop()
			t.left = t1
			t1.parent = t
			t.expression = char + t1.expression
		else:
			# Pop two top nodes
			t = Et(char)
			t1 = stack.pop()
			t2 = stack.pop()
			
			# make them children
			t.right = t1
			t.left = t2
			
			t1.parent = t
			t2.parent = t

			t.expression = t2.expression + char + t1.expression
		# Add this subexpression to stack
		stack.append(t)
		# for i in list(stack):
		# 	print(i.value , end="")
		# print()
	# Only element will be the root of expression tree
	t = stack.pop()
	
	return t

def quesProcessing(questions , quesVars):
  for ques in questions:
    quesVars.append([])
    for char in ques:
      if not (isOperator(char.strip())):
        quesVars[-1].append(char)
    
def simplifyFact(fact , finalFacts):
  for part in fact.split('^'):
    finalFacts.append(part.strip())

def factProcessing(facts , finalFacts):
  for fact in facts:
    if ('^' in fact and 'v' not in fact):
      simplifyFact(fact , finalFacts)
    elif ('v' in fact):
      pass
    else:
      finalFacts.append(fact.strip())

def evaluateFacts(finalFacts , vardict , knownVars):
  for fact in finalFacts: 
    if len(fact) == 1: # true value 
      if (fact in vardict):
        vardict[fact][0] = True
      else:
        vardict[fact] = [True , []]
      knownVars.append(fact)
    else:
      temp = fact.replace("~" , "")
      if (temp in vardict):
        vardict[temp][0] = False
      else:
        vardict[temp] = [False , []]
      knownVars.append(temp)

# check if ques has unknown vars
def unknownQuesVars(quesVars, vardict):
  for ques in quesVars:
    if isUnknownQuesVars(ques , vardict):
      return True
  return False

def isUnknownQuesVars(ques , vardict):
  for var in ques:
    if(var not in vardict):
      return True
    if(vardict[var][0] is None):
      return True
  return False

def evalMain(vardict , knownVars , quesVars):
  # assumes vardict has truth values of fact variables
  # knownvars: list of the fact variables
  for var in knownVars:
    outer_dfs(var, vardict, vardict[var][0] , quesVars)

    
def outer_dfs(var, vardict, truth , quesVars,  node=None):
    if not (unknownQuesVars(quesVars, vardict)):
      return
    
    if isOperator(var):
      dfs(node, vardict , quesVars)
    
    else:
      vardict[var][0] = truth
      nodelist = vardict[var][1]
      #print("hello")
      for node in nodelist:      
        node.truth = truth 
        if(node.visited == False):
          dfs(node, vardict , quesVars)
  

def dfs(node, vardict , quesVars):
  
  is_op = isOperator(node.value)
  
  if(node.visited == False ): # IT SHOULDNT BE VISITED AGAIN
    
    node.visited = True

    if(not(is_op)): #operand
      if (node.parent and canSetNode(node.parent)):
        dfs(node.parent, vardict , quesVars)
      else:
        return
    
    else: # operator
      trySettingChildren(node) # conditions for operators
      if node.left.truth is not None:
        outer_dfs(node.left.value, vardict, node.left.truth , quesVars , node.left)
      if node.right is not None and node.right.truth is not None:
        outer_dfs(node.right.value, vardict, node.right.truth , quesVars , node.right)
      if node.parent is not None and isOperator(node.parent.value):
        if (node.parent and canSetNode(node.parent)):
          dfs(node.parent, vardict , quesVars)
      


def trySettingChildren(node):
    
    left = node.left
    right = node.right
    
    if node.value == '-':
        if right.truth == False:
          left.truth = False
        elif left.truth == True:
          right.truth = True

    elif node.value == '~':
        left.truth = not (node.truth)        
    
    elif node.value == '^':
        if node.truth == True:
           left.truth = right.truth = True
        elif node.truth == False:
            #print("in and" , node.left.value, node.left)
            if left.truth == True:
              right.truth = False
            elif right.truth == True:
              left.truth = False 

    # elif node.value == '^' and node.truth == True:
    #     left.truth = right.truth = True
    
    elif node.value == 'v':
        if node.truth == False:
           left.truth = right.truth = False
        elif node.truth == True:
            if left.truth == False:
              right.truth = True
            elif right.truth == False:
              left.truth = True
        
    # elif node.value == 'v' and node.truth == False:
    #     left.truth = right.truth = False       
         

def canSetNode(node):

    left = node.left
    right = node.right
    
    if node.value == '-':
      node.truth = True

    elif node.value == '~':
      node.truth = not (left.truth)

    elif node.value == '^':
      if (left.truth is not None and right.truth is not None) or left.truth is not None:
        node.truth = left.truth and right.truth
      else:
        node.truth = right.truth and left.truth
    
    elif node.value == 'v': 
      if (left.truth is not None and right.truth is not None) or right.truth is not None:
        node.truth = right.truth or left.truth
      else:
        node.truth = left.truth or right.truth    


    if node.truth is None:
      return False
    return True

class Evaluate: 
	
	# Constructor to initialize the class variables 
  def __init__(self, capacity, vardict): 
    self.top = -1
    self.capacity = capacity
    self.vardict = vardict 
    # This array is used a stack 
    self.array = [] 
	
	# check if the stack is empty 
  def isEmpty(self): 
    return True if self.top == -1 else False

  # Return the value of the top of the stack 
  def peek(self): 
    return self.array[-1] 
    
  # Pop the element from the stack
  def pop(self): 
    if not self.isEmpty(): 
      self.top -= 1
      return self.array.pop() 
    else: 
      return "$"
  
  # Push the element to the stack 
  def push(self, op): 
    self.top += 1
    self.array.append(op) 
 
  # The main function that converts given infix expression to postfix expression 
  def evaluatePostfix(self, exp):     
    
    for i in exp:       
      
      if not (isOperator(i)): 
        self.push(self.vardict[i][0]) # push truth value onto stack
      
      # If the scanned character is an operator
      else: 
        if i == '~':
          val1 = self.pop() 
          val2 = None
        else:
          val1 = self.pop()
          val2 = self.pop() 
        res = my_eval(val1, val2, i)
        self.push(res) 
        
    return self.pop() 
				
def my_eval(val1, val2, op):

    res = None
   
    if op == '~':     # not
      return not (val1)
    
    elif op == '^':
      if (val1 is not None and val2 is not None) or val1 is not None:
        res = val1 and val2
      else:
        res = val2 and val1
    
    elif op == 'v': 
      if (val1 is not None and val2 is not None) or val2 is not None:
        res = val2 or val1
      else:
        res = val1 or val2  
         
    elif op == '-':
      if val2 == True and val1 == False:  # T -> F is False 
        res = False
      else:
        res = True  

    return res
    


# Driver program to test tree construction and facts processing 
# a^b -> c
# p ->b
# p
# ~c
#----------
# a ^~c

def eval_main(eval_input , infix_questions):

  # conditionals = ["ab^c-" , "pb-"]
  # facts = ["p^~c"]
  # questions = ["ac~^","c"] # should have postfix expressions

  # conditionals = []
  # facts = ["avb"]
  # questions = ["a" , "ab~^"] 
  # print("eval_in" , eval_input)
  # eval_input = [['c d ^ e ~ -> '], [' c e ^ ', ' d ~ '] , ['c ^ ~ d ']]

  for i in range(len(eval_input)):
    for j in range(len(eval_input[i])):
      eval_input[i][j] = eval_input[i][j].replace(' ','').replace('->','-')

  conditionals , questions , facts = eval_input

  vardict = {} # {a: T, [<nodes where that var occurs>]}
  treeList = []
  for expr in conditionals:
    r = constructTree(expr , vardict)
    treeList.append(r)
    print("Infix expression is")
    inorder(r)
    print()


  finalFacts = []
  knownVars =[]
  quesVars = []
  factProcessing(facts , finalFacts)
  evaluateFacts(finalFacts , vardict , knownVars)
  quesProcessing(questions , quesVars)
  # print("ques vars", quesVars)
  # print("final Facts", finalFacts)
  # print("known Vars", knownVars)
  #print("var dict" , vardict)

  #Evaluate the expressions
  evalMain(vardict , knownVars , quesVars)
  print(vardict)
  print()
  print ("----FINAL RESULT----")

  result = dict()

  for i in range(len(questions)):
    if (isUnknownQuesVars(quesVars[i], vardict)):
      result[infix_questions[i]] = "Cannot be determined"
      print("Expression: {:10} Result: {:5}".format(infix_questions[i], "Cannot be determined"))
    else:
      obj = Evaluate(len(questions[i]), vardict) 
      ans = str(obj.evaluatePostfix(questions[i]))
      result[infix_questions[i]] = ans
      print("Expression: {:10} Result: {:5}".format(infix_questions[i], ans ))
  
  return result