from PartA import *

#Part B
''' Time Complexity:  O(max (n, m)) where n and m is the size of each dictionary since .keys() support set operations 
    checking membership is average O(1) per element in the smaller set O(min(mn, m)). 
    Pipelined operations function without call to print has cost O( max(m, n))
'''
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fileOne')
    parser.add_argument('fileTwo')
    args = parser.parse_args()
    
    fileOne = args.fileOne
    fileTwo = args.fileTwo

    result = pipelinedOperations(Tokenizer(), fileOne, fileTwo, print=False)
    print( len(result[0].keys() & result[1].keys()) ) 

if __name__ == '__main__':
    main()