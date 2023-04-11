import pandas as pd
import math
from os import system, name


# # VIEW FUNCTIONS:
# def get_progress(df_row):
#     '''
#     Takes a single row from the reading log dataframe.
#     Returns a string containing the title and author of a book,
#     as well as a percentage and progress bar.
#     '''
#     block = u"\u2588"
#     empty_block = u"\u2591"
#     percentage = round((df_row.current_page/df_row.pages)*100, 2)
#     progress_bar = block*math.ceil(percentage) + empty_block*(100 - math.ceil(percentage))
#     return f"'{df_row['title']}' by {' & '.join(df_row['author'].split('/'))}: {percentage}%\n{progress_bar}"
#
#
# def display_progress_view(df):
#     '''
#     Takes the reading log dataframe, and prints the string
#     returned from get_progress for each row, sorted by priority.
#     '''
#     df.sort_values(by='priority').apply(get_progress, axis=1).apply(print)


# def get_backlog(df_row):
#     '''
#     Takes a single row from the backlog dataframe.
#     Returns a string containing a summary of a book.
#     '''
#     log = f'''
# "{df_row['title']}" by: {df_row['author']}
# {"Nonfiction" if df_row['nonfiction'] == 'yes' else 'Fiction'} -> {df_row['topic']} -> {df_row['subtopic']}
# Pages: {df_row['pages']}
# Priority: {df_row['priority']}
# '''
#     return log
#
#
# def display_backlog_view(df):
#     '''
#     Takes the backlog dataframe, and prints the string
#     returned from get_backlog for each row, sorted
#     by priority.
#     '''
#     df.sort_values(by='priority').apply(get_backlog, axis=1).apply(print)


# UTILITY FUNCTIONS:
def start_book(title, author, readinglog, backlog):
    '''
    Takes a title string, author string, and the reading log and backlog dataframes.

    Checks if book is in backlog; if so it moves the book from the backlog
    to the reading log and writes to their corresponding csv files. If it's not,
    the user is prompted for more info on the book, before it is added to the reading log
    and its csv file.

    Always sets the priority as the lowest priority (highest value).
    '''
    title = input('Title: ')
    author = input('Author: ')

    if title in backlog.title and author in backlog.author:
        book = backlog[(backlog.title == title) & (backlog.author == author)]
        book['priority'] = len(readinglog)
        book['current_page'] = 1
        book['date_started'] = str(pd.to_datetime('today').date())
        readinglog = pd.concat([readinglog, book], axis=0)
        backlog.drop(book['priority'], axis='rows')
        readinglog.to_csv('in_progress.csv')
        backlog.to_csv('backlog.csv')
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
        }]).set_index('priority')
        readinglog = pd.concat([readinglog, book], axis=0)
        readinglog.to_csv('in_progress.csv')
    print(f'"{title}" by: {author} successfully added to reading log.')


# def add_to_backlog(book, backlog):
#     '''
#     Takes a dictionary containing the data for a book, and the
#     backlog dataframe.
#     Adds the book to the backlog and its csv file,
#     after checking if it already exists.
#     Always sets priority to the lowest priority (highest possible).
#     '''
#
#     title_matches = backlog[backlog.title == book['title']]
#     full_matches = title_matches[title_matches.author == book['author']]
#     if len(full_matches) > 0:
#         print(f'''Cannot add "{book['title']}" by: {book['author']}; already exists in backlog.''')
#     else:
#         book_df = pd.DataFrame(book, index=[len(backlog)])
#         backlog = pd.concat([backlog, book_df], axis=0)
#         backlog.set_index('priority').to_csv('backlog.csv')
#         print(f'''Added "{book['title']}" by: {book['author']} to backlog.''')


# VIEW AND MENU LOOP:
# def clear_terminal():
#     if name == 'posix':
#         _ = system('clear')
#     else:
#         _ = system('cls')
#

rule_line = '-'*80
menu = f'''
BabelMark - Reading View:
{rule_line}
Progress View -> pv      Backlog View   -> bv      Quit  -> q
Category View -> cv      Start book     -> s       About -> a
Sorted by ... -> sv      Add to backlog -> b
'''

usr_input = ''
while usr_input != 'q':

    # Main menu:
    clear_terminal()
    print(menu, f'\n{rule_line}')

    match usr_input:
        # case 'pv':
        #     # Display progress-view menu and start view-loop.
        #     reading_data = pd.read_csv('in_progress.csv').set_index('priority')
        #     display_progress_view(reading_data)
        # case 'bv':
        #     # Display backlog-view menu and start view-loop.
        #     backlog_data = pd.read_csv('backlog.csv')
        #     display_backlog_view(backlog_data)d
        # case 's':
        #     # Refactor me by getting rid of .set_index() and modifying start_book().
        #     # This action should remain in both backlog and progress view menus.
        #     reading_data = pd.read_csv('in_progress.csv').set_index('priority')
        #     backlog_data = pd.read_csv('backlog.csv').set_index('priority')
        #
        #     start_book(title, author, reading_data, backlog_data)
        # case 'b':
        #     # Move this action into the backlog into the backlog-view menu and loop.
        #     backlog_data = pd.read_csv('backlog.csv')
        #     print('Please supply the following data:')
        #     title = input('Title: ')
        #     author = input('Author: ')
        #     nonfiction = input('Nonfiction? (yes/no): ')
        #     topic = input('Topic: ')
        #     subtopic = input('Subtopic: ')
        #     pages = input('Number of pages: ')
        #     book = {
        #         'priority': len(backlog_data),
        #         'title': title,
        #         'author': author,
        #         'nonfiction': nonfiction,
        #         'topic': topic,
        #         'subtopic': subtopic,
        #         'pages': int(pages)
        #    }
        #     add_to_backlog(book, backlog_data)
        case 'q':
            print('Quitting...')
        case '':
            # Display main menu view.
            reading_data = pd.read_csv('in_progress.csv').set_index('priority')
            display_progress_view(reading_data)
        case other:
            print('Unsupported command.')

    usr_input = input(f'{rule_line}\nEnter a command: ')
