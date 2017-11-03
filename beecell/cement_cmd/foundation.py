'''
Created on Nov 3, 2017

@author: darkbk
'''
import cmd
import sys, os, re
from cement.core.foundation import CementApp, LOG
from cement.core.controller import CementBaseController, expose
from gettext import gettext as _

class CementCmdBaseController(CementBaseController):
    def _dispatch(self):
        """
        Takes the remaining arguments from self.app.argv and parses for a
        command to dispatch, and if so... dispatches it.

        """
        if hasattr(self._meta, 'epilog'):
            if self._meta.epilog is not None:
                self.app.args.epilog = self._meta.epilog

        self._arguments, self._commands = self._collect()
        self._process_commands()
        self._get_dispatch_command()
        
        if self._dispatch_command:
            if self._dispatch_command['func_name'] == '_dispatch':
                func = getattr(self._dispatch_command['controller'],
                               '_dispatch')
                return func()
            else:
                self._process_arguments()
                self._parse_args()
                if self.app.error is True:
                    self.app.error = False
                    return
                func = getattr(self._dispatch_command['controller'],
                               self._dispatch_command['func_name'])
                return func()
        else:
            self._process_arguments()
            self._parse_args()    
    
    @expose(hide=True)
    def default(self):
        self.app.print_help()
        
    @expose(hide=True)
    def help(self):
        self.app.print_help()
    
    @expose(hide=True)
    def exit(self):
        return True      

class CementCmd(cmd.Cmd, CementApp):
    class Meta:
        label = 'myapp'
        base_controller = 'base'
        prompt = u'cmd> '
    
    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, completekey='tab', stdin=None, stdout=None)
        #CementApp.__init__(self, *args, **kwargs)
        self.__init_cement__(*args, **kwargs)
        
        self.prompt = self.Meta.prompt
    
    def __init_cement__(self, label=None, **kw):
        super(CementApp, self).__init__(**kw)
        
        self.loop = False
        self.error = False

        # disable framework logging?
        if 'CEMENT_FRAMEWORK_LOGGING' not in os.environ.keys():
            if self._meta.framework_logging is True:
                os.environ['CEMENT_FRAMEWORK_LOGGING'] = '1'
            else:
                os.environ['CEMENT_FRAMEWORK_LOGGING'] = '0'

        # for convenience we translate this to _meta
        if label:
            self._meta.label = label
        self._validate_label()
        self._loaded_bootstrap = None
        self._parsed_args = None
        self._last_rendered = None
        self._extended_members = []
        self.__saved_stdout__ = None
        self.__saved_stderr__ = None
        self.__retry_hooks__ = []
        self.handler = None
        self.hook = None

        self.exit_code = 0

        self.ext = None
        self.config = None
        self.log = None
        self.plugin = None
        self.args = None
        self.output = None
        self.controller = None
        self.cache = None
        self.mail = None 
    
    def do_greet(self, person):
        """greet [person]
        Greet the named person"""
        if person:
            print "hi,", person
        else:
            print 'hi'
    
    def do_exit(self, line):
        return True    
    
    def do_EOF(self, line):
        return True
    
    #
    # custom
    #
    def remove_options(self, parser, options):
        for option in options:
            for action in parser._actions:
                if vars(action)['option_strings'][0] == option:
                    parser._handle_conflict_resolve(None,[(option,action)])
                    break    
    
    #
    # cement argparse extension
    #
    def format_help(self):
        formatter = self.args._get_formatter()

        # usage
        #formatter.add_usage(self.usage, self._actions,
        #                    self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.args.description)

        # positionals, optionals and user-defined groups
        #for action_group in self.args._action_groups:
        #    formatter.start_section(action_group.title)
        #    formatter.add_text(action_group.description)
        #    formatter.add_arguments(action_group._group_actions)
        #    formatter.end_section()

        # epilog
        #formatter.add_text(self.args.epilog)

        # determine help from format above
        return formatter.format_help()
    
    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        if self.loop is True:
            format_help = self.format_help
        else:
            format_help = self.args.format_help
        self.args._print_message(format_help(), file)    
    
    #
    # cement extension
    #
    def _internal_parse_args(self, args=None, namespace=None):
        args, argv = self.args.parse_known_args(args, namespace)
        if argv:
            msg = _('unrecognized arguments: %s')
            self.error = True
            print(msg % ' '.join(argv))
            #self.error(msg % ' '.join(argv))
        return args    
    
    def _parse_args(self):
        for res in self.hook.run('pre_argument_parsing', self):
            pass

        # --- remove to avoid exit if loop is True
        if self.loop is False:
            self._parsed_args = self.args.parse(self.argv)
        # --- use if loop is True
        else:
            args = self._internal_parse_args(self.argv)
            self._parsed_args = args

        if self._meta.arguments_override_config is True:
            for member in dir(self._parsed_args):
                if member and member.startswith('_'):
                    continue

                # don't override config values for options that weren't passed
                # or in otherwords are None
                elif getattr(self._parsed_args, member) is None:
                    continue

                for section in self.config.get_sections():
                    if member in self.config.keys(section):
                        self.config.set(section, member,
                                        getattr(self._parsed_args, member))

        for member in self._meta.override_arguments:
            for section in self.config.get_sections():
                if member in self.config.keys(section):
                    self.config.set(section, member,
                                    getattr(self._parsed_args, member))

        for res in self.hook.run('post_argument_parsing', self):
            pass
    
    def _setup_arg_handler(self):
        LOG.debug("setting up %s.arg handler" % self._meta.label)
        self.args = self._resolve_handler('argument',
                                          self._meta.argument_handler)
        self.args.prog = self._meta.label

        if self.loop is False:
            self.args.add_argument('--debug', dest='debug',
                                   action='store_true',
                                   help='toggle debug output')
            self.args.add_argument('--quiet', dest='suppress_output',
                                   action='store_true',
                                   help='suppress all output')
        else:
            self.remove_options(self.args, ['-h', '--help'],)
        
        # merge handler override meta data
        if self._meta.handler_override_options is not None:
            # fucking long names... fuck.  anyway, merge the core handler
            # override options with developer defined options
            core = self._meta.core_handler_override_options.copy()
            dev = self._meta.handler_override_options.copy()
            core.update(dev)

            self._meta.handler_override_options = core    
    
    def run(self):
        if len(sys.argv) > 1:
            # setup argv... this has to happen before lay_cement()
            if self._meta.argv is None:
                self._meta.argv = list(sys.argv[1:])
            
            # setup the cement framework
            self._lay_cement()
            self.setup()
            CementApp.run(self)
            #InteractiveOrCommandLine().onecmd(' '.join(sys.argv[1:]))
        else:
            self.cmdloop()
            #InteractiveOrCommandLine().cmdloop()
    
    #
    # cmd extension
    #
    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """
        # set loop
        self.loop = True
        
        # setup argv... this has to happen before lay_cement()
        self._meta.argv = list(line.split(u' '))
        
        # setup the cement framework
        self._lay_cement()
        self.setup()        
        
        LOG.debug('running pre_run hook')
        for res in self.hook.run('pre_run', self):
            pass        

        return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        LOG.debug('running post_run hook')
        for res in self.hook.run('post_run', self):
            pass
        
        self.close()
        return stop    
    
    def default(self, line):
        """Called on an input line when the command prefix is not recognized.

        If this method is not overridden, it prints an error message and
        returns.

        """
        self.stdout.write('*** Unknown syntax: %s\n'%line)    

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                # If controller exists, then dispatch it
                if self.controller:
                    try:
                        return_val = self.controller._dispatch()
                    except Exception as ex:
                        #self.stdout.write(ex)
                        return_val = None
                else:
                    self._parse_args()
                
                #func = getattr(self, 'do_' + cmd)
            except AttributeError as ex:
                LOG.error(ex, exc_info=1)
                return self.default(line)
            return return_val
