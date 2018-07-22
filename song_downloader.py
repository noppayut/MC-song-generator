import os

from bs4 import BeautifulSoup
import urllib.request

""" ----------------- SET UP ----------------- """
# no set up needed if no necessary customization
sitename = "https://www.siamzone.com/music/thailyric/"
maxno = 14000 #default is fine
""" ------------------------------------------ """

savepath = os.getcwd()

def get_lyrics(soup):
	return soup.find(id="lyrics-content").text.replace('\r','').replace('\t','').strip()

def get_artist_and_trackname(soup):
	header = soup.find(itemprop="alternativeHeadline").text
	splittedhead = header.split('-')
	lhs = splittedhead[0]
	rhs = splittedhead[1]
	trackname = " ".join(lhs.split(' ')[1:]).strip()
	artist = rhs.strip()
	return artist, trackname

def main():
	for i in range(1, maxno+1):
		try:
			songurl = "%s%d"%(sitename, i)
			with urllib.request.urlopen(songurl) as response:
			    soup = BeautifulSoup(response, 'html.parser')
			    lyrics = get_lyrics(soup)
			    artist, trackname = get_artist_and_trackname(soup)
			    with open('%s\\raw\\%s.txt'%(savepath, str(i)), 'w', encoding='utf-8') as outfile:
			    	content = "%s\n%s\n\n%s"%(trackname, artist, lyrics)
			    	outfile.write(content)
			print("Downloaded song no.%d"%(i))
		except Exception as e:
			print(e)
			print("Song no.%d is unavailable. Skip"%(i))

if __name__ == "__main__":
	main()