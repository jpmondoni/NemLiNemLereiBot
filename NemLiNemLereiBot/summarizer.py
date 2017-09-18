from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


class Summarizer:
    def __init__(self, language, sentences_count):
        self.language = language
        self.sentences_count = sentences_count

    def summarize(self, text):
        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        stemmer = Stemmer(self.language)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(self.language)
        sentences = []
        for sentence in summarizer(parser.document, self.sentences_count):
            sentences.append(str(sentence))
        return ' '.join(sentences)
