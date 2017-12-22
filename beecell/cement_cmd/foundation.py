'''
Created on Nov 3, 2017

@author: darkbk
'''
import cmd
import sys, os, re
from cement.core.foundation import CementApp, LOG
from cement.core.controller import CementBaseController, expose
from gettext import gettext as _
import logging
import time
import traceback

logger = logging.getLogger(__name__)

class ColoredText:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    WHITEonBLACK = '\033[1;37;40m'
    GREENonBLACK = '\033[1;32;40m'
    BLUEonBLACK = '\033[1;34;40m'
    REDonBLACK = '\033[1;31;40m'
    YELLOWonBLACK = '\033[1;33;40m'
    PURPLEonBLACK = '\033[1;35;40m'
    CYANonBLACK = '\033[1;36;40m'
    
    def output(self, data, color):
        return getattr(self, color) + data + self.ENDC
    
    def error(self, data):
        return self.FAIL + u' ERROR : ' + self.ENDC +\
            self.FAIL + self.BOLD + str(data) + self.ENDC

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
                #return func()
            else:
                self._process_arguments()
                self._parse_args()
                if self.app.error is True:
                    self.app.error = False
                    return
                func = getattr(self._dispatch_command['controller'],
                               self._dispatch_command['func_name'])
                #return func()
        else:
            self._process_arguments()
            self._parse_args()
            func = None
            
        return func()
    
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
        color = True
    
    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, completekey='tab', stdin=None, stdout=None)
        #CementApp.__init__(self, *args, **kwargs)
        self.__init_cement__(*args, **kwargs)    
        
        self.prompt = self.Meta.prompt
        
        self.colored_text = ColoredText()
        self._colorize_prompt()
    
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
        
        self.has_setup = False # use to set single setup when loop is True

    def _colorize_prompt(self):
        if self._meta.color is True:
            self.prompt = self.colored_text.BOLD + self.prompt + \
                self.colored_text.ENDC

    def print_output(self, data, color=u'WHITEonBLACK'):
        if self.error is False:
            if self._meta.color is True:
                data = self.colored_text.output(data, color)
            print(data)
    
    def print_error(self, data):
        logger.error(traceback.format_exc())
        if self._meta.color is True:
            data = self.colored_text.error(data)
        print(data)
        self.error = True
    
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
            msg = _(u'unrecognized arguments: %s')
            msg = msg % u' '.join(argv)
            self.error = True
            self.print_error(msg)
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
            self.start = time.time()
            logger.debug(u'Run command: %s - START' % sys.argv)
            # setup argv... this has to happen before lay_cement()
            if self._meta.argv is None:
                self._meta.argv = list(sys.argv[1:])
            
            # setup the cement framework
            self._lay_cement()
            self.setup()
            self.setup_once()
            CementApp.run(self)
            #InteractiveOrCommandLine().onecmd(' '.join(sys.argv[1:]))
            logger.debug(u'Run command: %s - STOP [%s]' % (sys.argv, time.time()-self.start))
        else:
            self.cmdloop()
            #InteractiveOrCommandLine().cmdloop()
    
    def setup_once(self):
        """Exetend this when loop is True and you want to run only the first time
        """
        if self.has_setup is True:
            return
        self.has_setup = True
    
    #
    # cmd extension
    #
    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """
        self.start = time.time()
        logger.debug(u'Run command: %s - START' % line)
        
        # set loop
        self.loop = True
        
        # setup argv... this has to happen before lay_cement()
        #print line
        #self._meta.argv = []
        #if line is not None and line != u'':
        self._meta.argv = list(line.split(u' '))
        
        # setup the cement framework
        self._lay_cement()
        self.setup()
        self.setup_once()
        
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
        logger.debug(u'Run command: %s - STOP [%s]' % (line, time.time()-self.start))
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
            return
            #return self.emptyline()
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
