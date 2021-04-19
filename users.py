import json


def isregistered(user_id):
    with open("external_data/users.json", "r") as read_file:
        loaded_json_file = json.load(read_file)
    for user_dict in loaded_json_file:
        if int(user_dict['id']) == user_id:
            return True


def every_user_id(role):
    with open("external_data/users.json", "r") as read_file:
        loaded_json_file = json.load(read_file)
    for user_dict in loaded_json_file:
        if user_dict['role'] == role:
            yield user_dict['id']


def every_role():
    with open("external_data/roles.json", "r") as read_file:
        loaded_json_file = json.load(read_file)
    return loaded_json_file.keys()


def define_role(user_id):
    with open("external_data/users.json", "r") as read_file:
        loaded_json_file = json.load(read_file)
    for user_dict in loaded_json_file:
        if int(user_dict['id']) == user_id:
            return user_dict['role']


def every_command(user_id):
    role = define_role(user_id)
    with open("external_data/roles.json", "r") as read_file:
        loaded_json_file = json.load(read_file)
    return loaded_json_file[role]


def register_user(id, fullname, nick, role):
    with open("external_data/users.json", "r") as file:
        loaded_json_file = json.load(file)
    new_data = {'id': id, 'fullname': fullname, 'nick': nick, 'role': role}
    with open("external_data/users.json", "w") as file:
        file.write(json.dumps([*loaded_json_file, new_data], sort_keys=True, indent=4))
