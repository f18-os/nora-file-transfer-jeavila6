from sys import argv
import sys

prog_name = '()'
if len(argv):
    prog_name = argv[0]
    del argv[0]

switchesVarDefaults = ()


def parse_params(_switches_var_defaults):
    global switchesVarDefaults
    param_map = {}
    switchesVarDefaults = _switches_var_defaults
    sw_var_default_map = {}  # map from cmd switch to param var name
    for switches, param, default in switchesVarDefaults:
        for sw in switches:
            sw_var_default_map[sw] = (param, default)
        param_map[param] = default  # set default values
    try:
        while len(argv):
            sw = argv[0];
            del argv[0]
            param_var, default_val = sw_var_default_map[sw]
            if default_val:
                val = argv[0]
                del argv[0]
                param_map[param_var] = val
            else:
                param_map[param_var] = True
    except Exception as e:
        print('Problem parsing parameters (exception=%s)' % e)
        usage()
    return param_map


def usage():
    print('%s usage:' % prog_name)
    for switches, param, default in switchesVarDefaults:
        for sw in switches:
            if default:
                print(' [%s %s]   (default = %s)' % (sw, param, default))
            else:
                print(' [%s]   (%s if present)' % (sw, param))
    sys.exit(1)
