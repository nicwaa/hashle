import string
import requests
from colorama import Fore
import random
import hashlib

with open('./rockyou.txt', errors='ignore') as f:
    rockyou = f.read().split('\n')
ry_with_hash = []
for word in rockyou:
    ry_with_hash.append((word, hashlib.md5(word.encode()).hexdigest()))

link = 'http://io6.ept.gg:32803'
response = requests.get(f"{link}/api/session")
token = response.json()["token"]

alphanum = string.digits + 'abcdef'
error = False
level = 1
first = True
inner = False
flag = False

while not flag:
    if error:
        response = requests.get(f"{link}/api/session")
        token = response.json()["token"]
        error = False
        first = True
        inner = False
    password = random.choice(ry_with_hash)[0]
    banned_words = set()
    banned_words.add(password)
    green = dict()
    yellow = dict()
    gray = set()
    yellow_list = list()
    for symbol in alphanum:
        yellow[symbol] = {
            'count': 0,
            'gray': False
        }

    try:
        if first:
            payload = {
                'token': f'{token}',
                'password': password
            }
            response = requests.post(f"{link}/api/guess", json=payload)
            current_guess_json = response.json()
            first = False

        for count in range(current_guess_json['max_attempts']):

            if inner:
                payload = {
                    'token': f'{token}',
                    'password': password
                }
                response = requests.post(f"{link}/api/guess", json=payload)
                current_guess_json = response.json()

            if (current_guess_json.get('attempt') == 1) or not inner:
                print(f'======================== LEVEL: {current_guess_json.get("level")} ========================')
            for member in current_guess_json['hash']:
                if member['hint'] == 'green':
                    print(Fore.GREEN, member['char'], end='')
                elif member['hint'] == 'yellow':
                    print(Fore.YELLOW, member['char'], end='')
                elif member['hint'] == 'none':
                    print(Fore.RED, member['char'], end='')
            print(Fore.RESET)

            token = current_guess_json['token']

            for i, hash_data in enumerate(current_guess_json['hash']):
                hint = hash_data['hint']
                char = hash_data['char']
                if (hint == "green") and (i not in green.keys()):
                    green[i] = char
                elif (hint == "yellow") and not any(char in tpl[0] for tpl in gray):
                    yellow_list.append((char, i))
                    yellow[char]['count'] += 1
                elif (hint == "none") and (yellow[char]['count'] == 0):
                    gray.add(char)

            length = current_guess_json['length']
            tmp = current_guess_json['level']

            if (current_guess_json['level'] >= 13) and (len(green) == length):
                answer = ''.join([hash_data['char'] for hash_data in current_guess_json['hash']])
                possible_passwords = []
                for word, md5_hash in ry_with_hash:
                    if answer == md5_hash[:len(green)]:
                        possible_passwords.append(word)
                for password in possible_passwords:
                    payload = {
                        'token': f'{token}',
                        'password': password
                    }
                    response = requests.post(f"{link}/api/guess", json=payload)
                    if 'EPT{' in response.json().get('flag'):
                        print(response.json().get('flag'))
                        flag = True
                        break
                    if response.json().get('level') > tmp:
                        break
                break

            if (len(green) == length) or (level != current_guess_json['level']):
                level = current_guess_json['level']
                break

            for word, md5_hash in ry_with_hash:
                md5_hash = md5_hash[:length]

                if word in banned_words:
                    continue

                break_check = False
                if green:
                    for key, value in green.items():
                        if md5_hash[key] != value:
                            break_check = True
                            break
                    if break_check:
                        continue

                if not all([char[0] in md5_hash for char in yellow_list]):
                    continue

                for tpl in yellow_list:
                    if (tpl[0] not in green.keys()) and (md5_hash[tpl[1]] == tpl[0]):
                        break_check = True
                        break
                if break_check:
                    continue

                for i, c in enumerate(md5_hash):
                    if (i not in green.keys()) and (c in gray):
                        break_check = True
                        break
                if break_check:
                    continue

                if (word not in banned_words) or level == 15:
                    inner = True
                    password = word
                    banned_words.add(password)
                    break

    except (KeyError, IndexError, TypeError) as e:
        error = True
