from options import Option
from tools import ToolID, VocabTool


# ToDo: use rich to make nicer console output


def options_prompt():
    args = {}
    options = []

    # Add new tools here
    tool_names = {ToolID.VOCAB: 'Vocab Flashcards'}
    tool_id_prompt = 'Select an option:\n' + '\n'.join(
        [f'{tool_id.value}:\t{tool_name}' for tool_id, tool_name in tool_names.items()])
    tool_id_option = Option('tool_id', prompt=tool_id_prompt,
                            validator=lambda x, max_val=len(tool_names): x.isdigit() and (1 <= int(x) <= max_val),
                            processor=lambda x: ToolID(int(x)))
    options.append(tool_id_option)

    for option in options:
        option.prompt_user()
        args[option.name] = option.selection

    return args


def get_tool(tool_id: ToolID):
    # Add new tools here
    tools = {ToolID.VOCAB: VocabTool}

    tool = tools[tool_id]()
    return tool


if __name__ == '__main__':
    args = options_prompt()
    tool = get_tool(args['tool_id'])

    try:
        tool.run()
    except Exception as e:
        print(f'{type(e).__name__}: {e}')

    input('Press enter to exit')
