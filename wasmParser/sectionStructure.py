from dataclasses import dataclass

@dataclass
class sectionOffset:
    identifier:str = None
    startOffset:int = None
    bodyStartOffset:int = None
    endOffset:int = None

@dataclass
class TYPE:
    # identifier:str = None
    param:list = None
    result:list = None
    line:str = None
    
@dataclass
class IMPORT:
    funcID:str = None
    type:str = None
    line:str = None
    
@dataclass
class FUNCTION:
    type:str = None
    param:list = None
    result:list = None
    local:list = None
    header:list = None
    body:list = None
    
@dataclass
class GLOBAL:
    line:str = None
    
@dataclass
class EXPORT:
    funcID:str = None
    line:str = None
    
@dataclass
class ELEMENT:
    line:str = None

@dataclass
class DATA:
    line:str = None