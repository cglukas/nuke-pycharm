import inspect
import re
import os
import nuke


import logging
logging.basicConfig()
logger = logging.getLogger('NukeStubsGenerator')
logger.setLevel(logging.INFO)


class NukeStubsGenerator(object):
    """
    A stubs generator for the Nuke python API.
    @param directory: The ouput directory to write the stubs to.
                      Defaults to a stubs folder in your home directory.
    """

    default_directory = os.path.join(os.path.expanduser('~'), 'stubs')

    def __init__(self, directory=None):
        self._indent = 0
        self.contents = ''

        # Generate the stubs string
        self.generate()

        # If we didn't get anything, then lets not bother writing
        if not self.contents:
            logger.critical('Could not generate stubs')
            return

        # Check the directory to write to
        self.directory = directory or self.default_directory
        if not os.path.exists(self.directory):
            if directory:
                raise IOError("Directory %s does not exist. Cannot write." % (self.directory))

            logger.info('Creating directory %s', self.directory)
            os.mkdir(self.directory)

        self.output_file = os.path.join(self.directory, 'nuke.pyi')

        # Save the file
        self.save()

    def __str__(self):
        return self.output_file

    def write(self, text):
        """
        Writes the given text to the contents string with correct indentation
        @param text: the string to add
        """
        if not text:
            return

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            line = '%s%s\n' % (self._indent*' ', line)
            self.contents += line

    def indent(self):
        """Adds an indentation level to the output"""
        self._indent += 4

    def dedent(self):
        """Removes an indentation level to the output"""
        self._indent = max(self._indent - 4, 0)

    def get_builtin_info(self, builtin):
        """Resolves the signature and docstring for a given builtin function.
        This depends on parsing the docstring for the object.

        @param builtin: the builtin object to check
        @returns tuple of (name, args, defaults)
        """

        try:
            name = builtin.__name__
        except:
            name = None

        args = []
        defaults = []

        docs = builtin.__doc__ or ''
        lines = docs.split('\n')


        # Find the signature based on a common formatting scheme by finding the first ()
        if lines:
            decl = lines[0]

            # Try and find the function signature by finding the parens
            paren_open = decl.find('(')
            paren_close = decl.find(')', paren_open)
            if paren_open != -1 and (paren_close >= paren_open + 1):
                d = decl[paren_open+1:paren_close]
                args = d.replace(',', '').split()

            # If it's indented, just assume its a class method
            if self._indent:
                args.insert(0, 'self')

            # Try and find the name if we haven't got it from the object
            if not name:
                _name = decl[:paren_open].replace('self.', '')

                # Some of the objects don't get names well so a last failsafe
                if _name.strip() and _name in str(builtin):
                    name = _name.split()[0]

        return name, args, defaults


    def get_info(self, func):
        """Resolves the signature and docstring for a given object
        @param func: an executable object to work on.
        @return Returns True if it could resolve info, otherwise it fails
        """

        if inspect.isbuiltin(func) or inspect.isroutine(func):

            name, args, defaults = self.get_builtin_info(func)
        else:
            try:
                spec = inspect.getargspec(func)
            except:
                logger.info('Failed to resolve %s', func)
                return

            name = func.__name__
            args = spec.args or []
            defaults = spec.defaults or []

        if not name:
            return
        if inspect.ismethod(func) and 'self' not in args:
            args.insert(0, 'self')

        # Replace kwargs with their appropriate defaults
        for kw, val in zip(args[-len(defaults):], defaults):
            args[args.index(kw)] = '%s=%s' % (kw, val)

        # Finally write the declaration of the function
        signature = '\ndef %s(%s):' % (name, ', '.join(args))
        self.write(signature)
        self.indent()
        doc = '"""%s"""' % func.__doc__
        self.write(doc)
        self.write('pass\n')
        self.dedent()

        return True


    def get_class_info(self, cls):
        """Resolves the signature, docstring and members of a class"""

        base = inspect.getclasstree([cls])[0][0].__name__

        signature = '\nclass %s(%s):' % (cls.__name__, base)
        self.write(signature)
        self.indent()
        doc = '"""%s"""' % cls.__doc__
        self.write(doc)
        for member_name, member in cls.__dict__.items():
            if member_name.startswith('__'):
                continue
            if not member:
                logger.info('Failed to resolve %s', member_name)
            else:
                self.get_info(member)

        self.dedent()



    def generate(self):
        """Generates the docstring content for the nuke module"""
        for name in dir(nuke):
            if name.startswith('__'):
                continue
            obj = getattr(nuke, name, None)
            if not obj:
                logger.info('Failed to resolve %s', name)
            elif inspect.isclass(obj):
                self.get_class_info(obj)
            else:
                self.get_info(obj)

    def save(self):
        """Saves the generated stubs string to disk"""
        with open(self.output_file, 'w') as f:
            f.write(self.contents)

        logger.info('Wrote to %s', self.output_file)

def generate(directory=None):
    """Convenience method for generating the stubs.
    @param directory: the directory to write to. Defaults to a stubs folder in your user dir.
    @return the stubs object
    """
    stubs = NukeStubsGenerator(directory)
    return stubs


if __name__ == '__main__':
    print(generate(directory=r'C:\Users\Lukas\.nuke\_stubs'))
