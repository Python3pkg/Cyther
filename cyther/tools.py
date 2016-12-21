
import os


class CytherError(Exception):
    """A custom error used to denote that an exception was Cyther related"""
    def __init__(self, *args, **kwargs):
        super(CytherError, self).__init__(*args, **kwargs)


def write_dict_to_file(file_path, obj):
    """
    Write a dictionary of strings to a file
    """
    string = ''
    for key, value in obj.items():
        string += key + ':' + value + os.linesep

    with open(file_path, 'w+') as file:
        chars = file.write(string)

    return chars


def read_dict_from_file(file_path):
    """
    Read a dictionary of strings from a file
    """
    with open(file_path) as file:
        string = file.read()

    obj = {}
    for line in string.splitlines():
        key, value = line.split(':')
        obj[key] = value

    return obj


RESPONSES_ERROR = "Argument 'acceptableResponses' cannot be of type: '{}'"


def getResponse(message, acceptableResponses):
    """
    Ask the user to input something on the terminal level, check their response
    and ask again if they didn't answer correctly
    """
    if isinstance(acceptableResponses, str):
        acceptableResponses = (acceptableResponses,)
    else:
        if not isinstance(acceptableResponses, tuple):
            raise ValueError(RESPONSES_ERROR.format(type(acceptableResponses)))

    response = input(message)
    while response not in acceptableResponses:
        response = input(message)
    return response


def _removeGivensFromTasks(tasks, givens):
    for given in givens:
        if given in tasks:
            raise Exception("Task '{}' is not supposed to be a"
                            " given".format(given))
        for task in tasks:
            if given in tasks[task]:
                tasks[task].remove(given)


def generateBatches(tasks, givens):
    """
    A function to generate a batch of commands to run in a specific order as to
    meet all the dependencies for each command. For example, the commands with
    no dependencies are run first, and the commands with the most deep
    dependencies are run last
    """
    _removeGivensFromTasks(tasks, givens)

    batches = []
    while tasks:
        batch = set()
        for task, dependencies in tasks.items():
            if not dependencies:
                batch.add(task)

        if not batch:
            _batchErrorProcessing(tasks)

        for task in batch:
            del tasks[task]

        for task, dependencies in tasks.items():
            for item in batch:
                if item in dependencies:
                    tasks[task].remove(item)

        batches.append(batch)
    return batches


GIVENS_NOT_SPECIFIED = "The dependencies '{}' should be givens if not " \
                       "specified as tasks"


def _batchErrorProcessing(tasks):
    should_be_givens = []
    total_deps = {dep for deps in tasks.values() for dep in deps}
    for dep in total_deps:
        if dep not in tasks:
            should_be_givens.append(dep)

    if should_be_givens:
        string = ', '.join(should_be_givens)
        message = GIVENS_NOT_SPECIFIED.format(string)
    else:
        message = "Circular dependency found:\n\t"
        msg = []
        for task, dependencies in tasks.items():
            for parent in dependencies:
                line = "{} -> {}".format(task, parent)
                msg.append(line)
        message += "\n\t".join(msg)

    raise ValueError(message)
