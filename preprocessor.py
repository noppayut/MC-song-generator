# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 15:54:06 2018

@author: noppa
"""
import os

import deepcut
import string
import functools as ft

""" ----------------- SET UP ----------------- """
main_path = "[PROJECT_PATH]" + "\\"
path_to_files = main_path + "[FOLDER_NAME_CONTAINING_RAW_FILES]"
path_to_save = main_path + "[FOLDER_NAME_FOR_SAVING_PROCESSED_FILES]"
words_in_sentence_limit = 5 #used for determining sentence breaking
words_in_double_sentence = 15
token_type_dict = {'sentence': 's', 'phrase': 'p', 'double sentence': 'd'}
""" ------------------------------------------ """

class Lyrics:
    def __init__(self, lyrics):        
        self.lyrics = lyrics
   
    def break_sentence(self):
        """ break a line that contains two or more sentences
            the sentences will be written as new lines
        """
        def _determine_token_type(tokens):
            token_type = []
            tktype = None
            for token in tokens:
                tokenlength = len(deepcut.tokenize(token))
                if tokenlength > words_in_double_sentence:
                    tktype = token_type_dict['double sentence']
                elif tokenlength > words_in_sentence_limit:
                    tktype = token_type_dict['sentence']
                else :
                    tktype = token_type_dict['phrase']
                token_type.append(tktype)
            return token_type
        
        def _reconstruct_line(token_type_tuples):
            line = ""
            for pair in token_type_tuples:
                token = pair[0]
                tktype = pair[1]
                if tktype == token_type_dict['double sentence']:
                    sentences = deepcut.tokenize(token)
                    st1 = "".join(sentences[:int(len(sentences)/2)])
                    st2 = "".join(sentences[int(len(sentences)/2):])
                    line += "\n%s\n%s\n"%(st1, st2)
                    #print(line)
                elif tktype == token_type_dict['phrase']:
                    line += token + " "
                elif tktype == token_type_dict['sentence']:
                    line += "\n%s\n"%(token)
            ending = '\n' if line[-1] != '\n' else ''
            line = line[1:] if line[0] == '\n' else line
            return line + ending
        
        lr = self.lyrics        
        
        for i in range(len(lr)):            
            line = lr[i].replace('\n', '')
            linetokens = line.split(' ')
            token_type = _determine_token_type(linetokens)
            if token_type_dict['sentence'] in token_type:
                zipped = zip(linetokens, token_type)
                newline = _reconstruct_line(zipped)
                self.lyrics[i] = newline
            
            
    
    def remove_punctuations(self):
        """ remove punctuation """
        
        lr = self.lyrics
        for i in range(len(lr)):
            self.lyrics[i] = remove_punc(lr[i])
    
    def remove_multiple_singers(self):
        """ remove singers name included in the lyrics (if any) """
        lr = self.lyrics
        singerindicator = ':'
        for i in range(len(lr)):
            if singerindicator in lr[i]:
                self.lyrics[i] = lr[i].split(singerindicator)[1]
        
    def write_processed_lyrics(self, savepath):
        """ write processed lyrics to file """
        with open(savepath, 'w', encoding='utf-8') as savefile:            
            for line in self.lyrics:
                savefile.write("%s" % (line))

def remove_punc(line):
    pc = string.punctuation.replace(':', '')
    transtab = "".maketrans(pc, len(pc)*' ')
    return line.translate(transtab)            
    
def remove_beginning_metadata(rlyrics):
    """ remove metadata at the beginning of lyrics (if any) """
    paragraphmarker = '\n'
    metadata_indicator = ['เพลงประกอบภาพยนตร์', 
                          'คำร้อง', 
                          'คำร้อง/ทำนอง', 
                          'ทำนอง', 
                          'เรียบเรียง', 
                          'ร่วมร้องโดย',
                          'เพลงประกอบละคร',
                          'ร้องโดย'
                          ]
    
    firstparagraph = None
    count = 0
    for line in rlyrics:
        if line == paragraphmarker or count > 2:
            firstparagraph = rlyrics[:count]
            break
        count += 1
    
    #print(firstparagraph[0].split()[0].replace(':', "") in metadata_indicator)
    contain_meta = [remove_punc(line).split()[0].replace(":", '') in metadata_indicator for line in firstparagraph]
    ismeta = ft.reduce(lambda x, y: x | y, contain_meta)
       
    return rlyrics[count+1:] if ismeta else rlyrics 
        
    

def process_lyrics(sourcepath, savepath):
        rlyrics = None
        with open(sourcepath, 'r', encoding='utf-8') as sourcefile:
            rlyrics = sourcefile.readlines()[3:]        
        lyrics = Lyrics(remove_beginning_metadata(rlyrics))        
        lyrics.remove_punctuations()
        lyrics.remove_multiple_singers()
        lyrics.break_sentence()
        lyrics.write_processed_lyrics(savepath)
            

def main():
    """ main """
    allfiles = os.listdir(path_to_files)    
    writecount = 1
    for filename in allfiles:
        if writecount % 500 == 0 and writecount > 0:
            print("Processed %d files"%(writecount))
        process_lyrics(path_to_files + filename, path_to_save + filename)
        writecount += 1
    
    
if __name__ == "__main__":
    main()