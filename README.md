# pyCV
Python CV compiler to replace LaTeX attempts

# housekeeping
pyCV will read a source file (examples provided in MASTER_EG) and build your cv, cover letter and reference table as a pdf document.

Source files are formatted with a command starting with // and being the first element on a line. Some commands require arguments, others are optional

Items bounded by {brackets} can be replaced at compile, provided the "replacements" dict is populated (at the bottom of the script)
simply add a new item to the dict, where the key is the text in the brackets and the value is the desired text. The coverletter example has this set already, but to add more:

For example, if in your master text you have:

My favourite colour is {favouriteColour}.

A replacement dict of:

replacements = {'favouriteColour':'cyan'}

will produce the formatted text

"My favourite colour is cyan."

# available commands
## supplimentary control commands
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

	font(AREA) fontname
will update the AREA with fontname.
Valid regions for AREA are:
	bold : Used for headers and titles
	italic : Used for emphasis
	text : Used in most places within the document
	thin : Used for adding contrast to some text
fontname must be a valid font file in ./font/ with name fontname.ttf
default fonts will be used if this command is not present.

# basic formatting
    spacer(arg)
adds arg amount of whitespace. Useful for forcing the format to behave

    newpage()
forces a new page