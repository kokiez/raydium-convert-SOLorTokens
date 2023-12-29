from construct import  Int8ul
from construct import Struct as cStruct

POOL_INFO_LAYOUT = cStruct(
    "instruction" / Int8ul,
    "simulate_type" / Int8ul
)


