import re
import sys

"""
Sentence =  An 83-year-old woman with shortness of breath.

 TECHNIQUE:  Portable AP chest radiograph.

 COMPARISON:  The comparison is made with a prior chest radiograph dated
 [**2540-3-8**].

 FINDINGS:  The right IJ line, and nasogastric tube are unchanged compared to
 the prior study.  Mediastinal and cardiac contours are unchanged.  Note is
 made of increased bilateral pleural effusion, and increased interstitial
 edema.  Bilateral atelectasis is also noted.

 IMPRESSION:

 Worsening of bilateral effusion, pulmonary edema, due to CHF.  Bibasilar
 atelectasis.

Sample query = get_proximity_phrase(sentence, 'pulmonary edema', bilateral, 4, False/True)

"""


def get_proximity_phrase(sentence,word1,word2,number,order=True):
    sentence = sentence.lower()

    order = bool(order)
    number = int(number)

    iters1 = re.finditer(r"\b"+word1+r"\b", sentence)
    indices1 = [m.start(0) for m in iters1]
    iters2 = re.finditer(r"\b"+ word2 +r"\b", sentence)
    indices2 = [m.start(0) for m in iters2]

    phrases_caught = []
    bigger_word = []
    if len(word1) > len(word2):
        bigger_word.append(word1)
    else:
        bigger_word.append(word2)
    for x in indices1:
        for y in indices2:
            if order == True:
                if y > x:
                    phrases_caught.append(sentence[x:y+len(word2)])
                elif x == y:
                    phrases_caught.append(sentence[x:y+len(bigger_word[0])])
            if order == False:
                if y > x:
                    phrases_caught.append(sentence[x:y+len(word2)])
                elif x > y:
                    phrases_caught.append(sentence[y:x+len(word1)])
                elif x == y:
                    phrases_caught.append(sentence[x:y+len(bigger_word[0])])



    relevant_phrases = []
    for sent in phrases_caught:
        num_words_between = len(sent.split(' ')) - len(word1.split(' ')) - len(word2.split(' '))
        if num_words_between <= number:
            relevant_phrases.append(sent)


    return relevant_phrases


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if len(sys.argv) == 6:
            if sys.argv[5] == 'False':
                print(get_proximity_phrase(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],False))
            else:
                print('With default as True')
                print(get_proximity_phrase(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]))
        else:
            print(get_proximity_phrase(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]))

    else:
        raise SystemExit("Check inputs <name>")
