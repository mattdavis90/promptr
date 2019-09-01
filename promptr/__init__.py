import inspect
from collections import namedtuple
from functools import wraps, partial

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

__version__ = "0.1.0"


def _promptr_decorator(name=None, cls=None, parent=None, **kwargs):
    def decorator(f):
        if cls is None or cls not in globals():
            raise TypeError("Must specify a valid class")

        Cls = globals()[cls]

        if isinstance(f, Command):
            raise TypeError("Attempt to convert a command twice")

        try:
            params = f.__promptr_params__
            params.reverse()
            del f.__promptr_params__
        except AttributeError:
            params = []

        help = kwargs.get("help")
        if help is None:
            help = inspect.getdoc(f)
            if isinstance(help, bytes):
                help = help.decode("utf-8")
        else:
            help = inspect.cleandoc(help)

        kwargs["help"] = help

        cmd = Cls(
            name=name or f.__name__.lower().replace("_", "-"),
            callback=f,
            params=params,
            **kwargs
        )
        cmd.__doc__ = f.__doc__

        if parent is not None:
            parent._children.append(cmd)

        return cmd

    return decorator


class PromptrError(RuntimeError):
    pass


class ExitState(PromptrError):
    pass


class CommandNotFound(PromptrError):
    def __init__(self, cmd, args):
        super(CommandNotFound,
              self).__init__('Command Not Found "{}"'.format(cmd))


class AmbiguousCommand(PromptrError):
    def __init__(self, cmd, args):
        super(AmbiguousCommand,
              self).__init__('Ambigous Command "{}"'.format(cmd))


class NotEnoughArgs(PromptrError):
    def __init__(self, cmd, params):
        super(NotEnoughArgs, self).__init__(
            'Not enough args "{}" requires {}'.format(
                cmd, [p.name for p in params]
            )
        )


class Argument(object):
    def __init__(self, name, **kwargs):
        self._name = name
        self._completions = kwargs.pop("completions", [])
        self._kwargs = kwargs

    @property
    def name(self):
        return self._name

    @property
    def completions(self):
        if callable(self._completions):
            return self._completions()
        return self._completions

    def __repr__(self):
        return "<Argument {} {}>".format(self.name, self.completions)


class Base(object):
    def __init__(self, name, callback, params, **kwargs):
        self._name = name
        self._callback = callback
        self._params = params
        self._kwargs = kwargs
        self._children = []
        self._last_call_kwargs = {}

        self._names = [self._name]
        for prefix in kwargs.get('optional_prefixes', []):
            self._names.append('{} {}'.format(prefix, self._name))

        self._pass_name = kwargs.get('pass_name', False)

    def list_children(self, p=print, deep=False, indent=0):
        for child in self._children:
            p("{}{}".format(" " * indent, child))
            if deep:
                child.list_children(p, deep, indent + 2)

    def call(self, cmd, line_parts):
        if len(self._params) > len(line_parts):
            raise NotEnoughArgs(cmd, self._params)

        kwargs = {}

        if self._pass_name:
            kwargs['called_name'] = self.get_completions(cmd)[0]

        ## TODO: Parse these correctly
        for param in self._params:
            kwargs[param.name] = line_parts.pop(0)

        if self._callback is not None:
            self._callback(**kwargs)

        self._last_call_kwargs = kwargs

    @property
    def names(self):
        return self._names

    def completions(self, cmd):
        for name in self.names:
            if name.startswith(cmd):
                yield name

    def get_completions(self, cmd):
        return list(self.completions(cmd))

    def child_completions(self, line_parts, last_word):
        state = self
        child_complete = True

        for word in line_parts:
            for child in state._children:
                for name in child.completions(word):
                    if name == word:
                        state = child
                        if type(state) != Group:
                            child_complete = False

        for param in state._params:
            for completion in param.completions:
                if completion.startswith(last_word):
                    yield completion

        if child_complete:
            for child in state._children:
                for name in child.completions(last_word):
                    if name.startswith(last_word):
                        yield name

    def __repr__(self):
        return "<{} {} {} {}>".format(
            self.__class__.__name__,
            self._name,
            self._params,
            ", ".join(
                ["{}={}".format(k, v) for k, v in sorted(self._kwargs.items())]
            ),
        )


class Command(Base):
    pass


class Group(Base):
    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)

        self.command = partial(_promptr_decorator, cls="Command", parent=self)
        self.action = partial(_promptr_decorator, cls="Action", parent=self)
        self.group = partial(_promptr_decorator, cls="Group", parent=self)
        self.state = partial(_promptr_decorator, cls="State", parent=self)

    def call_child(self, line_parts):
        if len(line_parts) > 0:
            cmd = line_parts.pop(0)

            if cmd == "":
                return None

            possible = [
                child for child in self._children
                if len(child.get_completions(cmd)) == 1
            ]

            if len(possible) > 1:
                raise AmbiguousCommand(cmd, line_parts)
            elif len(possible) == 0:
                raise CommandNotFound(cmd, line_parts)

            child = possible[0]
            child.call(cmd, line_parts)

            if isinstance(child, State):
                return child
            elif hasattr(child, "call_child"):
                child.call_child(line_parts)

            return None


def _exit_state():
    raise ExitState()


class State(Group):
    def __init__(self, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)

        self._prompt = kwargs.get("prompt", None)
        self.command(name="exit")(_exit_state)

    @property
    def names(self):
        return [self._name]

    def get_prompt(self):
        if self._prompt is not None:
            return self._prompt.format(**self._last_call_kwargs)
        return None


StackItem = namedtuple("StackItem", ["state", "context"])


class PromptrCompleter(Completer):
    def __init__(self, prompt, *args, **kwargs):
        super(PromptrCompleter, self).__init__(*args, **kwargs)
        self._prompt = prompt

    def get_completions(self, document, complete_event):
        last_word = document.get_word_before_cursor()
        line_parts = document.text.split(" ")
        for word in self._prompt.current_state.child_completions(
            line_parts, last_word
        ):
            yield Completion(word, -len(last_word))


class Prompt:
    def __init__(
        self,
        prompt_fmt="{host}{state}# ",
        state_delim="-",
        state_paren_l="(",
        state_paren_r=")",
        extra_completions=None,
        **kwargs
    ):
        import socket

        fqdn = socket.gethostname()
        fqdn_parts = fqdn.split(".")
        host = fqdn_parts[0]
        domain = ""
        if len(fqdn_parts) > 1:
            domain = ".".join(fqdn_parts[1:])

        self._completions = {"fqdn": fqdn, "host": host, "domain": domain}
        if extra_completions is not None:
            self._completions.update(extra_completions)

        self._root = Group("_root", None, [])
        self._root.command(name="exit")(_exit_state)
        self._state_stack = [StackItem(self._root, {})]
        self._prompt_states = []

        self._prompt_fmt = prompt_fmt
        self._state_delim = state_delim
        self._state_paren_l = state_paren_l
        self._state_paren_r = state_paren_r

        self.command = partial(
            _promptr_decorator, cls="Command", parent=self._root
        )
        self.action = partial(
            _promptr_decorator, cls="Action", parent=self._root
        )
        self.state = partial(_promptr_decorator, cls="State", parent=self._root)
        self.group = partial(_promptr_decorator, cls="Group", parent=self._root)
        self.list_children = self._root.list_children

    def argument(self, *args, **kwargs):
        def decorator(f):
            ArgCls = kwargs.pop("cls", Argument)
            arg = ArgCls(*args, **kwargs)

            if isinstance(f, Base):
                f._params.append(arg)
            else:
                if not hasattr(f, "__promptr_params__"):
                    f.__promptr_params__ = []
                f.__promptr_params__.append(arg)

            return f

        return decorator

    @property
    def current_prompt(self):
        state = ""
        if len(self._prompt_states) > 0:
            state = "{}{}{}".format(
                self._state_paren_l,
                self._state_delim.join(self._prompt_states),
                self._state_paren_r,
            )
        return self._prompt_fmt.format(state=state, **self._completions)

    def _push_state(self, state):
        self._state_stack.append(StackItem(state, {}))
        if state.get_prompt() is not None:
            self._prompt_states.append(state.get_prompt())

    def _pop_state(self):
        if self.current_state.get_prompt() is not None:
            self._prompt_states.pop()
        return self._state_stack.pop().state

    def set_context(self, key, value):
        self._state_stack[-1].context[key] = value

    def get_context(self, key, default=None):
        for state in reversed(self._state_stack):
            value = state.context.get(key, None)
            if value is not None:
                return value
        return default

    @property
    def current_state(self):
        return self._state_stack[-1].state

    def _run(self, get_line):
        for line in get_line:
            try:
                line_parts = [w for w in line.split(" ") if w != ""]
                if len(line_parts) == 0:
                    continue

                new_state = self.current_state.call_child(line_parts)

                if new_state is not None:
                    self._push_state(new_state)
            except ExitState:
                if len(self._state_stack) > 1:
                    new_state = self._pop_state()
                else:
                    raise ExitState()

    def _get_prompt_line(self, **kwargs):
        kwargs["completer"] = PromptrCompleter(self)

        session = PromptSession(**kwargs)

        while True:
            try:
                yield session.prompt(self.current_prompt)
            except KeyboardInterrupt:
                continue

    def run_prompt(self, **kwargs):
        self._run(iself._get_prompt_line(**kwargs))

    def run_prompt_loop(self, **kwargs):
        while True:
            try:
                self._run(self._get_prompt_line(**kwargs))
            except (ExitState, EOFError):
                break
            except PromptrError as exc:
                print(exc)

    def run_text(self, text, **kwargs):
        self._run(text.splitlines())
