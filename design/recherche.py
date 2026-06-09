
import time, random

arr = random.sample(range(1, 1000000), 999999)
# arr = [7, 3, 1, 5, 2, 4, 8, 9, 6]
arr.sort()
# print(arr, len(arr))
target = 989599


    
#####################################################################################################################""
#Recherche Linéaire iterative

def iterative_linear_research(arr: list[int], target: int) -> int:
    return [i for i in arr if i == target]


#Recherche Linéaire reccusrive MEMORY LIFO
def reccusrive_linear_research(arr: list[int], target: int, index: int  = 0):
    #Base case
    if index >= len(arr):
        return - 1
    #Base case
    if arr[index] == target:
        return target
    
    #Reccusrive case
    return reccusrive_linear_research(arr, target, index + 1)




#####################################################################################################################""
#Recherche Binaire with sorted list only

def binary_research(arr: list[int], target: int) -> int:
    start = 0
    end = len(arr) - 1
    
    while start <= end:
        middle = (end + start) // 2
        if arr[middle] == target :
            # print(arr[start:end+1])
            return middle
        elif arr[middle] > target:
            end = middle - 1
            # print(arr[:end+1], start, end)
        else :
            # print(arr[:middle])
            start = middle + 1
            # print(arr[start:], start, end)
        
    return -1
            
#####################################################################################################################""
#Recherche Par interpolation with sorted list only

def interpolation_research(arr: list[int], target: int) -> int:
    d = 0
    f = len(arr) - 1
    while arr[d] <= target <= arr[f] and d <= f:
        if arr[d] == arr[f]:
            if target == arr[d]:
                return d
            return -1
        
        position = d + int(((f - d) / (arr[f] - arr[d])) * (target - arr[d]))
        
        if arr[position] == target:
            return position
        elif arr[position] > target:
            f = position - 1
        else:
            d = position + 1
    return -1


#####################################################################################################################""

def main():
    start = time.time()
    print(interpolation_research(arr, target))
    finish = time.time() - start
    print(f"EXEC TIME >> [{finish}]")

#####################################################################################################################""


if __name__ == "__main__" :
    main()

