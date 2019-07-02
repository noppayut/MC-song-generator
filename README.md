# Thai song lyrics generator
An automatic lyrics generator using Markov chains

## Overview
The generator (built from Markov chains) consists of three MC models, namely `Intro`, `Body`, and `Outro` generators.
The models learn from their corresponding parts of songs, and generate only the part of lyrics they are assigned to.
Parts of the lyrics from each model are combined at the end to make a complete lyrics.

## Dependencies
* [Deepcut](https://github.com/rkcosmos/deepcut) (required Keras with Tensorflow backend)
* Numpy
* BeautifulSoup4

## File descriptions
* `song_downloader.py` - A script for downloading (scraping) lyrics from Siamzone.com
* `preprocessor.py` - A script for preprocessing the downloaded lyrics
* `song_generator.py` - A lyrics generator.

__Note__:
1. Make sure to run the above files in order. (in case of starting from scratch)
2. Each file requires path and parameter set up before start running. (in-file setup, no command line argument parsing)
3. Follow the description at each file's header on how to setup and technical details.

## Pre-trained model
Pre-trained model is a json file containing a dictionary that serves as state transition table for `Chain` class in `song_generator.py`.
The model is located in `\pretrained`.

Always set `use_pretrained` variable in `song_generator.py` `True` if you want to use this option.

## Result

### Successful case
![succeed](https://cdn-images-1.medium.com/max/1000/1*kLDMXK3LasrwiSG5r0_7hw.png)

### Failure case
![failed](https://cdn-images-1.medium.com/max/1200/1*VvlXW97h4Qq98eK5K2dEQA.png)
