import numpy as np
from wasmParser import sectionStructure as ss

from pathlib import Path

file = Path(__file__).resolve()
package_root_directory = file.parents[1]

from wasmParser import parser

num_operand = {"add": 2, "sub":2, "mul": 2, "and": 2, "or": 2, "xor": 2, "shl": 2, "shr_s": 2, "shr_u": 2, "rotl": 2, "rotr": 2, \
       "lt": 2, "lt_s": 2, "lt_u": 2, "gt": 2, "gt_s": 2, "gt_u": 2, "le": 2, "le_s": 2, "le_u": 2, "ge": 2, "ge_s": 2, "ge_u": 2, \
               "ne": 2, "eqz": 1, "eq": 2, "neg": 1, \
                   "sqrt": 1, "min": 2, "max": 2, "copysign": 2, "abs": 1, "ceil": 1, "floor": 1, "nearest": 1
}
type_operand = {"add": ['i32', 'i64', 'f32', 'f64'], "sub": ['i32', 'i64', 'f32', 'f64'], "mul": ['i32', 'i64', 'f32', 'f64'], "and": ['i32', 'i64'], "or": ['i32', 'i64'], "xor": ['i32', 'i64'], "shl": ['i32', 'i64'], "shr_s": ['i32', 'i64'], "shr_u": ['i32', 'i64'], "rotl": ['i32', 'i64'], "rotr": ['i32', 'i64'], \
       "lt": ['f32', 'f64'], "lt_s": ['i32', 'i64'], "lt_u": ['i32', 'i64'], "gt": ['f32', 'f64'], "gt_s": ['i32', 'i64'], "gt_u": ['i32', 'i64'], "le": ['f32', 'f64'], "le_s": ['i32', 'i64'], "le_u": ['i32', 'i64'], "ge": ['f32', 'f64'], "ge_s": ['i32', 'i64'], "ge_u": ['i32', 'i64'], \
               "ne": ['i32', 'i64', 'f32', 'f64'], "eqz": ['i32', 'i64'], "eq": ['i32', 'i64', 'f32', 'f64'], "neg": ['f32', 'f64'], \
                   "sqrt": ['f32', 'f64'], "min": ['f32', 'f64'], "max": ['f32', 'f64'], "copysign": ['f32', 'f64'], "abs": ['f32', 'f64'], "ceil": ['f32', 'f64'], "floor": ['f32', 'f64'], "nearest": ['f32', 'f64']
}

stack_opcodes = {"add": [2, ["i32", "i64", "f32", "f64"]], "sub": [2, ["i32", "i64", "f32", "f64"]], "mul": [2, ["i32", "i64", "f32", "f64"]], "div": [2, ["f32", "f64"]], \
    "and": [2, ["i32", "i64"]], "or": [2, ["i32", "i64"]], "xor": [2, ["i32", "i64"]], "shl": [2, ["i32", "i64"]], "shr_s": [2, ["i32", "i64"]], "shr_u": [2, ["i32", "i64"]], "rotl": [2, ["i32", "i64"]], "rotr": [2, ["i32", "i64"]], \
       "lt": [2, ["f32", "f64"]], "lt_s": [2, "i32", "i64"], "lt_u": [2, "i32", "i64"], "gt": [2, ["f32", "f64"]], "gt_s": [2, "i32", "i64"], "gt_u": [2, "i32", "i64"], \
           "le": [2, ["f32", "f64"]], "le_s": [2, "i32", "i64"], "le_u": [2, "i32", "i64"], "ge": [2, ["f32", "f64"]], "ge_s": [2, "i32", "i64"], "ge_u": [2, "i32", "i64"], \
               "ne": [2, ["i32", "i64", "f32", "f64"]], "eqz": [1, ["i32", "i64"]], "eq": [2, ["i32", "i64", "f32", "f64"]], "neg": [1, ["f32", "f64"]]
}

non_stack_opcodes = ["unreachable", "nop", "block", "loop", "if", "else", "end", "br", "return", "call"]
stack_effect = {"br_if":-1, "br_table":-1, "call_indirect":-1, "drop":-1, "set":-1, "eq":-1, "ne":-1, \
                "lt_s":-1, "lt_u":-1, "gt_s":-1, "gt_u":-1, "le_s":-1, "le_u":-1, "ge_s":-1, "ge_u":-1, \
                "select":-2, "store":-2, "store8":-2, "store16":-2, \
                    "load":0, "load8":0, "load16":0, "load8_s":0, "load8_u":0, "load16_s":0, "load16_u":0, "load32_s":0, "load32_u":0, "grow":0, \
                        "eqz":0, 
                        "get":1, "size":1, "const":1}

crypto_opcodes = {"shr_u": [2, ["i32", "i64"]], "shr_s": [2, ["i32", "i64"]], "shl": [2, ["i32", "i64"]],  "xor": [2, ["i32", "i64"]],
}

non_crypto_opcodes = {"add": [2, ["i32", "i64", "f32", "f64"]], "sub": [2, ["i32", "i64", "f32", "f64"]], "mul": [2, ["i32", "i64", "f32", "f64"]], "div": [2, ["f32", "f64"]], \
    "and": [2, ["i32", "i64"]], "or": [2, ["i32", "i64"]], \
       "lt": [2, ["f32", "f64"]], "lt_s": [2, "i32", "i64"], "lt_u": [2, "i32", "i64"], "gt": [2, ["f32", "f64"]], "gt_s": [2, "i32", "i64"], "gt_u": [2, "i32", "i64"], \
           "le": [2, ["f32", "f64"]], "le_s": [2, "i32", "i64"], "le_u": [2, "i32", "i64"], "ge": [2, ["f32", "f64"]], "ge_s": [2, "i32", "i64"], "ge_u": [2, "i32", "i64"], \
               "ne": [2, ["i32", "i64", "f32", "f64"]], "eqz": [1, ["i32", "i64"]], "eq": [1, ["i32", "i64", "f32", "f64"]], "neg": [1, ["f32", "f64"]]
}

def getOpcodes(flag):
    if flag == 0:
        return crypto_opcodes
    elif flag == 1:
        return stack_opcodes
    elif flag == 2:
        return non_crypto_opcodes

#######Global
# DUMMY_GLOBAL_ADDED = False
LAST_GLOBAL_ID = 9999

DUMMY_GLOBALS = dict()
EXTRA_GLOBALS = {"i32":list(), "i64":list(), "f32":list(), "f64":list()}

ELEM_PARAMS = dict()

#############################

def get_dist(_alpha, _beta):
    
    rng = np.random.default_rng()
    
    return rng.beta(_alpha, _beta)
    
def add_global(parsedSection, pt_type):
    
    global LAST_GLOBAL_ID
    
    if LAST_GLOBAL_ID == 9999:
        globalIDs = list(parsedSection["Global"].keys())
        LAST_GLOBAL_ID= int(globalIDs[-1])
    
    # print(parsedSection['Global'][str(LAST_GLOBAL_ID)])
    this_indent = parser.retIndent(parsedSection['Global'][str(LAST_GLOBAL_ID)].line[0])
    
    EXTRA_GLOBALS[pt_type].append(LAST_GLOBAL_ID+1)
    # print(LAST_GLOBAL_ID)
    LAST_GLOBAL_ID += 1
    # print(LAST_GLOBAL_ID)
    
    new_global = f"{this_indent}(global (;{LAST_GLOBAL_ID};) (mut {pt_type}) ({pt_type}.const 0))\n"
    # print(new_global)
    parsedSection['Global'][str(LAST_GLOBAL_ID)] = ss.GLOBAL(line=[new_global,'+'])