import os
import subprocess
import cudatext as app
from cuda_fmt import get_config_filename

PROGRAM = 'uncrustify.exe' if os.name=='nt' else 'uncrustify' 
CONFIG = 'uncrustify.cfg'

LANGS = {
    'C': 'C',
    'C++': 'CPP',
    'C#': 'CS',
    'D': 'D',
    'Java': 'JAVA',
    'Pawn': 'PAWN',
    'Objective-C': 'OC',
    'Objective-C++': 'OC+',
    'Vala': 'VALA',
    }

def run_app(text, config):

    tab_spaces = app.ed.get_prop(app.PROP_TAB_SPACES)
    tab_size = app.ed.get_prop(app.PROP_TAB_SIZE)
    lexer = app.ed.get_prop(app.PROP_LEXER_FILE)
    syntax = LANGS.get(lexer, 'C')

    program = PROGRAM
    if os.name=='nt':
        fn = os.path.join(app.app_path(app.APP_DIR_EXE), 'tools', 'uncrustify.exe')
        if os.path.exists(fn):
            program = fn

    command = [
        program, 
        '-l', syntax,
        '-c', config,
        '--set', 'newlines=LF',
        '--set', 'indent_with_tabs='+str(0 if tab_spaces else 1),
        '--set', 'indent_columns='+str(tab_size),
        '--set', 'input_tab_size='+str(tab_size),
        '--set', 'output_tab_size='+str(tab_size),
        ]

    print('Running:', ' '.join(command))
    content = text.encode("utf-8")
    
    try:
        if os.name=='nt':
            # to hide the console window brings from command
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # si.wShowWindow = subprocess.SW_HIDE   # this is default provided

            proc = subprocess.Popen(command, \
                   stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, startupinfo = si)
        else:
            proc = subprocess.Popen(command, \
                   stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        outs, errs = proc.communicate(input=content)

        ret_code = proc.poll()
        if ret_code != 0:
            if errs:
                msg = errs.decode("utf-8")
                # slice the last useless part if found (from Uncrustify)
                pos = msg.find("Try running with -h for usage information")
                err = "Uncrustify failed (0x%X)\n\n%s" % (ret_code, msg[:pos])
            else:
                err = "Uncrustify stopped (0x%X)" % ret_code
            
            app.msg_box(err, app.MB_OK+app.MB_ICONWARNING)
            return

    except (OSError, ValueError, subprocess.CalledProcessError, Exception) as e:
    
        err = "Cannot execute '%s':\n\n%s" % (command[0], e)
        app.msg_box(err, app.MB_OK+app.MB_ICONERROR)
        return

    formatted_code=outs.decode("utf-8")
    return formatted_code


def do_format(text):

    config = get_config_filename('Uncrustify Format')
    return run_app(text, config)
