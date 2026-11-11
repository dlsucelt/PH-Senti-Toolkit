import re

class Tokenizer:
    def __init__(self):
        # Define patterns
        self.userhandle_pattern = r'@\w+'
        self.url_pattern = r'http\S+|www\.\S+|t.co//w+'
        self.time_pattern = r'\b\d{1,2}:\d{2}\s?(?:am|pm|AM|PM)?\b'
        self.phone_pattern = r'\b(?:\+?\d{1,3})?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
        self.number_pattern = r'\b\d+\b'
        self.repeating_chars_pattern = r'([a-zA-Z])\1{2,}'
        self.emoticon_pattern = r':\)|:\(|:D|:P|;P|:\*|<3|</3|:\'\(|:\'|:\||:-?o|:-?\(|:-?\)|;-?\)|>-?<|:O|:\['
        self.token_pattern = fr'<USERHANDLE>|<URL>|<TIME>|<PHONENUMBER>|<NUMBER>|#\w+|{self.emoticon_pattern}|\w+\'\w+|\w+[-\w]+|\b\w+\b|[^\w\s]'

    def tokenize(self, text):
        # Replace user handles with <USERHANDLE>
        text = re.sub(self.userhandle_pattern, '<USERHANDLE>', text)

        # Replace URLs with <URL>
        text = re.sub(self.url_pattern, '<URL>', text)

        # Replace time expressions with <TIME>
        text = re.sub(self.time_pattern, '<TIME>', text)

        # Replace phone numbers with <PHONENUMBER>
        text = re.sub(self.phone_pattern, '<PHONENUMBER>', text)

        # Replace generic numbers with <NUMBER>
        text = re.sub(self.number_pattern, '<NUMBER>', text)

        # Reduce repeating characters greater than or equal to three to three
        text = re.sub(self.repeating_chars_pattern, r'\1\1\1', text)

        # Split text into tokens
        tokens = re.findall(self.token_pattern, text)

        # Lowercase tokens except those in uppercase
        processed_tokens = []
        for token in tokens:
            if not token.isupper():
                processed_tokens.append(token.lower())
            else:
                processed_tokens.append(token)

        return processed_tokens