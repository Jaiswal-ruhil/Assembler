#!/bin/env/python2
import sys
program_length=0
### Creates Symbol Table using statically defined optable and source code.
def createSymbolTable(optable,filename):
  global program_length
  loc_Ctr=0                                                   #Linear Addres Generated.
  symtable=dict()
  errors=list()                                               #List of undeclared operands.
  errors.append("end")                                        #Make Sure and end statement is present in the Program.
  fp=open(filename,'r')
  data=fp.readlines()                                         #Read Source File.
  fp.close()
  program_name=""
  line=0
  firstLine=data[0]
  firstLine=(firstLine.strip()).split()
  args=firstLine.__len__()
  if args==3:
    label,opcode,operand=firstLine
    if (opcode=='START' or opcode=='start'):                  #Check for Start Instruction.
      program_name=label
      try:
        loc_Ctr=int(operand)                                  #Different Linear Start Address.
        data=data[1:]                                         #Delete Start instruction.
      except:
        print "Error! Syntax Error at Line:"+str(line)+" no\nPlease enter a valid address"
        exit(-1)
                                                              #Creation of Symbol Table
  for x in data:
    line=line+1                                               #Line Count in Source Code.
    inputLine=((x.strip()).split())
    args=inputLine.__len__()

    if(args==3):                                              #Contains label,opcode,operand
      label,opcode,operand=inputLine
      if(opcode!='resb' and opcode!='byte' and opcode!='word' and opcode!='resw' and opcode!='RESB' and opcode!='BYTE' and opcode!='WORD' and opcode!='RESW'):
        if(errors.count(operand)==0):
          errors.append(operand)
    elif(args==2):                                            #Contains opcode,operand.
      opcode,operand=inputLine
      if((opcode == 'END' or opcode == 'end') and operand == program_name):
        errors.remove("end")
        break;
      if(errors.count(operand==0)):
        errors.append(operand)
    elif(args==1):                                            #Contains operand.
      opcode=inputLine[0]
      if opcode=='//':                                        #Skip Comment Lines.
        continue
      elif(opcode == 'END' or opcode == 'end'):               #Indicates end of Source File.
        errors.remove("end")
        break
    elif(args==0):                                            #Skip Blank Lines.
        continue
    else:                                                     #Should contain only maximum 3 arguments.
      print "Error! Syntax Error at Line No:",line,"\n",inputLine," is not valid Assembly Code"
      exit(-1)
    try:
      if(opcode=='WORD' or opcode=='word'):                   #Word Declaration.
        symtable[label]=loc_Ctr
        loc_Ctr=loc_Ctr+3                                     #Linear Address + 3.
        if(errors.count(label)>0):
            errors.remove(label)                              #Operand is Missing.

      elif(opcode=='RESW' or opcode=='resw'):                 #Reserve a Word.
        symtable[label]=loc_Ctr
        loc_Ctr=loc_Ctr+(3*int(operand))                      #Linear Address + (3 * operand).
        if(errors.count(label)>0):
          errors.remove(label)                                #Operand is Missing.

      elif(opcode=='RESB' or opcode=='resb'):                 #Reserve a Byte.
        symtable[label]=loc_Ctr
        loc_Ctr=loc_Ctr+int(operand)                          #Linear Address + 3.
        if(errors.count(label)>0):
          errors.remove(label)                                #Operand is Missing.

      elif(opcode=='BYTE'or opcode=='byte'):                  #Byte Declaration.
        symtable[label]=loc_Ctr
        loc_Ctr=loc_Ctr+(operand.__len__())                   #Linear Address + Length of Operand.
        if(errors.count(label)>0):
            errors.remove(label)                              #Operand is Missing.

      elif((optable[opcode])[2] and args==3):                 #Check if opcode is Declared in Optable.
        symtable[label]=loc_Ctr                               #Store Linear Address with Operation.
        loc_Ctr=loc_Ctr+int((optable[opcode])[2])             #Linear Address + Length of Operation.

      elif((optable[opcode])[2]):
        loc_Ctr=loc_Ctr+int((optable[opcode])[2])             #Linear Address + Length of Operation
    except KeyError:                                          #Opcode is Missing.
      print "Error! Syntax Error at Line:",str(line)," no\n",inputLine," is not valid Assembly Code"
      exit(-1)
    program_length=loc_Ctr
  if(errors.__len__()!=0):                                    #Variables Undeclared.
    for x in errors:
      print "Error! Syntax Error Operand "+x+" is Undeclared in the Assembly Code\n"
    exit(-1)
  return symtable

def assemble(filename):
  optable=loadOpTable()                                       #Load OpTable from optable.dat.
  print "\nSuccessfully Loaded OpCode Table for the Machine : optable.dat\n"
  symtable=pass1(filename,optable)                            #Create Symbol Table and Validate Source Code.
  print "Successfully created Symbol Table for the input program : symtable.dat\n"
  pass2(filename,symtable,optable)                            #Map Linear Address with required Opcode from Optable.
  print "Successfully created Object Code for the input program : ObjectFile\n"

def pass1(filename,optable):
  symtable=createSymbolTable(optable,filename)                #Create Symbol Table.
  fp=open('symtable.dat','w')
  symbol=symtable.keys()
  symtable_Hex=dict()                                         #Address conversion to Hexadecimal.
  address=[hex(int(x)) for x in symtable.values()]
  for x in range(symbol.__len__()):
    fp.write(symbol[x]+" "+address[x]+"\n")
    symtable_Hex[symbol[x]]=address[x]
  fp.close()
  return symtable_Hex

def pass2(filename,symtable,optable):
  global program_length
  fp=open(filename,'r')
  data=fp.readlines()
  fp.close()
  program_name="Program"
  start_address=0
  fp=open('ObjectFile','w')
  firstLine=data[0]                                            #Check of first Line is Start operation.
  firstLine=(firstLine.strip()).split()
  args=firstLine.__len__()
  if args==3:
    label,opcode,operand=firstLine
    if (opcode=='START' or opcode=='start'):
      program_name=label
      start_address=hex(int(operand))
      data=data[1:]                                         #Delete operation.
  program_length=program_length-int(start_address,16)
  program_length=hex(program_length)
  fp.write('H'+'^'+program_name[0:5]+'^'+str(start_address)+'^'+str(program_length)+'\n')
  fp.write('T'+'^')
  for x in data:
    inputLine=((x.strip()).split())
    args=inputLine.__len__()
    if(args==3):                                              #Contains label,opcode,operand.
      label,opcode,operand=inputLine
      if(opcode!='resb' and opcode!='byte' and opcode!='word' and opcode!='resw' and opcode!='RESB' and opcode!='BYTE' and opcode!='WORD' and opcode!='RESW'):
        fp.write(str((optable[opcode])[0])+''+str(symtable[operand])+'^')
    elif(args==2):                                            #Contains opcode,operand.
      opcode,operand=inputLine
      if((opcode == 'END' or opcode == 'end') and operand == program_name):
        fp.write('\nE'+'^'+start_address)
        fp.close()
        break
      fp.write(str((optable[opcode])[0])+''+str(symtable[operand])+'^')
    elif(args==1):                                            #Contains opcode
      opcode=inputLine[0]
      if opcode=='//':                                        #skip comment.
        continue
      elif(opcode == 'END' or opcode == 'end'):               #Terminatation of Source Code.
        fp.write('\nE'+'^'+start_address)
        fp.close()
        break
      fp.write(optable[opcode])
    elif(args==0):                                            #Blank Line Skip.
        continue


def loadOpTable():
  optable=dict()
  fp=open('optable.dat','r')
  data=fp.readlines()
  for x in data:
    x=x.strip()
    opcode,bincode,instr_Format,instr_length = x.split()      #Read File and Store data in optable dictionary.
    optable[opcode]=[bincode,instr_Format,instr_length]
  fp.close()
  return optable

if len(sys.argv)<2:
  print "Error! no Input file detected"                       #Input File Missing.
else:
  filename=sys.argv[1]
  try:
    fp=open('optable.dat','r')
    fp.close()
  except (OSError,IOError) as e:
    print 'Op Code Table Missing, Please Store the Op Code Table for the Assembler\nError! File: optable.dat Missing'
  assemble(filename)
