path_name = "letterboxd_83k.txt"

# Current ALL word files are words_83k.txt and words_370k.txt
def load_words(path,case="lower"):
    try:
        with open("words/"+path) as word_file:
            words = set(word_file.read().split())
        if case=="lower":
            words = [word.lower() for word in words]
        if case=="upper":
            words = [word.upper() for word in words]
        return words
    except FileNotFoundError:
        print(f"Error: The file '{'word'+path}' does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def save_words(words, path):
    with open("words"+path, 'w') as file:
        for word in words:
            file.write(word.lower() + '\n')

def is_letterboxd_word(word):
    if len(word) <= 2 or len(word) >= 15:
        return False
    for i in range(len(word)-1):
        if word[i] == word[i+1]:
            return False
    return True

if __name__ == '__main__':
    words = load_words("words_83k.txt")
    filtered = [word for word in words if is_letterboxd_word(word)]
    save_words(sorted(filtered), path_name)
    print("done")
