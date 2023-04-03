# Babelmark: one bookmark to rule them all

  A simple CLI (for now) reading management app.

 ## Outline:
     
       This reading-management application will have a command-line interface,
     and will store the data files it uses locally.
     
  ### Purpose:
  
      This program has three core purposes to serve for a user:
     
      - For books they're currently reading:
          - Tracking what page they're on, and their overall progress in the book. 
          - Sorting and viewing their books data according to any variables.
       
      - For books they intend to read:
          - Tracking the order they intend to read them in.
          - Providing a way to easily add or remove books to their backlog.
          - Provide a way to change the priority of any book in their backlog.
          - Sorting and viewing backlog according to any variable.
          - Providing a way to move a book from the backlog to the books in progress.
         
      - For books they have finished:
          - Provide a timestamp for the day they finished a book.
          - Provide a history of finished books.

  ### Dependencies:
  
        The CSV library will be used in this program in order to efficiently read and write to the
      csv files used to store user data.
  
        The Numpy and Pandas libraries will be used in this program, as the csv files correspond with
      tabular representations of data such as Pandas DataFrames, and both libraries will facilitate
      efficient operations with this kind of data.
