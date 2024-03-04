from cx_Freeze import setup, Executable

base = None    

executables = [Executable("AI_game.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "AIgame",
    options = options,
    version = "<1.0.0>",
    description = 'asd',
    executables = executables
)