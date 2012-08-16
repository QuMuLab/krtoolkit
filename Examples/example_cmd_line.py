#File:        example_cmd_line.py
#Author:      Nathan Robinson
#Contact:     nathan.m.robinson@gmail.com
#Date:        2012-08-15
#Desctiption: An example of the command line processor with a built in help function.

import sys
from cmd_line import ArgProcessor, ArgDefinition, FlagDefinition,\
    range_validator, enum_validator, bool_validator, InputException



def print_citation_info(arg_processor):
    print "When citing this planner please use the following publication:"
    print "TBA"
    sys.exit(0)

def process_args():
    arg_processor = ArgProcessor()
    
    arg_processor.add_program_arg('-req_str_arg',
        ArgDefinition('required_string_argument',
            True,
            None,
            None,
            None,
            "A required string argument with no validator"))
    
    arg_processor.add_program_arg('-opt_str_arg',
        ArgDefinition('optional_string_argument',
            False,
            None,
            None,
            None,
            "An optional string argument with no validator and a default value of None"))
   
    arg_processor.add_program_arg('-opt_bool_arg',
        ArgDefinition('optional_boolean_argument',
            False,
            bool_validator,
            ["Error - invalid opt_bool_arg setting:"],
            True,
            "An optional Boolean argument with True as a default value"))

    arg_processor.add_program_arg('-opt_enum_arg',
        ArgDefinition('optional_enumerated_argument',
            False,
            enum_validator,
            [['value1', 'value2', 'value3'], "Error - invalid opt_enum_arg value:"],
            'value4',
            "An optional enumerated argument with three values and a default of 'value4'"))
    
    arg_processor.add_program_arg('-opt_int_arg',
        ArgDefinition('optional_integer_argument',
            False,
            range_validator,
            [int, 0, None, True, "Error - invalid integer argument:"],
            None,
            "An optional integer argument with a lower bound of 0 and no upper bound and a default of None"))
    
    arg_processor.add_program_arg('-opt_float_arg',
        ArgDefinition('required_float_argument',
            False,
            range_validator,
            [float, 0, 1, False, "Error - invalid floating point argument:"],
            None,
            "An optional floating point argument with a lower bound of 0 and an upper bound of 1"))
    
    arg_processor.add_program_flag('--cite',
        FlagDefinition('cite',
            print_citation_info,
            "Display citation information"))
    
    try:
        arg_processor.parse_args()
    except InputException as e:
        print e.message
        print "Use --help flag to display usage information."
        sys.exit(1)
    return arg_processor


if __name__ == '__main__':
    process_args()


