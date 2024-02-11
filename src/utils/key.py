import random


class Key:
    '''класс для генерации ключа формата XXXXX-XXXXX-XXXXX-XXXXX-XXXXX'''
    
    def generate(self):
        key = ''
        portion = ''
        characters = 'abcdefghijklmnopqrstuvwxyz0123456789'

        while True:
            while len(key) < 30:
                character = random.choice(characters) 
                key += character 
                portion += character
                if len(portion) == 5:
                    key += '-'
                    portion = ''

            key = key[:-1]
            if self.verify(key):
                return key.upper()
            else:
                key = ''

    def verify(self, key):
        total = 0
        main_character = key[0]
        main_character_count = 0
        portions = key.split('-')
        for portion in portions:
            if len(portion) != 5:
                return False
            else:
                for character in portion:
                    if character == main_character:
                        main_character_count += 1 
                    total += ord(character)
      
        if total == 2227 and main_character_count == 3:
            return True
        return False


if __name__ == "__main__":
    key = Key()
    print(key.generate())