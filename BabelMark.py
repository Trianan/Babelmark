import pandas as pd
import math, json
from os import system, name


# ----------------------------------------------------------------------------------------------------------------------
# GLOBAL HELPER FUNCTIONS:

def print_hrule(length=100):
    print('-'*length)


def clear_terminal():
    if name == 'posix':
        _ = system('clear')
    else:
        _ = system('cls')


def set_config(setting, value):
    with open('bblmrk_config.json', 'r+') as config_file:
        settings = json.load(config_file)
        settings[setting] = value
        json.dump(settings, config_file)


def load_logs():
    with open('bblmrk_config.json', 'r') as config_file:
        settings = json.load(config_file)
        reading_log_csv = settings['reading_log']
        backlog_csv = settings['backlog']
    return (
        pd.read_csv(reading_log_csv),
        pd.read_csv(backlog_csv),
        reading_log_csv,
        backlog_csv
    )


# ----------------------------------------------------------------------------------------------------------------------
# PROGRESS-MODE FUNCTIONS:

def get_progress(rl_row):
    '''
    Takes a single row from the reading log dataframe.
    Returns a string containing the title and author of a book,
    as well as a percentage and progress bar.
    '''
    block = u"\u2588"
    empty_block = u"\u2591"
    percentage = round((rl_row.current_page / rl_row.pages) * 100, 2)
    progress_bar = block*math.ceil(percentage) + empty_block*(100 - math.ceil(percentage))
    return f"'{rl_row['title']}' by {' & '.join(rl_row['author'].split('/'))}: {percentage}%\n{progress_bar}"


def display_progress_view(readinglog):
    '''
    Takes the reading log dataframe, and prints the string
    returned from get_progress for each row, sorted by priority.
    '''
    readinglog.sort_values(by='priority').apply(get_progress, axis=1).apply(print)


def add_to_reading(readinglog, backlog, reading_csv, backlog_csv):
    '''
    Takes the reading log and backlog dataframes.

    Checks if book is in backlog; if so it moves the book from the backlog
    to the reading log and writes to their corresponding csv files. If it's not,
    the user is prompted for more info on the book, before it is added to the reading log
    and its csv file.

    Always sets the priority as the lowest priority (highest value).
    '''
    print('Please supply the following data:')
    title = input('Title: ')
    author = input('Author: ')
    if title in backlog.title and author in backlog.author:
        book = backlog[(backlog.title == title) & (backlog.author == author)]
        book['priority'] = len(readinglog)
        book['current_page'] = 1
        book['date_started'] = str(pd.to_datetime('today').date())
        readinglog = pd.concat([readinglog, book], axis=0)
        backlog.drop(book['priority'], axis='rows')
        readinglog.set_index('priority').to_csv(reading_csv)
        backlog.set_index('priority').to_csv(backlog_csv)
    else:
        print('Book not found in backlog...supply the following data:')
        nonfiction = input('Nonfiction? (yes/no): ')
        topic = input('Topic: ')
        subtopic = input('Subtopic: ')
        pages = int(input('Number of pages: '))
        book = pd.DataFrame([{
            'priority': len(readinglog),
            'title': title,
            'author': author,
            'nonfiction': nonfiction,
            'topic': topic,
            'subtopic': subtopic,
            'pages': pages,
            'current_page': 1,
            'date_started': str(pd.to_datetime('today').date())
        }])
        readinglog = pd.concat([readinglog, book], axis=0)
        readinglog.set_index('priority').to_csv(reading_csv)
    print(f'"{title}" by: {author} successfully added to reading log.')


# ----------------------------------------------------------------------------------------------------------------------
# BACKLOG-MODE FUNCTIONS:

def get_backlog(bl_row):
    '''
    Takes a single row from the backlog dataframe.
    Returns a string containing a summary of a book.
    '''
    log = f'''
"{bl_row['title']}" by: {bl_row['author']}
{"Nonfiction" if bl_row['nonfiction'] == 'yes' else 'Fiction'} -> {bl_row['topic']} -> {bl_row['subtopic']}
Pages: {bl_row['pages']}
Priority: {bl_row['priority']}
'''
    return log


def display_backlog_view(backlog):
    '''
    Takes the backlog dataframe, and prints the string
    returned from get_backlog for each row, sorted
    by priority.
    '''
    backlog.sort_values(by='priority').apply(get_backlog, axis=1).apply(print)


def add_to_backlog(backlog, backlog_csv):
    '''
    Takes a dictionary containing the data for a book, and the
    backlog dataframe.
    Adds the book to the backlog and its csv file,
    after checking if it already exists.
    Always sets priority to the lowest priority (highest possible).
    '''
    print('Please supply the following data:')
    title = input('Title: ')
    author = input('Author: ')
    title_matches = backlog[backlog.title == title]
    full_matches = title_matches[title_matches.author == author]
    if len(full_matches) > 0:
        print(f'''Cannot add "{title}" by: {author}; already exists in backlog.''')
    else:
        nonfiction = input('Nonfiction? (yes/no): ')
        topic = input('Topic: ')
        subtopic = input('Subtopic: ')
        pages = input('Number of pages: ')
        book = {
            'priority': len(backlog),
            'title': title,
            'author': author,
            'nonfiction': nonfiction,
            'topic': topic,
            'subtopic': subtopic,
            'pages': int(pages)
        }
        book_df = pd.DataFrame(book, index=[len(backlog)])
        backlog = pd.concat([backlog, book_df], axis=0)
        backlog.set_index('priority').to_csv(backlog_csv)
        print(f'''Added "{book['title']}" by: {book['author']} to backlog.''')


# ----------------------------------------------------------------------------------------------------------------------
# READING VIEW LOOP:

def start_reading_view(r_df, b_df, r_csv, b_csv):

    reading_menu = '''
                .-. .-. .-. .-. .-. . . .-.   . . .-. .-. . . . 
                |(  |-  |-| |  ) |  |\| |..   | |  |  |-  | | | 
                ' ' `-' ` ' `-' `-' ' ` `-'   `.' `-' `-' `.'.' 
   *---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---*
    Sort by ...  -> s       Remove book  -> rb      Toggle progress or backlog mode    -> m
    Start book   -> sb      Edit book    -> eb      Add to backlog -> b      Main menu -> q
'''
    usr_input = ''
    reading_mode = True
    while usr_input != 'q':

        clear_terminal()
        print(reading_menu)

        match usr_input:
            case 's':
                print('Sort by ()')
            case 'sb':
                add_to_reading(r_df, b_df, r_csv, b_csv)
                r_df, b_df, r_csv, b_csv = load_logs()
            case 'rb':

                r_df, b_df, r_csv, b_csv = load_logs()
            case 'eb':

                r_df, b_df, r_csv, b_csv = load_logs()
            case 'm':
                if reading_mode:
                    reading_mode = False
                else:
                    reading_mode = True
            case 'b':
                add_to_backlog(b_df, b_csv)
                r_df, b_df, r_csv, b_csv = load_logs()
            case 'q':
                print('Back to main menu...')
            case other:
                pass

        if reading_mode:
            display_progress_view(r_df)
        else:
            display_backlog_view(b_df)

        usr_input = input('Enter a command: ')



# ----------------------------------------------------------------------------------------------------------------------
# MAIN LOOP:

main_menu = '''

    ██████╗  █████╗ ██████╗ ███████╗██╗     ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗
    ██╔══██╗██╔══██╗██╔══██╗██╔════╝██║     ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝
    ██████╔╝███████║██████╔╝█████╗  ██║     ██╔████╔██║███████║██████╔╝█████╔╝ 
    ██╔══██╗██╔══██║██╔══██╗██╔══╝  ██║     ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ 
    ██████╔╝██║  ██║██████╔╝███████╗███████╗██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗
    ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
   *---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---*
    Reading View  -> rv      Set default logs -> dl      Quit -> q
    Stats View    -> sv      Start book       -> sb
    Category View -> cv      About            -> a
'''

usr_input = ''
rl, bl, r_csv, b_csv = load_logs()
while usr_input != 'q':

    clear_terminal()
    print(main_menu)

    usr_input = input('Enter a command: ')
    match usr_input:
        case 'rv':
            start_reading_view(rl, bl, r_csv, b_csv)
        case 'sv':
            # stats_view()
            pass
        case 'cv':
            # category_view()
            pass
        case 'dl':
            # Set default logs(reading_log.csv, backlog.csv)
            # set_config('reading_log': reading_log.csv)
            # set_config('backlog': backlog.csv)
            pass
        case 'sb':
            add_to_reading(rl, bl, r_csv, b_csv)
            rl, bl, r_csv, b_csv = load_logs()
        case 'a':
            # print_about_info()
            pass
        case 'q':
            print('Quitting BabelMark...')
        case other:
            pass

# ----------------------------------------------------------------------------------------------------------------------
