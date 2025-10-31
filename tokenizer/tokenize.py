from typing import Generator

def alphaNumeric(char: str) -> bool:
    return char >= 'A' and char <= 'Z' \
            or char >= 'a' and char <= 'z' \
            or char >= '0' and char <= '9'

class Tokenize:
    def __init__(self, input):
        self.tokens = {}
        self.tokenize(input)

    def getTokens(self):
        return self.tokens
    
    def extractTokens(self, line: str) -> Generator[str, None, None]:
        left = 0
        for right, char in enumerate(line):
            if not alphaNumeric(char):
                if left < right and right - left > 1:
                    yield line[left : right].lower()
                left = right +1
        
        if left < len(line) and right - left > 1:
            yield line[left : ].lower()

    def tokenize(self, input) -> None:
        for line in input:
            for token in self.extractTokens(line):
                if token in self.tokens:
                    self.tokens[token] += 1
                else:
                    self.tokens[token] = 1

    def print(self) -> None:
        frequency = lambda x: self.tokens[x]
        keys = sorted(self.tokens.keys(), key=frequency, reverse=True)
        for key in keys:
            print(key, self.tokens[key])


