from pylint import epylint as lint
import json

#format the raw std_out,
#returns a list of message dictionaries
def convertMSG(std_out, print_raw=False, print_stripped=False):
    rawStr = std_out.getvalue()
    if print_raw:
        print("This is the Raw output")
        print(rawStr)
    stripped = rawStr.replace("[", "").replace("]","").split('},\n')
    for i in range(len(stripped)):
        stripped[i] = stripped[i].replace("\n", "").replace("         ", " ")
    if print_stripped:
        print("This is the stripped output")
        for s in stripped:
            print(s + "\n")

    #We'll be missing }, this tacks them back on
    result = []
    if len(stripped) == 1:
        result.append(json.loads(stripped[0]))
        return result
    for i in range(len(stripped) - 1):
        result.append(json.loads(stripped[i] + '}'))
    #A trailing } is on the final entry
    result.append(json.loads(stripped[len(stripped) - 1]))
    return result

#take in string names of modules to be linted
def apply(*args, print_raw=False, print_stripped=False):
    assert len(args) > 0
    opts = ""
    for arg in args:
        opts = opts + arg + " "
    opts = opts + "--output-format=json"
    a = lint.py_run(command_options=opts, return_std=True)
    return convertMSG(a[0], print_raw, print_stripped)