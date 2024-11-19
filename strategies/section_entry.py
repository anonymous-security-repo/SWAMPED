from strategies import state
import math
import random
import re
from wasmParser.parser import retIndent
from wasmParser import sectionStructure as ss

RE_TYPE_ID = re.compile("\(type\s(\d+)\)")

def add_type(parsedSection, _alpha, _beta, ratio=0):
    
    types = parsedSection['Type']
    
    cur_types = list()
    
    for t in types:
        cur_types.append([types[t].param, types[t].result])
    type_indent = retIndent(types[t].line[0])
    type_template_P = type_indent+"(type (;{id};) (func (param {param})))\n"
    type_template_R = type_indent+"(type (;{id};) (func (result {result})))\n"
    type_template_PR = type_indent+"(type (;{id};) (func (param {param}) (result {result})))\n"
        
    if ratio != 0:
        iter = round(len(cur_types)*ratio)
    else:
        iter = 1
    
    target_lines = dict()
    for _ in range(0,iter):
        target_line_offset = math.floor((len(cur_types)-1)*state.get_dist(_alpha,_beta))
        if target_line_offset not in target_lines:
            target_lines[target_line_offset] = 1
        else:
            target_lines[target_line_offset] += 1
    # print(cur_types)
    
    pt_TYPE = dict()
    new_type_id = 0
    type_id_dict = dict()
    
    for offset, origin_type_id in enumerate(types.keys()):
        this_line = types[origin_type_id].line[0]
        
        if offset in target_lines:
            
            for _ in range(0, target_lines[offset]):
                pt_param = types[origin_type_id].param
                pt_result = types[origin_type_id].result
            
                is_unique = False
                
                while(not is_unique):
                    pt_insert = random.choice(['P', 'R'])
                    pt_OPtype = random.choice(["i32", "i64", "f32", "f64"])
                    if pt_insert == 'P':
                        pt_param = pt_param + f" {pt_OPtype}" if pt_param is not None else pt_OPtype
                    if pt_insert == 'R':
                        pt_result = pt_result + f" {pt_OPtype}" if pt_result is not None else pt_OPtype
                    
                    if [pt_param, pt_result] in cur_types:
                        continue
                    else:
                        is_unique = True
                
                if pt_param is not None:
                    if pt_result is None:
                        pt_line = type_template_P.format(id=new_type_id, param=pt_param)
                    else:
                        pt_line = type_template_PR.format(id=new_type_id, param=pt_param, result=pt_result)
                else:
                    pt_line = type_template_R.format(id=new_type_id, result=pt_result)
                    
                pt_TYPE[str(new_type_id)] = ss.TYPE(param=pt_param, result=pt_result, line=[pt_line, 'add_type'])
                new_type_id += 1
                # print(pt_line)
        
        this_line = types[origin_type_id].line[0]
        pt_TYPE[str(new_type_id)] = types[origin_type_id]
        pt_TYPE[str(new_type_id)].line[0] = this_line.replace(f";{origin_type_id};", f";{str(new_type_id)};")
        type_id_dict[origin_type_id] = str(new_type_id)
        
        new_type_id += 1
        
    parsedSection['Type'] = pt_TYPE
    
    for i in parsedSection['Import']:
        if parsedSection['Import'][i].type in type_id_dict.keys():
            
            this_type = parsedSection['Import'][i].type
            this_line = parsedSection['Import'][i].line[0]
            pt_type = type_id_dict[this_type]
            
            parsedSection['Import'][i].type = type_id_dict[parsedSection['Import'][i].type]
            parsedSection['Import'][i].line[0] = this_line.replace(f"type {this_type}", f"type {pt_type}")
            # line[1] 수정?
    
    for f in parsedSection['Function']:
        if parsedSection['Function'][f].type in type_id_dict.keys():
            
            this_type = parsedSection['Function'][f].type
            this_header = parsedSection['Function'][f].header
            pt_type = type_id_dict[this_type]
            
            parsedSection['Function'][f].type = type_id_dict[parsedSection['Function'][f].type]
            
            for h_idx in range(0, len(this_header)):
                this_line = this_header[h_idx][0]
                parsedSection['Function'][f].header[h_idx][0] = this_line.replace(f"type {this_type}", f"type {pt_type}")
        
        this_body = parsedSection['Function'][f].body
        for b_idx in range(0,len(this_body)):
            
            matchTypeId = re.search(RE_TYPE_ID, this_body[b_idx][0])
            if matchTypeId:
                # print(this_body[b_idx][0])
                this_type = matchTypeId.group(1)
                pt_type = type_id_dict[this_type]
                parsedSection['Function'][f].body[b_idx][0] = this_body[b_idx][0].replace(f"type {this_type}", f"type {pt_type}")
                # print(parsedSection['Function'][f].body[b_idx][0])
                
    
def add_data(parsedSection, _alpha, _beta, ratio=0):
    #check data referencing area
    #synthesize data memory location
    datas = parsedSection['Data']
    backslash = "\\"
        
    # print(list(datas.keys())[-1])
    
    pt_DATA = dict()
    
    if ratio != 0:
        iter = round(len(datas)*ratio)
    else:
        iter = 1
        
    target_lines = dict()
    for _ in range(0,iter):
        target_line_offset = math.floor((len(datas)-1)*state.get_dist(_alpha,_beta))
        if target_line_offset not in target_lines:
            target_lines[target_line_offset] = 1
        else:
            target_lines[target_line_offset] += 1
    
    # print(target_lines)
    data_indent = "  "
    this_dataID = 0
    for offset, origin_data_id in enumerate(datas.keys()):
        this_line = datas[origin_data_id].line[0]
        
        frags = this_line.split('"')[1]
        frags = frags.split("\\")[1:]
        
        if offset in target_lines:
            
            for _ in range(0, target_lines[offset]):
            
                random.shuffle(frags)
                pt_DATA[str(this_dataID)] = ss.DATA(line=[f'{data_indent}(data (;{this_dataID};) (i32.const 0) "{backslash}{(backslash).join(frags)}")', "add_data"])
                
                this_dataID += 1
                
        pt_DATA[str(this_dataID)] = ss.DATA(line=[this_line.replace(f"(;{origin_data_id};)", f"(;{this_dataID};)"), "add_data"])
        this_dataID += 1
            # for _ in range(0, target_lines[offset]):
    
    parsedSection['Data'] = pt_DATA