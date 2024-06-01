from termcolor import colored
from colorama import just_fix_windows_console

# This fixes issues with colored text on windows consoles
just_fix_windows_console()

# Colored text lambda functions
print_blue = lambda x: print(colored(x, "blue"))
print_green = lambda x: print(colored(x, "green"))
print_red = lambda x: print(colored(x, "red"))
print_purple = lambda x: print(colored(x, "magenta"))