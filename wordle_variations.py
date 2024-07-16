import wordle_graph as wg
import numpy as np

def is_anagram(w1, w2):
    if len(w1)!=len(w2):
        return False
    a1 = [l for l in w1]
    a2 = [l for l in w2]
    for i in range(len(a1)):
        if a1[i] in a2:
            j=a2.index(a1[i])
            a2[j] = "!"
        else:
            return False
    return True

def anagram_free(word_arr):
    d = {}
    afw = []
    for w in word_arr:
        d[w] = w
    for w in word_arr:
        if d[w] is None:
            continue
        d[w] = None
        afw.append(w)
        for wp in word_arr:
            if is_anagram(w,wp):
                d[wp]=None
    return afw

def graph_afw(graph = None):
    guess_words = wg.guess_words
    possible_words = wg.possible_words
    if graph is None:
        graph = wg.load_graph()
    gg={}
    afw = []
    guesses = graph.keys()
    for word in guesses:
        gg[word] = word
    for word in guesses:
        if gg[word] is not None:
            afw.append(word)
            gg[word] = None
            for s in graph[word].keys():
                if "B" not in s:
                    for a in graph[word][s]:
                        gg[a] = None
    return afw
