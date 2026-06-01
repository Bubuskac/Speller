import json
import Io

class Dictionary:
    WORD_DICTIONARY = "words.json"

    def __init__(self):
        self.words = Io.load_file(self.WORD_DICTIONARY)
        
    def add_words(self, result, words, letter):
        for word in words[letter]:
            result["words"].append(word.replace("*", letter))
        return result
    
    def add_word(self, words, word, letter):
        if letter in word:
            words[letter].append(word.replace(letter, "*"))
        return words
    
    def remove_word(self, words, word, letter):
        if letter in word:
            words[letter].remove(word.replace(letter, "*"))
        return words
    
    def get_count(self):
        words = self.get_words()
        count_obj = { "count": len(words["ly"])  + len(words["j"])}
        return json.dumps(count_obj)
        
    def get_words(self):
        return self.words
    
    def get_word_list(self):
        result = {"words": []}
        result = self.add_words(result, self.words, "ly")
        result = self.add_words(result, self.words, "j")
        return json.dumps(result)
    
    def save_word(self, word):
        self.words = self.add_word(self.words, word, "ly")
        self.words = self.add_word(self.words, word, "j")
        Io.write_file(self.WORD_DICTIONARY, self.words)
        return json.dumps({"word": word})
    
    def delete_word(self, word):
        self.words = self.remove_word(self.words, word, "lY")
        self.words = self.remove_word(self.words, word, "j")
        Io.write_file(self.WORD_DICTIONARY, self.words)