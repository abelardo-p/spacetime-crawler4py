from typing import Generator


def alphaNumeric(char: str) -> bool:
    return char >= 'A' and char <= 'Z' \
            or char >= 'a' and char <= 'z' \
            or char >= '0' and char <= '9'

class Tokenize:
    def __init__(self, input, stopWords=None, countWords=False):
        self.stopWords = stopWords if stopWords else set()
        self.countWords = countWords
        self.wordCount = 0
        self.tokens = {}
        self.tokenize(input, self.tokens)

    def getTotalWordCount(self):
        return self.wordCount
    
    def getTokens(self):
        return self.tokens
    
    def extractTokens(self, line: str) -> Generator[str, None, None]:
        left = 0
        for right, char in enumerate(line):
            if not alphaNumeric(char):
                if left < right and right - left > 1:
                    if self.countWords: self.wordCount += 1
                    yield line[left : right].lower()
                left = right +1
        
        if left < len(line) and len(line) - left > 1:
            if self.countWords: self.wordCount += 1
            yield line[left : len(line)].lower()

    def tokenize(self, input, tokenDict) -> None:
        for line in input:
            for token in self.extractTokens(line):
                if token in self.stopWords: continue
                if token in tokenDict:
                    tokenDict[token] += 1
                else:
                    tokenDict[token] = 1

    def print(self) -> None:
        frequency = lambda x: self.tokens[x]
        keys = sorted(self.tokens.keys(), key=frequency, reverse=True)
        for key in keys:
            print(key, self.tokens[key])


