##Module with List functions
import sys


def split_list (list):
    print("Inside Split_list splitting the list:",list)
    if not list:
        print("List is empty so exiting")
    else:
        print("List is not empty so not exiting")
        #sys.exit(0)
    return (list[0:2])

def number_list_functions():
    numlist=[1,2,3,4,5]
    print("Inside number_list_functions")
    print(numlist.append(1))
