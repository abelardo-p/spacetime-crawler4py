import argparse
from pathlib import Path
from typing import Generator


# Part A

''' Time Complexity: O(1) contstant time to check if character in alphabet or number range'''
def alphaNumeric(char: str) -> bool:
    return char >= 'A' and char <= 'Z' \
            or char >= 'a' and char <= 'z' \
            or char >= '0' and char <= '9'

class Tokenizer:

    ''' Time Complexity: O(n) where n is the number of chars in the input string as each character is visited at most once in the loop'''
    def getTokens(self, line: str) -> Generator[str, None, None]:
        left = 0
        for right, char in enumerate(line):
            if not alphaNumeric(char):
                if left < right and left:
                    yield line[left : right].lower()
                left = right +1
        
        if left < len(line):
            yield line[left : ].lower()

    ''' Time Complexity: O(n) where n is the number of characters in the input file as each line is visited at most ounce in the loop'''
    def tokenize(self, path: str) -> list[str]:
        tokens = []
        path = Path(path)
        try:
            with path.open(encoding='utf-8', errors='replace') as file:
                for line in file:
                    tokens.extend(self.getTokens(line))
        except OSError:
            print(f"Could not open file: {path}")
        finally:
            return tokens
    
    ''' Time Complexity: O(n) where n is the number of tokens in the input list as each token is visited 
        once and lookups along with insertions in a dictionary have an average cost of O(1)
    '''
    def computeWordFrequencies(self, tokens: list[str]) -> dict[str, int]:
        tokenMap = {}
        for token in tokens:
            if token in tokenMap:
                tokenMap[token] += 1
            else:   
                tokenMap[token] = 1
        return tokenMap
    
    ''' Time Complexity: O(n * log(n)) where n is the number of entrys in the dictionary. 
        Since the output needs to be in descending order of frequency it must be sorted which costs n * log(n)
    '''
    def print(self, frequencies: dict[str: int]) -> None:
        frequency = lambda x: frequencies[x]
        keys = sorted(frequencies.keys(), key=frequency, reverse=True)
        for key in keys:
            print(key, frequencies[key])

''' Time Complexity: O(m * log(m)) all function calls excluding print have cost less than or equal to O(n) where n is the number of characters
    in the input files as each character is visited at least once but not more than C times where C is some small constant. 
    However print requires the dictionary of tokens to be sorted which costs O(m * log(m)) and m <= n where m is the number of tokens.
'''
def pipelinedOperations(tokenizer: Tokenizer, *args, print=True) -> list[dict[str: int]]:
    results = [0] * len(args)
    for index, path in enumerate(args):
        results[index] = tokenizer.tokenize(path)
        results[index] = tokenizer.computeWordFrequencies(results[index])
        if print: tokenizer.print(results[index])
    return results

''' Time Complexity: O(m * log(m)) all function calls excluding print have cost less than or equal to O(n) where n is the number of characters
    in the input files as each character is visited at least once but not more than C times where C is some small constant. 
    However print requires the dictionary of tokens to be sorted which costs O(m * log(m)) and m <= n where m is the number of tokens.
'''
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fileOne')
    args = parser.parse_args()

    fileOne = args.fileOne
    pipelinedOperations(Tokenizer(), fileOne)

if __name__ == '__main__':
    main()