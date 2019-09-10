from promptr import Prompt, AmbiguousCommand, CommandNotFound, NotEnoughArgs, ExitState, PromptrCompleter
import pytest


@pytest.fixture()
def prompt():
    p = Prompt(prompt_fmt="{state}#")

    @p.command()
    def cmd1():
        pass

    @p.group()
    def group1():
        pass

    @p.state(prompt="s1")
    @p.argument("arg1", completions=lambda: ['test1', 'test2'])
    def state1(arg1):
        pass

    @state1.on_exit()
    def state1_exit():
        pass

    @state1.command(
        optional_prefixes=['no'], pass_name=True, pass_context=['arg1']
    )
    def cmd2(called_name, arg1):
        assert arg1 == 'test'

    @p.state()
    def state2(prompt="s2"):
        pass

    @p.argument("arg2")
    @state2.group()
    def group2(arg2):
        p.set_context("arg2", arg2)

    @state2.state()
    def state3():
        pass

    return p


def test_run(prompt):
    prompt.run_text(
        """cmd1
        group1
        state1 test
        cmd
        exit
        state2
        group2 test
        state3
        exit
        exit
        """,
        prompt_fmt="{state}#"
    )


def test_bad_runs(prompt):
    with pytest.raises(AmbiguousCommand):
        prompt.run_text("state")

    with pytest.raises(CommandNotFound):
        prompt.run_text("stait")

    with pytest.raises(NotEnoughArgs):
        prompt.run_text("state1")

    with pytest.raises(ExitState):
        prompt.run_text('exit')


def test_list_children(prompt):
    lines_target = [
        '<Command exit [] help=None>', '<Command cmd1 [] help=None>',
        '<Group group1 [] help=None>',
        "<State state1 [<Argument arg1 ['test1', 'test2']>] help=None, prompt=s1>",
        '  <Command exit [] help=None>',
        "  <Command cmd2 [] help=None, optional_prefixes=['no'], pass_context=['arg1'], pass_name=True>",
        '<State state2 [] help=None>', '  <Command exit [] help=None>',
        '  <Group group2 [<Argument arg2 []>] help=None>',
        '  <State state3 [] help=None>', '    <Command exit [] help=None>'
    ]
    lines = []
    prompt.list_children(p=lines.append, deep=True, indent=2)
    print(lines)
    assert lines == lines_target


def test_completion(prompt):
    from prompt_toolkit.document import Document
    completer = PromptrCompleter(prompt)
    for completion in completer.get_completions(Document('state', 5), None):
        assert completion.text.startswith('state')
    for completion in completer.get_completions(Document('state1 t', 8), None):
        assert completion.text.startswith('test')
    prompt.run_text("state1 test")
    assert prompt.current_prompt == '(s1)#'
    completions = list(completer.get_completions(Document('c', 1), None))
    assert len(completions) == 1
