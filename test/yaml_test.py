import yaml


def set_state(state):
    with open('file_to_edit.yaml') as f:
        doc = yaml.load(f)

    doc['state'] = state

    with open('file_to_edit.yaml', 'w') as f:
        yaml.dump(doc, f)


while True:
    future = str(input(">>> "))
    set_state(future)
