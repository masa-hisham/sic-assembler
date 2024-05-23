import os
from collections import namedtuple
from token import COMMENT

AppStruct = namedtuple('AppStruct', "Value Length Address")
OPERATIONTABEL = {}
# Read the operation table from the file
try:
    with open("optab.txt", "r") as optab_file:
        for line in optab_file:
            parts = line.split()
            if len(parts) == 2:  # Ensure there are exactly two parts
                mnemonic, opcode = parts
                OPERATIONTABEL[mnemonic] = opcode
except FileNotFoundError:
    print("The operation table file 'optab.txt' does not exist. Please check the filename and try again.")
    exit()
# define the directives
DIRECTIVES = ['START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW', 'BASE']

ErrFlag = False
try:
    inputFile = open("sic.txt", "r")  # read sic file
    
except:
    print("The file: " + " does not exist, please check the name correctly.")
    ErrFlag = True
outputFile = open("intermediate.mdt", "w")  # create output file
listFile = open("list.txt", "w")  # write to list file
objectFile = open("obj.txt", "w")  # write to object file

while ErrFlag:
    break

Lines = inputFile.readlines()  # read the input file line by line
# define each column as a list
LOCCOUNTER = list()
LAB = list()
opcode = list()
OPERAND = list()
literal = {}  # {key, value}
SYMB = {}
error = []
jump = False
noOfLiter = 0
index = 0
LOCATION = int("0000", base=16)
prgName = Lines[0][0:9].strip()
first_line = Lines[0]
ByteLen = 0
isJump = False
isLiteral = False
isIndexed = False
objeText = ""
listText = ""
ObjCodes = []
LocctrArray = []

if first_line[11:19].strip() == 'START':
    LOCATION = int(first_line[21:38].strip(), base=16)
    #  first line to intermFile
    BaceLocation = LOCATION
    LOCCOUNTER.append(hex(BaceLocation))
    LAB.append(first_line[0:9])
    opcode.append(first_line[12:20])
    OPERAND.append(first_line[22:39].strip())
else:
    LOCATION = int("0000", base=16)
    BaceLocation = LOCATION

start_location = BaceLocation

for lineIndex, line in enumerate(Lines):
    tmpLocationCtr = BaceLocation
    if lineIndex == 0: continue
    #handel daplicat coment
    if line.strip()[0] != '.':
        _Label = line[0:10].strip()
        _Opcode = line[12:20].strip()
        _Operand = line[22:39].strip()
        #handel daplicat lapel
        if _Label != '':
            if _Label in SYMB:
                error.append('ERROR-Line:' + str(lineIndex) + ' : duplicate symbol')
                ErrFlag = True
            elif (_Label != ''):
                # insert {LABEL,baseLoc} into SYMTAB
                SYMB[_Label] = BaceLocation

        # search OPTAB for opcode
        if (_Opcode in OPERATIONTABEL):
            BaceLocation = BaceLocation + 3
        elif (_Opcode == 'WORD'):
            BaceLocation += 3
        elif (_Opcode == 'RESW') and (_Operand != ''):
            BaceLocation += 3 * int(_Operand)
        elif (_Opcode == 'RESB') and (_Operand != ''):
            BaceLocation += int(_Operand)
        elif (_Opcode == 'BYTE'):
            if (_Operand[0] == 'C'):
                # -3 ==> to ignore the three characters ==> (C'')
                ByteLen = len(_Operand) - 3
                BaceLocation += ByteLen
            elif _Operand[0] == 'X':
                ByteLen = (int((len(_Operand) - 3) / 2))  # it will increase one byte to the baseLoc
                BaceLocation += ByteLen
                # LTORG && END Processing
        elif (_Opcode == 'LTORG' or _Opcode == 'END'):
            LAB.append(_Label)
            opcode.append(_Opcode)
            OPERAND.append(_Operand)
            LOCCOUNTER.append("      ")
            Displacement = 0
            total_Displacement = 0
            for _literal in literal:

                if (literal[_literal].Address == '0000'):
                    literal[_literal] = AppStruct(literal[_literal].Value, literal[_literal].Length,
                                                  hex(tmpLocationCtr + Displacement))

                    LAB.append("")
                    opcode.append("")
                    OPERAND.append(_literal)
                    LOCCOUNTER.append(str(hex(tmpLocationCtr + Displacement)))
                    Displacement += int(literal[_literal].Length)
                    total_Displacement += Displacement
                    BaceLocation += Displacement
        else:
            error.append('ERROR at line ' + str(lineIndex) + ': invalid operation code : ' + _Opcode)
            errorFlag = True

        if (_Operand != ''):
            # =C'-----' literal
            if (_Operand[0:2] == '=C'): 

                Name = _Operand
                Value = ''
                for char in _Operand[3:len(_Operand) - 1]:
                    asc = hex(ord(char))  # ASCII value
                    Value = Value + str(asc[2:])
                # -4 is to ignore the four characters ==> (=C'')
                LENG = len(_Operand) - 4
                New_Literal = AppStruct(Value, LENG, '0000')
                literal[Name] = New_Literal



            elif (_Operand[0:2] == '=X'):

                Name = _Operand
                Value = _Operand[3:len(_Operand) - 1]
                LENG = 1
                New_Literal = AppStruct(Value, LENG, '0000')
                literal[Name] = New_Literal
                # LOCCTR += length

                # write line to intermediate readFile, remove comment

        if (_Opcode != 'LTORG' and _Opcode != 'END'):  # END,LTORG lines have been written above
            LOCCOUNTER.append(hex(tmpLocationCtr))
            LAB.append(_Label)
            opcode.append(_Opcode)
            OPERAND.append(_Operand)



print('\n\n SYMTAB')
print('________________________\n|  LABEL   |  LOCATION  |\n|-----------------------|')
for lineNumber, Label in enumerate(SYMB):
    print("|  " + Label.ljust(10) + " |  " + str(hex(SYMB[Label])).upper()[2:] + ' H |')
print('|-----------------------|\n\n')
ProgramLength = BaceLocation - start_location - 1 + 1
print("\nProgram Name:: " + str(prgName) + "\n" + "Length:: " + str(hex(ProgramLength)[2:]).upper() + " H\n")
print(' masa bader\n')

listLength = len(LOCCOUNTER)
for item in range(listLength):
    ll = str(LOCCOUNTER[item].upper()[2:]) + "   " + str(LAB[item].ljust(10)) + "   " + str(
        opcode[item].ljust(10)) + "   " + str(OPERAND[item].ljust(10)) + "\n"
    outputFile.write(str(ll))

outputFile.close()

# --------------------------------------------------------------------
# Pass 2
IntermFile = open("intermediate.mdt", "r")
contents = IntermFile.readlines()

objeText = "H^" + prgName.ljust(6) + "^" + str(hex(start_location))[2:].zfill(6) + "^" + hex(ProgramLength)[2:].zfill(
    6).upper() + "\n"  # +

objectCode = ""
for lineNumber, line in enumerate(contents):
    opcode1 = line[20:32].strip()
    label1 = line[7:19].strip()
    operand1 = line[33:].strip()
    location1 = line[0:4].strip()

    if (isJump and (opcode1 != 'RESW' and opcode1 != 'RESB')):
        # this means that the jump has reached its end
        isJump = False
        ObjCodes.append('JumpEndsAt' + location1)  # (special jump item)
        LocctrArray.append('JumpHere')
    if (opcode1 == ''):
        objectCode = str(literal[operand1][0])
    elif opcode1 in OPERATIONTABEL:
        _Opcode = OPERATIONTABEL[opcode1]

        if (operand1 == ''):
            operandValue = "0000"
        elif (operand1 in SYMB):
            operandValue = str(hex(SYMB[operand1])[2:])
        elif (operand1 in literal):
            isLiteral = True
            operandValue = literal[operand1][2][2:]
        elif (operand1[len(operand1) - 2:] == ',X'):
            isIndexed = True
            oplen = len(operand1) - 2
            tempOperand = operand1[:oplen]
            if (tempOperand in SYMB):
                ModifiedOpr = int(hex(SYMB[tempOperand]), base=16)
                
                
                ModifiedOpr += 32768
                operandValue = hex(ModifiedOpr)[2:]


        else:  # error invalid operand
            error.append("ERROR-at Loc " + location1 + ": invalid operand: " + operand1)
        if (isLiteral or isIndexed):
            OOP = str(_Opcode)
            objectCode = OOP + str(operandValue).upper()
        else:
            objectCode = (_Opcode + operandValue.zfill(4)).upper()

    elif opcode1 == "RESW" or opcode1 == "RESB":
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        isJump = True  # begin or continue the current jump
        continue
    elif (opcode1 == "START"):
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 == "BYTE"):
        if (operand1[0] == 'X'):
            operandValue = operand1[2:len(operand1) - 1]
        elif (operand1[0] == 'C'):
            operandValue = ""
            # Calculate the value between the two parentheses C'---'
            for char in operand1[2:len(operand1) - 1]:
                asc = hex(ord(char))  # ASCII value
                operandValue = operandValue + str(asc[2:])  # to hex
                # print(operand_value)

        else:
            error.append("ERROR-at Loc " + location1 + ": the BYTE instruction should have either C or X")

        objectCode = operandValue
    elif (opcode1 == "WORD"):
        operandValue = hex(int(operand1))[2:]
        objectCode = operandValue.zfill(6)
    elif (opcode1 == "END"):
        ll1 = location1.upper() + "\t      " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 == "LTORG"):
        ll1 = location1.upper() + "\t      " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(
            10) + "\n"
        listText += ll1
        continue
    elif (opcode1 in literal):
        objectCode = str(literal[opcode1][0])
    else:
        # error invalid instruction
        error.append("ERROR-at Loc " + location1 + ": invalid instruction: " + opcode1)

    ObjCodes.append(objectCode)
    LocctrArray.append(location1)

    if (opcode1 in literal):
        # line = line[:5] + "*" + line[6:] # adds a star at the start of the literal line (as in the textbook)
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(10) + ""
        listText += ll1 + "   " + objectCode.upper() + "\n"
    else:
        ll1 = location1.upper() + "\t   " + label1.ljust(10) + "\t" + opcode1.ljust(10) + "\t" + operand1.ljust(10) + ""
        listText += ll1 + "   " + objectCode.upper() + "\n"

listFile.write(listText)

while (len(ObjCodes) > 0):
    lineLength = 30
    newLine = "T^" + LocctrArray[0].zfill(6)
    # While there are Object codes remaining
    while (len(ObjCodes) > 0 and len(ObjCodes[0]) / 2 <= lineLength and ObjCodes[0][
                                                                                        0:10] != "JumpEndsAt"):  # Check for Special jumps Items
        lineLength -= len(ObjCodes[0]) / 2
        objCod = "^" + ObjCodes.pop(0)
        LocctrArray.pop(0)
        newLine = newLine + objCod

    # Delete the Special List Item ("JumpEndsAtXXXX"),("Jumphere")
    if (len(ObjCodes) > 0 and ObjCodes[0][0:10] == "JumpEndsAt"):
        ObjCodes.pop(0)
        LocctrArray.pop(0)
    # Jump
    newLine = newLine[0:9].upper() + "" + hex(int(30 - lineLength))[2:].zfill(2).upper() + newLine[8:]
    objeText += newLine + "\n"

objeText += "E^" + str(hex(start_location))[2:].zfill(6)
objectFile.write(objeText)

listFile.close()
objectFile.close()


if len(error):
    for error in error:
        print(error)
    error.clear()
