# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 23:28:04 2018

@author: noppa
"""

import os
import json
import numpy as np
import deepcut as dc

main_path = "C:\\Users\\noppa\\Desktop\\Free project\\Song generator\\"
path_to_files = main_path + "test\\"
path_to_stopword = main_path + "stopwords-th.txt"
initial_word = "ฉัน"
song_chunk_names = ['intro', 'body', 'outro']
bodyratio = 0.7
illegal_initials = ['ๆ']
use_pretrained = True
pretrained_name = "pretrained\\chain-trained.json"

class Song:
    def __init__(self, lyricschunks):
        no_chunk = len(list(filter(lambda x: x is '\n', lyricschunks))) + 1        
        bodystart, bodyend = calculate_song_proportion(no_chunk)
        
        filtered_lyrics = list(filter(lambda x: not (x is '\n'), lyricschunks))        
        lyrics_chunks = [filtered_lyrics[:bodystart], filtered_lyrics[bodystart: bodyend], filtered_lyrics[bodyend:]]
        
        self.lyrics = {k:v for (k, v) in zip(song_chunk_names, lyrics_chunks)}        

def calculate_song_proportion(no_chunk):
    no_bodychunk = int(round(no_chunk*bodyratio))
    no_introchunk = max(1, no_chunk - no_bodychunk)
    
    bodystart = no_introchunk
    bodyend = no_introchunk + no_bodychunk 
    if no_chunk - bodyend <= 0:
        bodyend = no_chunk - 1
    return bodystart, bodyend
            
    
class Chain:
    def __init__(self):
        self.name = "Markov Chain"
        self.learned = False
        self.chain = {k:v for (k, v) in zip(song_chunk_names, [{}, {}, {}])}
    
    def train(self, songlist):
        """ learn from songs """
        print("Training...")
        for song in songlist:
            self._train(song)
        with open(main_path + pretrained_name, 'w', encoding='utf-8') as pretrained_file:
            json.dump(self.chain, pretrained_file)
        #np.save(main_path + pretrained_name, self.chain)
        self.learned = True
        print("Finished training")
    
    def load_pretrained(self):
        with open(main_path + pretrained_name, 'r', encoding='utf-8') as pretrained_file:
            self.chain = json.load(pretrained_file)
        #np.load(main_path + pretrained_name).item()
        self.learned = True
    
    def _train(self, song):
        """ learn from a song """
        for chunk_name in song_chunk_names:
            self._update_chain(chunk_name, song.lyrics[chunk_name])
        
    def _update_chain(self, chain_name, sentences):
        """ update a chain specified by chain_name """
        for sentence in sentences:
            st = sentence.replace('\n', '').replace(' ','')
            tokens = dc.tokenize(st)
            bigrams = bigram(tokens)
            for (b1, b2) in bigrams :
                if b1 in self.chain[chain_name]:
                    if b2 in self.chain[chain_name][b1]:
                        self.chain[chain_name][b1][b2] += 1
                    else:
                        self.chain[chain_name][b1][b2] = 1
                else:
                    self.chain[chain_name][b1] = {b2: 1}
        
    def compose(self, initial=None):
        """ compose a song using learned chain """
        def sample_initial(choices):
            legal_choices = list(filter(lambda x: not x in illegal_initials, choices))
            return np.random.choice(legal_choices)
        if not self.learned:
            print("Train the model first")
            return
        if not initial:                        
            initial = sample_initial(list(self.chain['intro'].keys()))
        
        total_no_chunks = np.random.choice(range(6,10))
        bodystart, bodyend = calculate_song_proportion(total_no_chunks)
        
        no_intro = bodystart - 1
        no_body = bodyend - bodystart
        no_outro = total_no_chunks - no_body - no_intro
        
        intro_raw, keywords = self._compose(initial, 'intro', no_intro)
        keyword_keys = list(keywords.keys())
        body_initial = sample_initial(keyword_keys)
        body_raw, body_kw = self._compose(body_initial, 'body', no_body, keywords)
        keyword_keys.remove(body_initial)
        
        
        if len(keyword_keys) == 0:
            outro_initial = sample_initial(list(self.chain['outro'].keys()))
        else:
            outro_initial = sample_initial(keyword_keys)
        outro_raw, outro_kw = self._compose(outro_initial, 'outro', no_outro, keywords)
        print('--------------------------')
        print(intro_raw)
        print('--------------------------')
        print(body_raw)
        print('--------------------------')
        print(outro_raw)
        print('--------------------------')
        return format_song(intro_raw, body_raw, outro_raw)
        
    def _compose(self, initial, chain_name, no_chunks, bias_dict=None):        
        sentence_length = np.random.choice(range(6,8))
        chunk_length = np.random.choice(range(4,6))
        lines = []
        words = []        
        for i in range(no_chunks):
            sentence_start = initial
            for j in range(chunk_length):                
                line = self.sample(chain_name, sentence_start, sentence_length, bias_dict=bias_dict)                
                sentence_start = np.random.choice(line)
                words += line
                lines.append(line)
            lines.append('\n')
        return lines, get_keywords(words)
   
    def sample(self, chain_name, initial, sentence_length, bias_dict=None):                
        def _sample(a_dict, word, bias_dict=None):            
            choices = list(a_dict[word].keys())
            prob = calculate_probs(a_dict[word], bias_dict=bias_dict)
            #print(choices, prob)
            word = np.random.choice(choices, p=prob)
            return word
        min_word_per_line = 3
        
        if not (initial in self.chain[chain_name]):
            initial = np.random.choice(list(self.chain[chain_name].keys()))
        line = [initial]
        sampling_word = initial
        count = 0
        while count <= sentence_length:
            word = _sample(self.chain[chain_name], sampling_word, bias_dict=bias_dict)            
            if word == "EOS":
                if len(line) > min_word_per_line:
                    break
                else:
                    word = sampling_word
            else:
                sampling_word = word
            line.append(word)
            count += 1
        return line

def format_song(intro, body, outro):
    n_intro = '\n'.join([''.join(line) for line in intro])
    n_body = '\n'.join([''.join(line) for line in body])
    n_outro = '\n'.join([''.join(line) for line in outro])
    
    return ("%s\n%s\n%s"%(n_intro, n_body, n_outro)).replace('EOS','')

def calculate_probs(a_dict, bias_dict=None):
    repopulated_dict = a_dict
    if bias_dict:
        for word in repopulated_dict:
            if word in bias_dict:
                repopulated_dict[word] *= (1 + 0.2*bias_dict[word])
    population = repopulated_dict.values()
    counts = sum(population)
    return list(map(lambda x: float(x)/counts, population))
        
def bigram(tokens):
    bigrams = []
    for i in range(len(tokens)-1):
        bigrams.append((tokens[i], tokens[i+1]))
    bigrams.append((tokens[-1], 'EOS')) #end of sequence, indicates that this word usually ends the sentence
    return bigrams

def get_keywords(words):
    word_counts = {}
    stopwords = get_stopwords()
    for word in words:
        if word in stopwords:
            continue
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    return word_counts

def get_stopwords(path=path_to_stopword):
    """ return stopwords """
    stpw = None
    with open(path, 'r', encoding='utf-8') as stpwfile :
        stpw = list(map(lambda x: x[:-1], stpwfile.readlines()))
    return stpw

def make_song_list(path=path_to_files):
    """ make a list of Song objects """
    allfiles = os.listdir(path)
    songlist = []
    for f in allfiles:
        with open(path+f, 'r', encoding='utf-8') as songfile:
            raw_lyrics = songfile.readlines()
            p_lyrics = list(map(lambda x: x if x is '\n' else x.replace('\n', ''), raw_lyrics))
            p_lyrics = p_lyrics[1:] if p_lyrics[0] == '\n' else p_lyrics
            songlist.append(Song(p_lyrics))
    return songlist

def main():
    """ main """
    songlist = make_song_list()
    generator = Chain()
    if use_pretrained:
        print("Use pretrained model")
        generator.load_pretrained()
    else:        
        generator.train(songlist)
    generated_song = generator.compose(initial=initial_word)

    print(generated_song)

if __name__ == "__main__":
    main()
