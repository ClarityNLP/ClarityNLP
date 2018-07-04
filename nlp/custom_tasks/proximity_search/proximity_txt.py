import re
import numpy as np
import sys

def get_proximity_txt(sentence,word1,word2,number,order = True):
    new_sentence = sentence.lower()

    order = bool(order)
    number = int(number)


    new_word1 = '@'*len(word1)
    new_word2 = '$'* len(word2)
    #new_sentence = new_sentence.replace(word1,new_word1 + ' ')
    #new_sentence = new_sentence.replace(word2,new_word2 + ' ')
    new_sentence = re.sub(r'\b'+word1+r'\b',' '+new_word1+' ',new_sentence)
    new_sentence = re.sub(r'\b'+word2+r'\b',' '+new_word2+' ',new_sentence)
    word_array= np.asarray(new_sentence.split(' '))
    word_array= [x for x in word_array if x not in ['', ' ', ',','.','?','/','"','','!',"'",'-',']','[']]
    word_array= np.asarray(word_array)


    word1_pos = np.where(word_array== new_word1)[0]
    word2_pos = np.where(word_array== new_word2)[0]


    if order == False:
        all_distances = []
        for x in word1_pos:
            word_distance = word2_pos - x
            word_distance_unordered = abs(word_distance)
            all_distances.append(list(word_distance_unordered))
        all_distances_list = [j for i in all_distances for j in i]
        if len(all_distances_list) > 0:
            min_distance = min(all_distances_list)
        else:
            min_distance = float('inf')

    else:
        all_distances = []
        for x in word1_pos:
            word_distance = word2_pos - x
            word_distance_ordered = word_distance[word_distance > 0]
            all_distances.append(list(word_distance_ordered))
        all_distances_list = [j for i in all_distances for j in i]

        if len(all_distances_list) > 0:
            min_distance = min(all_distances_list)
        else:
            min_distance = float('inf')

    if min_distance <= number + 1:
        return True
    else:
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if len(sys.argv) == 6:
            if sys.argv[5] == 'False':
                print(get_proximity_txt(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],False))
            else:
                print(get_proximity_txt(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]))
        else:
            print(get_proximity_txt(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]))

    else:
        raise SystemExit("Check inputs <name>")
