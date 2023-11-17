#! python Nagmat Nazarov 1002186972
# (c) DL, UTA, 2009 - 2016
import  sys, string, time
# Global variables
wordsize = 24                                        # everything is a word
numregbits = 3                                       # actually +1, msb is indirect bit
opcodesize = 5
addrsize = wordsize - (opcodesize+numregbits+1)      # num bits in address
memloadsize = 1024                                   # change this for larger programs
numregs = 2**numregbits
regmask = (numregs*2)-1                              # including indirect bit
addmask = (2**(wordsize - addrsize)) -1
nummask = (2**(wordsize))-1
opcposition = wordsize - (opcodesize + 1)            # shift value to position opcode
reg1position = opcposition - (numregbits +1)            # first register position
reg2position = reg1position - (numregbits +1)
memaddrimmedposition = reg2position                  # mem address or immediate same place as reg2
realmemsize = memloadsize * 1                        # this is memory size, should be (much) bigger than a program
#memory management regs
codeseg = numregs - 1                                # last reg is a code segment pointer
dataseg = numregs - 2                                # next to last reg is a data segment pointer
#ints and traps
trapreglink = numregs - 3                            # store return value here
trapval     = numregs - 4                            # pass which trap/int
mem = [0] * realmemsize                              # this is memory, init to 0 
reg = [0] * numregs                                  # registers
clock = 1                                            # clock starts ticking
ic = 0                                               # instruction count
numcoderefs = 0                                      # number of times instructions read
numdatarefs = 0                                      # number of times data read
nummemref = 0
starttime = time.time()
curtime = starttime
predictionTable = [True]
guess = 0

def startexechere ( p ):
    # start execution at this address
    reg[ codeseg ] = p    
def loadmem():                                       # get binary load image
  global nummemref
  curaddr = 0
  for line in open("a.out", 'r').readlines():
    token = str.split(str.lower(line))      # first token on each line is mem word, ignore rest
    if ( token[ 0 ] == 'go' ):
        startexechere(  int( token[ 1 ] ) )
    else:
        mem[curaddr] = int( token[ 0 ], 0 )
        curaddr = curaddr = curaddr + 1
def getcodemem ( a ):
    global nummemref
    nummemref = nummemref + 1
    # get code memory at this address
    memval = mem[ a + reg[ codeseg ] ]
    return ( memval )
def getdatamem ( a ):
    global nummemref
    nummemref = nummemref + 1
    # get code memory at this address
    memval = mem[ a + reg[ dataseg ] ]
    return ( memval )

def storedatamem( a,v ):
    global nummemref
    nummemref = nummemref + 1
    # write the data into memoru
    mem[a+reg[dataseg]] = v

def getregval ( r ):
    # get reg or indirect value
    if ( (r & (1<<numregbits)) == 0 ):               # not indirect
       rval = reg[ r ] 
    else:
       rval = getdatamem( reg[ r - numregs ] )       # indirect data with mem address
    return (rval)
def checkres( v1, v2, res):
    v1sign = ( v1 >> (wordsize - 1) ) & 1
    v2sign = ( v2 >> (wordsize - 1) ) & 1
    ressign = ( res >> (wordsize - 1) ) & 1
    if ( ( v1sign ) & ( v2sign ) & ( not ressign ) ):
      return (1)
    elif ( ( not v1sign ) & ( not v2sign ) & ( ressign ) ):
      return (1)
    else:
      return(0)
def dumpstate(d):
    if ( d ==1):
        print("Dumpstate 1 = {} =".format(reg))
    elif ( d == 2 ):
        print("Dumpstate2 mem = {} = ".format(mem))
    elif ( d == 3 ):
        print("clock={} , IC={}, Coderefs={}, Datarefs={}, Start Time={}, Currently={}, Number of Memory access = {} , Guess = {} ".format(clock,ic, numcoderefs,numdatarefs,starttime, time.time(),nummemref,guess))

def print_sb(sb):
    for i in range(sb):
        print("sb {} = {} ".format(i,sb[i]))
def trap ( t ):
    # unusual cases
    # trap 0 illegal instruction
    # trap 1 arithmetic overflow
    # trap 2 sys call
    # trap 3+ user
    rl = trapreglink                            # store return value here
    rv = trapval
    if ((t==0) | (t==1)):
       dumpstate(1)
       dumpstate(2)
       dumpstate(3)
    elif ( t == 2 ):                          # sys call, reg trapval has a parameter
       what = reg[ trapval ] 
       if ( what == 1 ):
           a = a        #elapsed time
    return ( -1, -1 )
    return ( rv, rl )
# opcode type (1 reg, 2 reg, reg+addr, immed), mnemonic  
opcodes = { 1: (2, 'add'), 2: ( 2, 'sub'), 
            3: (1, 'dec'), 4: ( 1, 'inc' ),
            7: (3, 'ld'),  8: (3, 'st'), 9: (3, 'ldi'),
           12: (3, 'bnz'), 13: (3, 'brl'),
           14: (1, 'ret'),
           16: (3, 'int') }
startexechere(0)                                  # start execution here if no "go"
loadmem()                                           # load binary executable
ip = 0                                              # start execution at codeseg location 0
# while instruction is not halt
sb = [0] * numregs
numstalls =  0
while( 1 ):
   print("SB = {} Number of stalls = {} , branch_predictor = {} ".format(sb,numstalls, predictionTable[0]))
   clock = clock + 1
   ir = getcodemem(ip)                            # - fetch
   ip = ip + 1
   opcode = ir >> opcposition                       # - decode
   clock = clock + 1
   reg1   = (ir >> reg1position) & regmask
   reg2   = (ir >> reg2position) & regmask
   addr   = (ir) & addmask
   ic = ic + 1
   print("ir = {}, ip={}, opcode={}, opcpos={}, reg1={},reg2={}addr={}, ic={} guess = {} ".format(ir,ip,opcode,opcposition,reg1,reg2,addr,ic,guess))
                                                    # - operand fetch
                                                    # - operand fetch
   clock = clock + 1
   if not (opcode in opcodes):
      tval, treg = trap(0) 
      if (tval == -1):                              # illegal instruction
         break
   memdata = 0                                  #     contents of memory for loads
   if opcodes[opcode][0] == 1:                   #     dec, inc, ret type
      operand1 = getregval( reg1 )                  #       fetch operands
      if sb[reg1]==0 :
          sb[reg1]=3
      else :
          print("We face stalls here 1")
          numstalls = numstalls + 1
   elif opcodes[opcode][0]== 2:                 #     add, sub type
      operand1 = getregval(reg1)                  #       fetch operands
      print("Register 1 = {}".format(reg1))
      if sb[reg1]==0 :
          sb[reg1]=3
      else:
          print("We face stalls here 2")
          numstalls = numstalls + 1
      operand2 = getregval(reg2)
      print("Operand2 = {} , reg2 = {} ".format(operand2,reg2))
   elif opcodes[opcode] [0] == 3:                 #     ld, st, br type
      operand1 = getregval( reg1 )                  #       fetch operands
      operand2 = addr                     
   elif opcodes[opcode][0] == 0:                 #     ? type
      break
   if (opcode == 7):                                # get data memory for loads
      memdata = getdatamem( operand2 )
   #print("\n\nAddr = {}, Operand2 = {} Opcode = {} , ".format(addr, operand2,opcode))
   if (opcode == 8 ) :
       operand2 = getregval(addr)
       if sb[reg2]==0 :
           sb[reg2]=2
       else :
           print("We face stalls here 2")
           numstalls = numstalls + 1
       #print("\n\nAddr = {}, Operand2 = {} ".format(addr, operand2))
   # execute

   if opcode == 1:                     # add
      clock = clock + 1
      result = (operand1 + operand2) & nummask
      if (checkres( operand1, operand2, result )):
         tval, treg = trap(1) 
         if (tval == -1):                           # overflow
            break
   elif opcode == 2:                   # sub
      clock = clock + 1
      result = (operand1 - operand2) & nummask
      if ( checkres( operand1, operand2, result )):
         tval, treg = trap(1) 
         if (tval == -1):                           # overflow
            break
   elif opcode == 3:                   # dec
      clock = clock + 1
      result = operand1 - 1
   elif opcode == 4:                   # inc
      clock = clock + 1
      result = operand1 + 1
   elif opcode == 7:                   # load
      result = memdata
   elif opcode == 8 :
      result = operand1
   elif opcode == 9:                   # load immediate
      result = operand2
   elif opcode == 12:                  # conditional branch
      print("\n\n12 Bnz operand1 = {} ".format(operand1))
      result = operand1
      if result != 0:
         if predictionTable[0]:
             guess = guess + 1
         print("\n\n12Bnz operand2 = {} ".format(operand2))
         ip = operand2
         if sb[operand2]!= 0 :
             sb[operand2]=2
         else:
             print("\n\n\nWe face stalls here 2")
             numstalls = numstalls + 1
      else :
          predictionTable[0] = not (predictionTable[0])
   elif opcode == 13:                  # branch and link
      print("\n\n13 Bnz operand2 = {} ".format(operand2))
      result = ip
      ip = operand2
   elif opcode == 14:                   # return
      ip = operand1
   elif opcode == 16:                   # interrupt/sys call
      result = ip
      tval, treg = trap(reg1)
      if (tval == -1):
        break
      reg1 = treg
      ip = operand2
   # write back
   if ( (opcode == 1) | (opcode == 2 ) | 
         (opcode == 3) | (opcode == 4 ) ):     # arithmetic
        clock = clock + 1
        print("reg= {}, reg1={} ".format(reg,reg1))
        reg[reg1]=result
   elif ( (opcode == 7) | (opcode == 9 )):     # loads
        clock = clock + 1
        reg[reg1] = result
        if sb[reg1]==0 :
            sb[reg1]=3
        else :
            print("We face stalls here 2")
            numstalls = numstalls + 1
   elif (opcode ==8 ):
        clock = clock + 1
        storedatamem(operand2,result)
   elif (opcode == 13):                        # store return address
        clock = clock + 1
        print("Store1 ={},{}= ".format(reg1,reg))
        reg[reg1] = result
   elif (opcode == 16):# store return address
        clock = clock + 1
        print("store2= {},{}=".format(reg1,reg))
        reg[reg1] = result
   for i in range(len(sb)):
        if sb[i]!= 0 :
            sb[i]=sb[i]-1
   # end of instruction loop
# end of execution
