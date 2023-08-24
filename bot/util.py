

def format_message_list2(obj):
    text = ''
    messages = []
    if len(obj) > 0:
        for k, v in obj.items():
            key = str(k)
            val = str(v)
            total_len = (len(key) + len(val))
            pad = 31 - total_len % 31

            text += key

            if pad > 0:
                text += ' ' * pad

            if total_len > 31:
                text += ' ' * 2

            text += str(v)
            text += '\n'

        text += ''
        # parts = [your_string[i:i+n] for i in range(0, len(your_string), n)]
        index = 0
        size = 4000
        while len(text) > 0:
            part = text[index:index + size]
            index = part.rfind('\n')
            if index == -1:
                index = len(text)
            part = text[0:index]
            messages.append('```\n' + part + '\n```')
            text = text[index:].strip()
        return messages


def format_message_list4(obj):
    # print(obj)
    text = ''
    messages = []
    if len(obj) > 0:
        for i in obj:
            for k, v in i.items():
                key = str(k)
                val = str(v)
                total_len = (len(key) + len(val))
                pad = 30 - total_len % 30

                text += key

                if pad > 0:
                    text += ' ' * pad

                if total_len > 30:
                    text += ' ' * 2

                text += str(v)
                text += '\n'
            text += '\n'
            text += '******************************'
            text += '\n'

        text += ''
        index = 0
        size = 4000
        while len(text) > 0:
            part = text[index:index + size]
            index = part.rfind('\n')
            if index == -1:
                index = len(text)
            part = text[0:index]
            messages.append('```\n' + part + '\n```')
            text = text[index:].strip()
        return messages
