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


def edit_book(readinglog, backlog, reading_csv, backlog_csv, args_list=[]):
    # Instead of getting title and author and setting values
    # through system dialogue, consider passing these in a
    # container; this will allow a streamlined change_page()
    # function which will have its own command, as this will be
    # a very common operation in Reading View for Progress Mode.
    if args_list:
        title, author, key, val = args_list
    else:
        print('Please supply the following data...')
        title = input('Title: ')
        author = input('Author: ')

    if title in readinglog.title.values and author in readinglog.author.values:
        book = readinglog[(readinglog.title == title) & (readinglog.author == author)]
        book_found = 'readinglog'
        print('Book found in reading log.')

    elif title in backlog.title.values and author in backlog.author.values:
        book = backlog[(backlog.title == title) & (backlog.author == author)]
        book_found = 'backlog'
        print('Book found in backlog.')
    else:
        book_found = None

    if book_found:
        if not args_list:
            key = input('Trait to modify: ')
            val = input('New value: ')

        if key in book.columns.values:
            print(f"Former value of {key}: {book[key]}")
            eval(book_found).at[book.index.values[0], key] = val
            print(f"Current value of {key}: {book[key]}")
        else:
            print('Invalid key in book: \n', book)
            input('press any key then ENTER: ')

        if book_found == 'backlog':
            backlog.set_index('priority').to_csv(backlog_csv)
        elif book_found == 'readinglog':
            readinglog.set_index('priority').to_csv(reading_csv)


def remove_book(readinglog, backlog, reading_csv, backlog_csv):

    pass


def update_current_page(readinglog, backlog, reading_csv, backlog_csv):
    print('Please supply the following data...')
    title = input('Title: ')
    author = input('Author: ')
    new_current_page = input('New current page: ')
    edit_book(readinglog, backlog, reading_csv, backlog_csv, [title, author, 'current_page', new_current_page])




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
    percentage = round((int(rl_row.current_page) / int(rl_row.pages)) * 100, 2)
    progress_bar = block*math.ceil(percentage) + empty_block*(100 - math.ceil(percentage))
    return f"'{rl_row['title']}' by {' & '.join(rl_row['author'].split('/'))}: {percentage}%\n{progress_bar}\n"


def display_progress_view(readinglog):
    '''
    Takes the reading log dataframe, and prints the string
    returned from get_progress for each row, sorted by priority.
    '''
    readinglog.apply(get_progress, axis=1).apply(print)


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
    print(backlog.title, backlog.author, backlog.title.values)
    if title in backlog.title.values and author in backlog.author.values:
        book = backlog[(backlog.title == title) & (backlog.author == author)]
        book_index = book.index[0]
        book = book.to_dict()
        book['priority'] = len(readinglog)
        book['current_page'] = 1
        book['date_started'] = str(pd.to_datetime('today').date())
        book = pd.DataFrame(book)
        readinglog = pd.concat([readinglog, book], axis=0)
        backlog.drop(book_index, axis='rows', inplace=True)
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
    backlog.apply(get_backlog, axis=1).apply(print)


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

    reading_menu = lambda m: f'''
    READING VIEW ({'Progress' if m else 'Backlog'} mode)
   *---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---=---*
    Sort by ...  -> s       Remove book  -> rb      Toggle progress or backlog mode      -> m
    Start book   -> sb      Edit book    -> eb      Add to backlog -> b      Update page -> p
'''
    usr_input = ''
    reading_mode = True
    sort_modes = {
        'p': 'priority',
        't': 'title',
        'a': 'author',
        'l': 'pages'
    }
    sort_mode = 'p'

    while usr_input != 'q':
        match usr_input:
            case 's':
                print('''
Sort by ...
priority -> p title -> t
author   -> a length -> l
'''
                      )
                sort_mode = input('Enter command: ')
            case 'sb':
                add_to_reading(r_df, b_df, r_csv, b_csv)
                r_df, b_df, r_csv, b_csv = load_logs()
            case 'rb':
                remove_book(r_df, b_df, r_csv, b_csv)
                r_df, b_df, r_csv, b_csv = load_logs()
            case 'eb':
                edit_book(r_df, b_df, r_csv, b_csv)
                r_df, b_df, r_csv, b_csv = load_logs()
            case 'p':
                update_current_page(r_df, b_df, r_csv, b_csv)
                r_df, b_df, r_csv, b_csv = load_logs()
            case 'm':
                reading_mode = False if reading_mode else True
            case 'b':
                add_to_backlog(b_df, b_csv)
                r_df, b_df, r_csv, b_csv = load_logs()
            case 'q':
                print('Back to main menu...')
            case other:
                pass

        clear_terminal()
        print(reading_menu(reading_mode))
        if reading_mode:
            display_progress_view(r_df.sort_values(by=sort_modes[sort_mode]))
        else:
            display_backlog_view(b_df.sort_values(by=sort_modes[sort_mode]))

        usr_input = input('Enter a command: ')


# ----------------------------------------------------------------------------------------------------------------------
# MAIN LOOP:

main_menu = '''
        ██████   █████  ██████  ███████ ██      ███    ███  █████  ██████  ██   ██ 
        ██   ██ ██   ██ ██   ██ ██      ██      ████  ████ ██   ██ ██   ██ ██  ██  
        ██████  ███████ ██████  █████   ██      ██ ████ ██ ███████ ██████  █████   
        ██   ██ ██   ██ ██   ██ ██      ██      ██  ██  ██ ██   ██ ██   ██ ██  ██  
        ██████  ██   ██ ██████  ███████ ███████ ██      ██ ██   ██ ██   ██ ██   ██ 
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
