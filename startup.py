import pandas as pd
from lib import list_functions
import platform

print(platform.system())
print(platform.version())
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def foo (x,y,z):
    return(x+y+z)

print(foo(10,11,12))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Vijay')

##Pandas Dataframes
df = pd.read_csv('data.csv')
#Drop header
#print(df)
df.drop_duplicates(subset=['Duration'] , keep=False)
#print (df.to_string())
#df.to_csv
df['Date'] = pd.to_datetime(df['Date'])
df = df.assign(Hour = lambda x: (x['Duration'] /60))
#print((df.duplicated()).to_string())

for x in df.index:
        if df.loc[x,"Calories"] > 100:
           df.loc[x,"Calories"] = 1

#print (df.to_string())
df.to_csv("health.csv")
##List
fruits = ["apple", "banana", "cherry","Alpha"]
#fruits = []
fruits_copy = fruits
print(fruits)
fruits.sort()
print(fruits)
fruits.reverse()
print(fruits)
#fruits.remove("banana")
print(fruits)
print(fruits_copy)

print(type(fruits))

#Call List Functions
sublist=list_functions.split_list(fruits)
print(sublist)

list_functions.number_list_functions()

for x in fruits:
  print(x)

x=lambda a,b:a+b
print(x(4,5))

#input = input()

print(input)
words = ["Artificial", "Intelligence"]
output = "".join([w[0].upper() for w in words])
print(output)

numbers = [str((x+1)*2) for x in range(0,10,2) if x > 5]
print("".join(numbers))

for x in range(0,10,2):
    print(x)

dict = {'abc': 1, 'bcd': 3, 'cde': 5}
print({k.upper(): v**2 for (k, v) in dict.items()})
print(dict)

def check(word):
    if word:
        return True
        return False

words =["home", "", "pen", None, "Nick"]

print(list(filter(check, words)))

#list slicing
word = "Machine Learning"
text = word.split()
print("".join([i[0].upper() for i in text]))

number = 2.3148546432234
print(str(number).split(".")[1][4])


numbers = [2,6]
print(list(range(*numbers)))