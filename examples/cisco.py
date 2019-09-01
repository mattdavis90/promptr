"""
ping
enable
  show
    startup-config
    running-config
    interfaces <intf> counters
  configure
    interface <intf>
      shutdown
      no shutdown
"""

from promptr import Prompt


prompt = Prompt()


@prompt.command()
def ping():
    pass


@prompt.state(prompt='en')
def enable():
    pass


@enable.group()
def show():
    pass


@show.command()
def startup_config():
    print("Showing startup config")


@show.command()
def running_config():
    print("Showing startup config")


@show.group('interface')
@prompt.argument("intf", completions=lambda: ["g0", "g1", "g2", "g3"])
def show_intf(intf):
    prompt.set_context('intf', intf)


@show_intf.command('counters')
def show_intf_count():
    print('Counters for {}'.format(prompt.get_context('intf')))


@enable.state(prompt='conf')
def configure():
    pass


@configure.state('interface', prompt='{intf}')
@prompt.argument("intf", completions=lambda: ["g0", "g1", "g2", "g3"])
def conf_intf(intf):
    prompt.set_context('intf', intf)


@conf_intf.command(optional_prefixes=['no'], pass_name=True)
def shutdown(called_name):
    print("Will {} {}".format(called_name, prompt.get_context('intf')))


if __name__ == "__main__":
    prompt.run_prompt_loop()
