from strategies import state
import re
import math

import random
import pickle as pkl
from wasmParser.parser import retIndent
from wasmParser.parser import retType

def checkIndent(inst):
    return ' '*(len(inst) - len(inst.lstrip()))

def call_indirect(wast, parsedSection, level):
    
    RE_TYPE = re.compile('\(type (\d*)\)')
    
    num_convertable_insts = 0
    num_converted_insts = 0
    
    for f in parsedSection['Function']:
        # if not f.identifier in pt_funcIDs:
        #     continue
        # print(f"\n==========={f.identifier}===========")
        
        pt_offset_list = list()
        for o in range(f.bodyStartOffset, f.endOffset+1):
            if "call " in wast[o][0]:
                pt_offset_list.append(o)
                # print(wast[o])
        # print(direct_offset_list)
        # print(f"[# convertable call instructions]:", len(pt_offset_list))
        
        num_convertable_insts += len(pt_offset_list)
        num_convInst = math.ceil(len(pt_offset_list)*(level/100))
        # print(f"[# converted call instructions]:", num_convInst)
        
        # num_convInst_real = 0
        
        for pt_offset in pt_offset_list[:num_convInst]:
            origin_line = wast[pt_offset][0]
            pt_indent = checkIndent(origin_line)
            remain_lines = wast[pt_offset][1:]
            
            # print(wast[pt_offset])
            callee = wast[pt_offset][0].strip().split("call ")[1]
            
            
            # print(callee)
            # print(f';{callee};')
            foundFunc = False
            # print(callee)
            for f in parsedSection['Function']:
                if f.identifier==f';{callee};' or f.identifier==callee:
                    typeID = re.search(RE_TYPE, wast[f.startOffset][0]).group(1)
                    elemID = ret_elem_param(wast, parsedSection, f.identifier)
                    foundFunc = True
                    break
            if not foundFunc:
                # print(callee)
                for i in parsedSection['Import']:
                    # print(callee, wast[i.startOffset][0])
                    if f'func (;{callee};' in wast[i.startOffset][0] or f'callee"' in wast[i.startOffset][0]:
                        # print('here')
                        # print(callee)
                        # print(wast[i.startOffset][0])
                        typeID = re.search(RE_TYPE, wast[i.startOffset][0]).group(1)
                        if callee.isdigit():
                            elemID = ret_elem_param(wast, parsedSection, callee)
                        else:
                            elemID = ret_elem_param(wast, parsedSection, i.identifier)
                        foundFunc = True
                        break
            if not foundFunc:
                continue
            
            wast[pt_offset] = [f"{pt_indent}i32.const {elemID}\n",
                f"{pt_indent}call_indirect (type {typeID})\n"] \
                    + remain_lines
            # num_convInst_real += 1
            num_converted_insts += 1
            
    print(f"# Original convertable call operations: {num_convertable_insts}")
    print(f"# converted call operations: {num_converted_insts} ({num_converted_insts/num_convertable_insts})\n")

def ret_elem_param(wast, parsedSection, funcID):
    
    if funcID in state.ELEM_PARAMS:
        elemParam = state.ELEM_PARAMS[funcID]
    else:
        last_element = parsedSection['Element'][-1]
        indent = checkIndent(wast[last_element.startOffset][0])
        
        elemParam_len = len(state.ELEM_PARAMS)
        elemParam = elemParam_len + 1
        state.ELEM_PARAMS[funcID] = elemParam
    
        funcID = funcID.replace(";","")
        if not funcID.isdigit() and funcID[0]!='$':
            funcID = '$'+funcID
            
        # print('here', funcID)
        new_elem = f"{indent}(elem (i32.const {elemParam}) {funcID})\n"
        wast[last_element.startOffset].append(new_elem)
    
    return elemParam

def add_NOP(parsedSection, _alpha, _beta, ratio=0):
    functions = parsedSection['Function']
    
    for f in functions:
        # if f != "41":
            # continue
        
        this_body = functions[f].body
        
        if ratio != 0:
            iter = round(len(this_body)*ratio)
        else:
            iter = 1
        
        target_lines = dict()
        
        for _ in range(0,iter):
            target_line_offset = math.floor((len(this_body)-1)*state.get_dist(_alpha,_beta))
            if target_line_offset not in target_lines:
                target_lines[target_line_offset] = 1
            else:
                target_lines[target_line_offset] += 1
            
        pt_body = list()
        # print(target_lines)
        
        for offset in range(0, len(this_body)):
            this_line = this_body[offset][0]
            if offset in target_lines:
                
                this_indent = retIndent(this_line)
                if 'end' in this_line:
                    this_indent = '  '+this_indent
                
                for _ in range(0, target_lines[offset]):
                    pt_body.append([f'{this_indent}nop\n','add NOP'])
                    
            pt_body.append([this_line, ''])
        
        parsedSection['Function'][f].body = pt_body
        
        ###################test###########################
        
        plt_list = list()
        # print(len(this_body))
        for b in range(0, len(this_body)):
            if b in target_lines:
                for _ in range(0, target_lines[b]):
                    plt_list.append(b)
                # print(target_lines[b], this_body[b])
            # else:
                # print(0, this_body[b])
        print(plt_list)
        plt.hist(plt_list, range=[0,len(this_body)])
        plt.ylim([0, 1650])
        # plt.xticks(range(0,))
        plt.title(f'\n(alpha={_alpha}, beta={_beta})')


def add_stackOP(parsedSection, dum_operation, _alpha, _beta, ratio=0):
    functions = parsedSection['Function']
    
    dummy_opcode = dum_operation.split('.')[1]
    dummy_type = dum_operation.split('.')[0]
    num_operand = state.num_operand[dummy_opcode]
    
    for f in functions:
        
        this_body = functions[f].body
        
        if ratio != 0:
            iter = round(len(this_body)*ratio)
        else:
            iter = 1
        
        target_lines = dict()
        
        for _ in range(0,iter):
            target_line_offset = math.floor((len(this_body)-1)*state.get_dist(_alpha,_beta))
            if target_line_offset not in target_lines:
                target_lines[target_line_offset] = 1
            else:
                target_lines[target_line_offset] += 1
            
        pt_body = list()
        # print(target_lines)
        
        for offset in range(0, len(this_body)):
            this_line = this_body[offset][0]
            if offset in target_lines:
                
                this_indent = retIndent(this_line)
                if 'end' in this_line:
                    this_indent = '  '+this_indent
                
                for _ in range(0, target_lines[offset]):
                    for _ in range(0,num_operand):
                        pt_body.append([f'{this_indent}{dummy_type}.const {random.randint(0,10)}\n', f'add {dummy_type}.{dummy_opcode}+'])
                    pt_body.append([f'{this_indent}{dummy_type}.{dummy_opcode}\n', f'add {dummy_type}.{dummy_opcode}'])
                    pt_body.append([f'{this_indent}drop\n', f'add {dummy_type}.{dummy_opcode}+'])
                    
            pt_body.append([this_line, ''])
        
        parsedSection['Function'][f].body = pt_body      

def convert_shift(parsedSection, _alpha, _beta, ratio=0):
    functions = parsedSection['Function']
    
    for f in functions:
        # if f != "41":
        #     continue
        
        shift_offset_list = list()
        this_body = functions[f].body
        
        for b_idx in range(0, len(this_body)):
            this_line = this_body[b_idx][0]
            if ("shl" in this_line) or ("shr" in this_line):
                if ("const" in this_body[b_idx-1][0]):
                    shift_offset_list.append(b_idx)
        
        if ratio != 0:
            iter = round(len(shift_offset_list)*ratio)
        else:
            iter = 1   
        
        target_lines = list()
        # print(len(shift_offset_list), iter)
        
        for _ in range(0, iter):
            target_line_offset = math.floor((len(this_body)-1)*state.get_dist(_alpha,_beta))
            # print(shift_offset_list)
            shift_line_offset = min(shift_offset_list, key=lambda x:abs(x-target_line_offset))
            shift_offset_list.remove(shift_line_offset)
            
            target_lines.append(shift_line_offset)
            
        for b_idx in target_lines:
            this_line = this_body[b_idx][0]
            this_type = retType(this_line)
            this_indent = retIndent(this_line)
            
            this_const =  int(this_body[b_idx-1][0].split(".const ")[1])
            
            parsedSection['Function'][f].body[b_idx-1] = [f"{this_indent}{this_type}.const {str(2**this_const)}\n","conv_shift+"]
            if "shl" in this_line:
                conv_line = f"{this_indent}{this_type}.mul\n"
            elif "shr" in this_line:
                if "_u" in this_line:
                    conv_line = f"{this_indent}{this_type}.div_u\n"
                elif "_s" in this_line:
                    conv_line = f"{this_indent}{this_type}.div_s\n"
            parsedSection['Function'][f].body[b_idx] = [conv_line,"conv_shift"]
            # print(b_idx)
            
def convert_xor(parsedSection, _alpha, _beta, ratio=0):
    
    with open('strategies/wasm_xor_rule.pkl', 'rb') as fr:
        xor_rules = pkl.load(fr)
    
    functions = parsedSection['Function']
    
    for f in functions:

        xor_offset_list = list()
        this_body = functions[f].body
        
        for b_idx in range(0, len(this_body)):
            this_line = this_body[b_idx][0]
            if ("xor" in this_line):
                xor_offset_list.append(b_idx)
        
        if ratio != 0:
            iter = round(len(xor_offset_list)*ratio)
        else:
            iter = 1   
        
        target_lines = list()
        for _ in range(0,iter):
            target_line_offset = math.floor((len(this_body)-1)*state.get_dist(_alpha,_beta))
            xor_line_offset = min(xor_offset_list, key=lambda x:abs(x-target_line_offset))
            xor_offset_list.remove(xor_line_offset)
            
            target_lines.append(xor_line_offset)
        
        pt_body = list()
        
        for b_idx in range(0, len(this_body)):
            this_line = this_body[b_idx][0]
            
            if b_idx in target_lines:
                pt_type = retType(this_line)
                pt_indent = retIndent(this_line)
                
                xor_rule = random.choice(xor_rules)
                this_indent = retIndent(this_line)
                
                # print(pt_type)
                insuff = len(state.EXTRA_GLOBALS[pt_type]) - 2
                while(insuff < 0):
                    state.add_global(parsedSection, pt_type)
                    insuff += 1 
                x_index = state.EXTRA_GLOBALS[pt_type][0]
                y_index = state.EXTRA_GLOBALS[pt_type][1]
                   
                pt_body.append([f'{this_indent}global.set {y_index}\n', 'convert_xor'])
                pt_body.append([f'{this_indent}global.set {x_index}\n', 'convert_xor+'])
                
                for x in xor_rule:
                    pt_body.append([pt_indent + x.replace('[type]',pt_type).replace('[x]',str(x_index)).replace('[y]',str(y_index))+'\n', 'convert_xor+'])
            else:
                pt_body.append([this_line, ''])
            
        parsedSection['Function'][f].body = pt_body       
        

def convert_or(parsedSection, _alpha, _beta, ratio=0):
    
    with open('strategies/wasm_or_rule.pkl', 'rb') as fr:
        or_rule = pkl.load(fr)
    or_rule = or_rule[0]
    
    functions = parsedSection['Function']
    
    for f in functions:

        or_offset_list = list()
        this_body = functions[f].body
        
        for b_idx in range(0, len(this_body)):
            this_line = this_body[b_idx][0]
            if ("xor" in this_line):
                or_offset_list.append(b_idx)
        
        if ratio != 0:
            iter = round(len(or_offset_list)*ratio)
        else:
            iter = 1   
        
        target_lines = list()
        for _ in range(0,iter):
            target_line_offset = math.floor((len(this_body)-1)*state.get_dist(_alpha,_beta))
            xor_line_offset = min(or_offset_list, key=lambda x:abs(x-target_line_offset))
            or_offset_list.remove(xor_line_offset)
            
            target_lines.append(xor_line_offset)
        
        pt_body = list()
        
        for b_idx in range(0, len(this_body)):
            this_line = this_body[b_idx][0]
            
            if b_idx in target_lines:
                pt_type = retType(this_line)
                pt_indent = retIndent(this_line)
                
                this_indent = retIndent(this_line)
                
                # print(pt_type)
                insuff = len(state.EXTRA_GLOBALS[pt_type]) - 2
                while(insuff < 0):
                    state.add_global(parsedSection, pt_type)
                    insuff += 1 
                x_index = state.EXTRA_GLOBALS[pt_type][0]
                y_index = state.EXTRA_GLOBALS[pt_type][1]
                   
                pt_body.append([f'{this_indent}global.set {y_index}\n', 'convert_or'])
                pt_body.append([f'{this_indent}global.set {x_index}\n', 'convert_or+'])
                
                for x in or_rule:
                    pt_body.append([pt_indent + x.replace('[type]',pt_type).replace('[x]',str(x_index)).replace('[y]',str(y_index))+'\n', 'convert_xor+'])
            else:
                pt_body.append([this_line, ''])
            
        parsedSection['Function'][f].body = pt_body       