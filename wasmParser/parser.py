import re
import subprocess as sp
import os
import sys

# RE_TYPE = re.compile("\s+\(type\s+\((.[^\)]+)\)")
RE_TYPE = re.compile("\s+\(type\s+\(;(\d+);\)")
# RE_IMPORT = re.compile('\s+\(import "env" "(.+)"')
RE_IMPORT = re.compile('\s+\(import ".*"\s"(.*)"')
# RE_FUNCTION = re.compile("\s+\(func\s+\((.[^\)]+)\)")
RE_FUNCTION_1 = re.compile("\s+\(func \([^;]*;([0-9]*);\) \(type ([0-9]*)\)")
RE_FUNCTION_2 = re.compile("\s+\(func (\$[^\s]*) \(type ([0-9]*)\)")
RE_GLOBAL = re.compile("\s+\(global\s+\(;(\d+);")

RE_EXPORT = re.compile('\s+\(export\s"(.+)"\s\(func\s(.+)\)\)')
RE_ELEM = re.compile("\s+\(elem\s+\(;(\d+);")
RE_DATA = re.compile("\s+\(data\s+\(;(\d+);")

RE_PARAM = re.compile('\(param (([if][3264]{1,2}( )*)+)\)')
RE_LOCAL = re.compile('\(local (([if][3264]{1,2}( )*)+)\)')
RE_RESULT = re.compile('\(result (([if][3264]{1,2}( )*)+)\)')

from . import sectionStructure as ss
from strategies import state

from importlib import reload
reload(ss)

def retIndent(inst):
    return ' '*(len(inst) - len(inst.lstrip()))

def retType(inst):
    if "i32" in inst:
        return "i32"
    elif "i64" in inst:
        return "i64"
    elif "f32" in inst:
        return "f32"
    elif "f64" in inst:
        return "f64"

def parseWast(origin_wast):
    parsedSection = {'Type': dict(), 'Import': dict(),'Function': dict(), 'Table': list(), 'Memory': list(), 'Global': dict(), \
        'Export': dict(), 'Start': list(), 'Element': dict(), 'Code': list(), 'Data': dict(), 'Custom': list()}

    # funcHeaderLine = str()
    funcHeaderArea = False
    funcHeaderLine = list()
    funcBodyArea = False
    funcBodyLine = list()
    func_bracketNum = 0


    for l in range (0, len(origin_wast)):
        
        line = origin_wast[l]
        
        ## Type, Import, Function, Table, Memory, Global, Export, Start, Element, Code, Data, Custom
        whichSection = [0 for i in range(12)]
        
        matchType = re.match(RE_TYPE,line)
        if matchType:
            # print(matchType.group(1))
            typeID = matchType.group(1) ##type ID. e.g., 1
            whichSection[0] = 1
            
            has_param = re.search(RE_PARAM,line)
            param = has_param.group(1) if has_param is not None else None
            has_result = re.search(RE_RESULT,line)
            result = has_result.group(1) if has_result is not None else None

            # TYPE - param:list, result:list, line:str
            parsedSection["Type"][typeID] = ss.TYPE(param=param, result=result, line=[line, ''])
        
        matchImport = re.match(RE_IMPORT,line)
        if matchImport:
            importID = matchImport.group(1)
            whichSection[1] = 1
            
            isFuncImport = re.search(RE_FUNCTION_1,line)
            if not isFuncImport:
                isFuncImport = re.search(RE_FUNCTION_2,line)
            if isFuncImport:
                funcID = isFuncImport.group(1) ##function ID. e.g., ;1;
                funcType = isFuncImport.group(2)
            else:
                funcID = None
                funcType = None
            
            parsedSection["Import"][importID] = ss.IMPORT(funcID=funcID, type=funcType, line=[line, ''])
            # parsedSection["Import"].append(ss.sectionOffset(identifier=importID, startOffset=l))

        matchGlobal = re.match(RE_GLOBAL,line)
        if matchGlobal:
            globalID = matchGlobal.group(1) ##global ID(only numeric). e.g., 1
            whichSection[5] = 1
            
            parsedSection["Global"][globalID] = ss.GLOBAL(line=[line, ''])
            # print(globalID)
            # parsedSection["Global"].append(ss.sectionOffset(identifier=globalID.replace(';',''), startOffset=l))
        
        matchExport = re.match(RE_EXPORT,line)
        if matchExport:
            exportID = matchExport.group(1)
            whichSection[6] = 1
            parsedSection["Export"][exportID] = ss.EXPORT(line=[line, ''])
            
        matchElem = re.match(RE_ELEM,line)
        if matchElem:
            elemID = matchElem.group(1)
            whichSection[8] = 1
            parsedSection["Element"][elemID] = ss.ELEMENT(line=[line, ''])
            
        matchData = re.match(RE_DATA,line)
        if matchData:
            dataID = matchData.group(1)
            whichSection[10] = 1
            parsedSection["Data"][dataID] = ss.DATA(line=[line, ''])
        
        matchFunc = re.match(RE_FUNCTION_1,line)
        if not matchFunc:
            matchFunc = re.match(RE_FUNCTION_2,line)
        if matchFunc:
            # print(matchType.group(1))
            funcID = matchFunc.group(1) ##function ID. e.g., ;1;
            funcType = matchFunc.group(2)
            whichSection[2] = 1
            # print(funcID)
            func_bracketNum += line.count('(') - line.count(')')
            
            funcHeaderArea = True
            funcHeaderLine.append([line, ''])
            
            parsedSection["Function"][funcID] = ss.FUNCTION(type=funcType)
        
            
        # print(whichSection)
        if 1 not in whichSection and (funcHeaderArea==True or funcBodyArea==True):
            
            func_bracketNum += line.count('(') - line.count(')')
            
            # print(l, func_bracketNum)
            if func_bracketNum == 1:
                # print('\n', line.strip())
                if (((line.count('(')+line.count(')')) == 0) or 'block' in line) and funcBodyArea == False:
                    # print('here')
                    funcHeaderArea = False
                    
                    funcBodyArea = True
                    funcBodyLine.append([line, ''])
                    
                    # thisFuncElem = parsedSection["Function"][len(parsedSection["Function"])-1]
                    # thisFuncElem.bodyStartOffset = l
                    # parsedSection["Function"][len(parsedSection["Function"])-1] = thisFuncElem
                    
                elif funcBodyArea == False:
                    funcHeaderLine.append([line, ''])
                    
                else:
                    funcBodyLine.append([line, ''])
                    continue
            elif func_bracketNum == 0:
                # thisFuncElem = parsedSection["Function"][len(parsedSection["Function"])-1]
                # thisFuncElem.endOffset = l
                # if thisFuncElem.bodyStartOffset == None:
                #     thisFuncElem.bodyStartOffset = (l-1)
                
                # parsedSection["Function"][len(parsedSection["Function"])-1] = thisFuncElem
                funcHeaderLineStr = [h[0] for h in funcHeaderLine]
                # print(funcHeaderLineStr)
                funcHeaderStr = (''.join([n.strip() for n in funcHeaderLineStr]))
                # print(funcHeaderStr)
                # print(funcID, funcHeaderStr, '\n')
                
                has_param = re.search(RE_PARAM,funcHeaderStr)
                param = has_param.group(1) if has_param is not None else None
                has_result = re.search(RE_RESULT,funcHeaderStr)
                result = has_result.group(1) if has_result is not None else None
                has_local = re.search(RE_LOCAL,funcHeaderStr)
                local = has_local.group(1) if has_local is not None else None      
                
                parsedSection["Function"][funcID].param = param
                parsedSection["Function"][funcID].result = result
                parsedSection["Function"][funcID].local = local
                parsedSection["Function"][funcID].header = funcHeaderLine
                funcHeaderLine = list()
                
                last_bodyIndent = retIndent(line)
                # if line[-2] == ')' and (line != last_bodyIndent+'end)\n'):
                if line[-2] == ')':
                    last_bodyLine = [[line[:-2]+'\n', ''], [last_bodyIndent+')\n','']]
                else:
                    last_bodyLine = [[line, '']]
                
                # funcBodyLine.append(line)
                funcBodyLine += last_bodyLine
                parsedSection["Function"][funcID].body = funcBodyLine
                
                funcBodyArea = False
                funcBodyLine = list()
    
    # print(parsedSection["Global"])          
    # print(state.LAST_GLOBAL_ID)
    
    return parsedSection

def savePertWasm(path, name, ptSection):
    # print(path)
    os.makedirs(path+"meta/", exist_ok=True)
    
    with open(path+name, 'w') as fw, open(path+'meta/'+name, 'w') as mw:
        fw.write("(module\n")
        
        for sec in ptSection:
            
            if sec=="Type":
                sec_type = ptSection["Type"]
                if len(sec_type)!=0:
                    for t in sec_type:
                        fw.write(sec_type[t].line[0])
                        if sec_type[t].line[1] != '':
                            mw.write(f'[TYPE]{t}, {sec_type[t].line[1]}\n')
            
            elif sec=="Import":
                sec_import = ptSection["Import"]
                if len(sec_import)!=0:
                    for i in sec_import:
                        fw.write(sec_import[i].line[0])
                        if sec_import[i].line[1] != '':
                            mw.write(f'[IMPORT]{i}, {sec_import[i].line[1]}\n')
                        
            elif sec=="Function":
                sec_function = ptSection["Function"]
                if len(sec_function)!=0:
                    for f in sec_function:
                        headerLines = [h[0] for h in sec_function[f].header]
                        fw.write(''.join(headerLines))
                        for h_idx in range(0, len(headerLines)):
                            if sec_function[f].header[h_idx][1] != '':
                                mw.write(f'[FUNC-H]{f}-{h_idx}, {sec_function[f].header[h_idx][1]}\n')
                        
                        bodyLines = [b[0] for b in sec_function[f].body]
                        if bodyLines[-1]=='    )\n':
                            bodyLines.remove('    )\n')
                            funcEndLine = bodyLines[-1]
                            bodyLines[-1] = funcEndLine.replace('\n',')\n')
                            # print(sec_function[f].body[-1])
                        for b_idx in range(0, len(bodyLines)):
                            # print(sec_function[f].body[b_idx])
                            if sec_function[f].body[b_idx][1] != '':
                                mw.write(f'[FUNC-B]{f}-{b_idx}, {sec_function[f].body[b_idx][1]}\n')
                        fw.write(''.join(bodyLines))
            
            elif sec=="Table":
                sec_table = ptSection["Table"]
                if len(sec_table)!=0:
                    next
                    # for f in sec_table:
                    #     fw.write(''.join(sec_table[f].line))
                    #     fw.write(''.join(sec_function[f].body))
            
            elif sec=="Memory":
                sec_memory = ptSection["Memory"]
                if len(sec_memory)!=0:
                    next
                    
            elif sec=="Global":
                sec_global = ptSection["Global"]
                if len(sec_global)!=0:
                    for g in sec_global:
                        fw.write(sec_global[g].line[0])
                        if sec_global[g].line[1] != '':
                            mw.write(f'[GLOBAL]{g}, {sec_global[g].line[1]}\n')
                        
            elif sec=="Export":
                sec_export = ptSection["Export"]
                if len(sec_export)!=0:
                    for x in sec_export:
                        fw.write(sec_export[x].line[0])
                        if sec_export[x].line[1] != '':
                            mw.write(f'[EXPORT]{x}, {sec_export[x].line[1]}\n')
                        
            elif sec=="Start":
                sec_start = ptSection["Start"]
                if len(sec_start)!=0:
                    next
                    
            elif sec=="Element":
                sec_element = ptSection["Element"]
                if len(sec_element)!=0:
                    for e in sec_element:
                        fw.write(sec_element[e].line[0])
                        if sec_element[e].line[1] != '':
                            mw.write(f'[ELEMENT]{e}, {sec_element[e].line[1]}')
                        
            elif sec=="Code":
                sec_code = ptSection["Code"]
                if len(sec_code)!=0:
                    next
                    
            elif sec=="Data":
                sec_data = ptSection["Data"]
                if len(sec_data)!=0:
                    for d in sec_data:
                        fw.write(sec_data[d].line[0])
                        if sec_data[d].line[1] != '':
                            mw.write(f'[DATA]{d}, {sec_data[d].line[1]}')
                        
            elif sec=="Custom":
                sec_custom = ptSection["Custom"]
                if len(sec_custom)!=0:
                    next
                    
    ### Uncomment the below code to directly convert .wast file into .wasm
    # cmd = "wat2wasm " + path+name + " -o " + path+(name[:-1] + 'm')
    # result = sp.run(cmd.split(' '))
    # if result.returncode != 0:
    #     print("[wat2wasm failed]", path)
    
##################################################################


def retFuncIDs(parsedSection):
    
    funcIDs = list()
    
    for f in parsedSection['Function']:
        funcIDs.append(f.identifier)
    
    return funcIDs