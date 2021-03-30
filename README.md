# pyCV
Python CV compiler to replace LaTeX attempts

## available commands
# supplimentary control commands
    info(arg)
gives info to heading used on documents

    doctype(type)
sets the doctype for the footer 

    footer(arg)
required for pyCV to draw a footer

args unsupported right now, just leave it at "full"

# creation commands
    heading(arg)
creates a heading with arg text

    subheading(arg)
creates a subheading with arg text

    bulktext()
adds the text below as a block of text.

    list()
adds the lines below as a bullet pointed list
use a new line to separate list elements

    headlist()
adds the lines below as a headed list, separate heading from content with |
use a new line to separate list elements
formatted as:
HEADING: | LIST TEXT

    dated()
useful for experiences, adds a compound block with info sections and the ability to add text under
REQUIRES
    who(arg)   arg = company or bureau
    what(arg)  arg = job/degree title
    where(arg) arg = location
    when(arg)  arg = date of occurrence

dated blocks also REQUIRE:
    enddated()
used to tell pyCV that you are finshed adding text for the current date block

to add another experience use
    nextdated()
will start a new block

# basic formatting
    spacer(arg)
adds arg amount of whitespace. Useful for forcing the format to behave

    newpage()
forces a new page