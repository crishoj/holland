import os, sys
import logging
from pkg_resources import get_distribution
from holland.cli.config import load_global_config, ValidateError
from holland.cli.log import configure_logging, configure_basic_logger
from holland.cli.commands import ArgparseCommand, argument, load_command, \
                                 CommandNotFoundError

HOLLAND_VERSION = get_distribution('holland').version
HOLLAND_BANNER = """
Holland Backup v%s
Copyright (c) 2008-2010 Rackspace US, Inc.
More info available at http://hollandbackup.org

[[[[[[[]]]]]]] [[[[[[[]]]]]]]
[[[[[[[]]]]]]]       [[[[[[[]]]]]]]
[[[[[[[]]]]]]] [[[[[[[]]]]]]]
[[[[[[[]]]]]]] [[[[[[[]]]]]]]

""" % HOLLAND_VERSION

LOG = logging.getLogger(__name__)

configure_basic_logger()

class HollandCli(ArgparseCommand):
    name = 'holland'
    summary = 'Holland command line'
    description = HOLLAND_BANNER
    arguments = [
        argument('--config', '-c'),
        argument('--log-level', '-l'),
        argument('subcommand', nargs='?'),
        argument('args', nargs='...'),
    ]

    def execute(self, opts):

        try:
            config = load_global_config(opts.config)
        except IOError, exc:
            self.stderr("Failed to load config file: %s", exc)
            return 1
        except SyntaxError, exc:
            self.stderr("Error while reading config file: %s", exc, exc_info=True)
            return 1
        except ValidateError, exc:
            self.stderr("Error while validating config file: %s", exc)
            return 1

        if opts.log_level:
            config['logging']['level'] = \
            logging._levelNames[opts.log_level.upper()]
        if config['holland']['umask'] is not None:
            os.umask(config['holland']['umask'])
        if config['holland']['tmpdir']:
            os.environ['TMPDIR'] = config['holland']['tmpdir']
        if config['holland']['path']:
            os.environ['PATH'] = config['holland']['path']
        configure_logging(config['logging'])

        if not opts.subcommand:
            self.parser.print_help()
            opts.subcommand = 'list-commands'

        try:
            cmd = load_command('holland.commands', opts.subcommand, self.parser)
            return cmd(opts.args, context=opts)
        except CommandNotFoundError, exc:
            self.stderr('Failed to load command "%s"', opts.subcommand)
            return 1
        except: # unexpected command failure
            self.stderr('Unexpected exception while running command "%s"',
                        opts.subcommand)
            import traceback
            traceback.print_exc()
            return 1
        return 1

holland = HollandCli()
