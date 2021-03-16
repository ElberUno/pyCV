# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 19:22:13 2021

@author: Louis Beal
"""

import os,io,sys,pathlib,math
import pandas as pd
import numpy as np

from fpdf import FPDF
from datetime import datetime

fonts = os.listdir('font/')
icons = os.listdir('icon/')


#### debug ####
debug = False
###############

def parseText():
    
    with io.open("content.txt","r",encoding="utf-8") as o:
        #read content file, splitting by section
        content = o.read().split("//")
        
    content = [x.strip() for x in content if x != ""]
        
    data = {"command":[],"args":[],"values":[]}
    for item in content:
            
        #index brackets from start and split on those indices
        b1 = item.index("(")
        b2 = item.index(")")
        
        com = item[:b1].strip()
        arg = item[b1+1:b2].strip()
        val = item[b2+1:].strip()
        
        data["command"].append(com)
        data["args"].append(arg)
        
        if com in ["list","headlist"]:
            data["values"].append(val.split("\n"))
        else:
            data["values"].append(val)
    
    data = pd.DataFrame(data)
        
    return(data)
        
class PDF(FPDF):
    
    #need to extend FPDF for footer to function properly

    def create(self,
               maincolour = [60,60,60],
               textcolour = [90,90,90],
               lightcolour = [140,140,140],
               accentcolour = [210,60,60]):
        
        #driver function to read in data and compile the PDF
        
        
        #supplimentary data
        self.version = "v0.0.2"
        
        #templating, set colours, font sizes and font tables
        self.colour = {"main":maincolour,
                        "text":textcolour,
                        "light":lightcolour,
                        "accent":accentcolour}
        
        self.fontsize = {"name":32,
                          "heading":14,
                          "subheading":12,
                          "text":10,
                          "contact":7.6}
        
        self.font = {"bold":"Roboto-Bold",
                     "thin":"Roboto-Thin",
                     "text":"Roboto-Regular",
                     "italic":"Roboto-Italic"}
        
        #init blank pdf
        self.initialisation()
        #set layout settings
        self.layout()
        
        #enable/disable debug constructs
        if debug:
            self.enableDebug()
        else:
            self.b = 0
        
        #process commands
        
        self.commandState = "run"
        self.store = []
        self.temp = {}
        self.textContent = ""
        
        i = 0
        while i < len(self.content):
            
            com = self.content.iat[i,0]
            arg = self.content.iat[i,1]
            val = self.content.iat[i,2]
            
            self.processCommand(com,arg,val)
            
            i += 1
        
        self.save()
        
    def initialisation(self):
        #initialise a blank PDF for compilation        
        self.addFonts() #add fonts
        self.set_margins(0,0,0) #remove automatic margins
        
        #set manual margins and x/y spacing for cells
        self.xbuffer = 2.5
        self.ybuffer = 1
        
        #placement cursor, keep track for sequential cell addition
        self.cursor = {"x":0,"y":0}
        
        #parse content into commands, arguments and text
        self.content = parseText()
        
        #extract needed info such as document type, name, footer info, etc.
        self.userName = self.extractFromContent("info","name")        
        self.footerType = self.extractFromContent("footer")            
        self.sidebar = self.extractFromContent("sidebar")
        
        
        self.add_page()
                
        self.set_xy(0,0)
        
    def layout(self):
        
        #set margins, using internal margins
        
        if self.sidebar:
            #using a sidebar, start here by cutting the page
            
            self.set_fill_color(*self.colour["accent"])
            self.rect(0,0,self.w/3,self.h,"F")
            self.width = self.w/3
            
            self.margins = 2
            
        else:
            self.margins = 14
            self.width = self.w
            
        self.vmargins = 10
        
        self.l_margin = self.margins
        self.r_margin = self.margins
        self.t_margin = self.vmargins
        self.b_margin = self.vmargins
        
        self.c_margin = 0 #seems to be the offset for text within a cell
                    
        self.edge = {"l": self.l_margin,
                     "t": self.t_margin,
                     "r": self.width - self.r_margin,
                     "b": self.h - self.b_margin}
        
        self.set_xy(self.l_margin,self.t_margin)
        
    def extractFromContent(self,command,args=None):
        #extract data from selected command
        
        if not args:
            
            if command in list(self.content["command"]):
                val = self.content.loc[(self.content["command"] == command)]["args"].values[0]
                return val.lower() != "false"
            else:
                return None
            
        else:
            
            return self.content.loc[(self.content["command"] == command) & 
                                    (self.content["args"] == args)]["values"].values[0]
    
    def addFonts(self):
        
        #read in fonts and add them to the PDF for usage
        
        for fontName in fonts:
            name = fontName.split(".")[0]
            ttype = fontName.split(".")[1]
            
            if ttype in ["ttf"]:
                path = str(pathlib.Path().absolute()) + "\\font\\" + fontName
                
                self.add_font(family=name,fname=path, uni= True)
        
    def enableDebug(self):
        
        self.b = 1
        
        self.rectCoord(self.l_margin,
                       self.t_margin,
                       self.width-self.r_margin,
                       self.h-self.b_margin)
        
    def processCommand(self,com,arg,val):
        
        #command states override other commands
        #allows for nested items
        state = self.commandState
        if state == "dated":
            
            if com == "enddated":
                
                self.commandState = "run"
                self.store.append(self.temp)
                self.temp = {}
                for block in self.store:
                    
                    self.addDateBlock(block)
                    
                self.store = []
                    
            elif com == "nextdated":
                self.store.append(self.temp)
                self.temp = {}
                
            else:
                self.temp[com] = (arg,val)
                
        elif state == "info":
            
            #if the info flag is set, but a new command is passed
            #process info block and process the current command using recursion
            if com != "info":
                
                self.addInfo()
                
                self.commandState = "run"                
                self.processCommand(com,arg,val)
                
            else:                
                self.temp[arg] = val
        
        
        else:
            if com == "newpage":
                
                #force new page by writing empty string to end of page and resetting y
                self.addText(text="",x=self.l_margin,y = self.h,font="thin")
                self.set_y(self.t_margin)
                
            elif com == "info":
                self.commandState = "info"
                self.processCommand(com,arg,val)
            
            elif com == "subheading":                
                self.addHeader(arg,sub=True)
                    
            elif com == "heading":
                self.addHeader(arg)
                
            elif com == "bulktext":                
                self.addText(val)
                
            elif com == "dated":        
                print("\tstarting date block")
                self.commandState = "dated"
                    
            elif com == "list":                
                print("create list:")
                print("\t",arg,val)
                
                self.addList(val)
                
            elif com == "headlist":                
                print("create headed list:")
                print("\t",arg,val)
                
                self.addList(val, headings = True)            
    
    #### override default functions ####    
    def set_x(self, x):
        #Set x position
        if(x>=0):
            self.x=x
        else:
            self.x=self.w-x    
            
    def set_y(self, y):
        #Set y position
        # print("\t\ty set to {}".format(y))
        self.x=self.l_margin
        if(y>=0):
            self.y=y
        else:
            self.y=self.h-y
    
    def step_y(self,step=None):
        
        if not step:
            step = self.ybuffer
            
        y = self.get_y()
        self.set_y(y+step)
    
    def set_xy(self, x,y):
        "Set x and y positions"
        self.set_y(y)
        self.set_x(x)
        
    def footer(self):
        #replace FPDF footer class with manual footer
        #called by add_page and output
        
        if self.footerType:
            
            edgeStore = self.edge["r"]
            self.edge["r"] = self.w
            oldCommand = self.commandState
            self.commandState = "footer"
        
            print("drawing footer "+"#"*24)
            
            y = self.h - 10
            
            #print centered "name    cv"
            footerText = "{}    ~    {}".format(self.userName, "Curriculum Vitae")
            x = self.w/2
            self.addText(footerText,x,y,font = "text",
                         size="contact",colour= "light",align = [0.5,0])
            
            # Print page number on right        
            pageNo = "Page {}/{}".format(self.page_no(),self.alias_nb_pages())
            x = self.w - self.margins
            self.addText(pageNo,x,y,font = "text",
                         size="contact",colour= "light",align = [1,0])
                
            #might as well self credit
            version = "Compiled {}".format(datetime.now().strftime("%d %B, %Y"))        
            x = self.margins
            self.addText(version,x,y,font = "text",
                         size="contact",colour= "light")
            
            self.commandState = oldCommand
            self.edge["r"] = edgeStore
        
    #### internal placement functions ####
        
    def drawCross(self,x,y,r=1,rot=0):
        
        if rot !=0:
            self.rotate(-rot,x,y)
        
        self.line(x-r,y-r,x+r,y+r)
        self.line(x-r,y+r,x+r,y-r)
        
        if rot !=0:
            self.rotate(0,x,y)
        
    
    def rectCoord(self,x1,y1,x2,y2, mode = "D"):
        
        #draw rectangle by coordinates rather than w,h
        
        #ensure correct placement order
        
        xa = max(x1,x2)
        ya = max(y1,y2)
        xb = min(x1,x2)
        yb = min(y1,y2)
        
        w = xb - xa
        h = yb - ya
        
        self.rect(xa,ya,w,h,mode)
    
    def addInfo(self):
        
        info = self.temp
        
        self.temp = {}
        
        print("adding info block")
        
        #colour, size, font
        styles = {"name":[["light","main"],["name","name"],["text","bold"]],
                  "address":["light","contact","italic"],
                  "other":["main","contact","text"]}
        
        store = []
        links = []
        for key in info.keys():
            
            val = info[key]
            
            if key not in styles.keys():
                oldkey = key
                key = "other"
                
            colour = styles[key][0]
            size = styles[key][1]
            font = styles[key][2]
            
            midx = self.width/2
            if key == "name":                
                #name needs unique spacing and formatting
                
                fname = " ".join(val.split(" ")[:-1])
                lname = val.split(" ")[-1]
                
                name = [fname,lname]
                
                self.addText(name,x=midx,font=font,size=size,colour=colour)
                
            elif key == "address":
                
                self.addText(val,x=midx,font=font,size=size,colour=colour,align=[0.5,0])
                
            else:
                
                store.append(oldkey + ": " + val)
                
                if oldkey.lower() in ["git","github"]:
                    links.append("www.github.com/"+val)
                else:
                    links.append(None)
                
        self.addText(store,x = midx,font=font,size=size,colour=colour,link=links,multi=" | ")
        
    def addText(self,text,x=None,y=None,
                font="text",size="text",colour="text",link=None,multi=" ",
                align=[0,0],rot=0,
                step=True):
        #smarter call for FPDF.cell function
        #place an aligned text cell exactly bounding the text
        
        #if no x,y given, use the current cursor position
        #font and size default to regular text
        #alignment is the x/y of the corner chosen. 0-1 range
        #rot is clockwise rotation
        
        ptmm = 0.352778 #points to mm conversion
        
        if not x:
            x = self.get_x()
        if not y:
            y = self.get_y()
            
        self.step_y()
        
        #if lists, call multiple times and return
        #alignment persists over whole block
        if type(text) == list:
            
            # print("list of texts, using recursion")
            
            widths = [0]
            heights = []
            texts = []
            sizes = []
            fonts = []
            links = []
            colours = []
            
            for i in range(len(text)):
                
                tempText = text[i]
                
                if type(size) == list:
                    tempSize = size[min(i,len(size))]
                else:
                    tempSize = size
                    
                if type(font) == list:
                    tempFont = font[min(i,len(font))]
                else:
                    tempFont = font
                
                if type(link) == list:
                    tempLink = link[min(i,len(link))]
                else:
                    tempLink = link
                
                if type(colour) == list:
                    tempColour = colour[min(i,len(colour))]
                else:
                    tempColour = colour
                             
                if i != len(text) -1:
                    tempText += multi
                
                self.set_font(self.font[tempFont], size = self.fontsize[tempSize])
                widths.append(self.get_string_width(tempText))
                heights.append(self.fontsize[tempSize]*ptmm)
                
                texts.append(tempText)
                sizes.append(tempSize)
                fonts.append(tempFont)
                links.append(tempLink)
                colours.append(tempColour)
                
            basex = x - sum(widths)/2 #centre point      
            
            for i in range(len(texts)):
                
                tempText = texts[i]
                tempSize = sizes[i]
                tempFont = fonts[i]
                tempColour = colours[i]
                
                if link:
                    tempLink = link[min(i,len(link))]
                else:
                    tempLink = None
                print("{}, adding {}".format(tempText,sum(widths[:i+1])))
                tempx = basex + sum(widths[:i+1])
                tempy = y + max(heights) #base aligned if the sizes differ
                
                if type(tempText) == list:
                    raise Exception("multi-layered recursion found, halting")
                    
                self.addText(tempText,tempx,tempy,tempFont,tempSize,tempColour,tempLink, align = [0,1]) 
            
            #do not process for listed inputs
            return
           
        text = text.replace("\n"," ")
        
        self.set_font(self.font[font], size = self.fontsize[size])    
        self.set_text_color(*self.colour[colour])
        width = round(self.get_string_width(text),2)
        height = self.fontsize[size]*ptmm 
        
            
        print("adding text {}... at {},{} (align {})".format(text[:5],round(x,2),round(y,2),align))
        
        if link:
            print("link {}".format(link))
        
        if self.b == 1:
            self.drawCross(x, y, rot = 45)
            
        #rotate around intended coordinates, not shifted
        rx = x
        ry = y
            
        x = x - width*align[0]
        y = y - height*align[1]
            
        self.set_xy(x,y)
        
        if rot != 0:
            #rotate canvas before placement
            #-ve rotation as canvas is moving
            self.rotate(-rot,rx,ry)
        
        #calculate available space
        rotPi = math.radians(rot)
        available = round((self.edge["r"] - x)*math.cos(rotPi) + 
                          (self.h - y)*math.sin(rotPi),2)
        
        #Round the measurements, a 0.00000000000002 difference was throwing it off
        if width > available:
            print("\t using justified mulitCell")
            
            textAlign = "J"
            cellWidth = available
            
        else:
            # self.cell(width, height, text, border = self.b, align = "C", link=link)
            textAlign = "L"
            cellWidth = width*1.0005 #multicell is very trigger happy on the newlines
        
        if link:
            self.cell(width, height, text, border = self.b, align = "C", link=link)
        else:
            self.multi_cell(cellWidth, height, text, border = self.b, align = textAlign)
        
        if rot != 0:
            #fix any rotation
            self.rotate(0,rx,ry)
        
        if self.b == 1:
            self.drawCross(x, y)
        
        nLines = math.ceil(width/available)
        
        #prevent runaway pages
        if (y > self.h - (self.t_margin + self.b_margin)) and not self.commandState == "footer":
            print("oh shit "*24)
            
            self.set_y(0)
        
        if step:
            self.step_y()
        
        #return original bounding box
        return(x,y,x+width,y+height*nLines)
        
    def addHeader(self,heading,sub=False,rotated=False):
                
        self.step_y(self.ybuffer*3)
        
        y = self.get_y()
        
        if not rotated:
        
            if sub:
                y += 3
                print("adding subheading {}... at y={}".format(heading,y))
                box = self.addText(heading,font = "bold",colour = "main" ,size="subheading")
                
            else:
                y += 6
                print("adding heading {}... at y={}".format(heading,y))
                box = self.addText(heading,font = "bold",colour = "main", size="subheading")
                
            self.set_draw_color(*self.colour["main"])
            
            if not sub:
                
                y = box[1] + (box[3]-box[1]) * 3/4
                
                self.line(box[2]+1, y ,self.width-self.r_margin, y)
                
        else:
            
            #add fancy rotated headers
            pass
        
        self.step_y()
    
    def addDateBlock(self,block):
        #constant functions to head the block
        const = {"who":None,
                 "what":None,
                 "where":None,
                 "when":None}
        
        styles = {"who":[0,0,"bold","text","main"],
                 "what":[0,1,"text","text","text"],
                 "where":[1,0,"italic","text","accent"],
                 "when":[1,1,"italic","text","text"]}
        
        subs = {}
        
        for key in block.keys():
            if key == "dated":
                pass
            elif key in const.keys():
                const[key] = block[key][0]
            else:
                #subsidiary command, process as needed
                subs[key] = block[key]
                
        #handle main secton
        basey = self.get_y() + self.ybuffer
        for key in const.keys():
            
            text = const[key]
            gridx = styles[key][0]
            gridy = styles[key][1]
            font = styles[key][2]
            size = styles[key][3]
            colour = styles[key][4]
            
            print(text,font,size,colour)
            
            if gridx == 0:
                x = self.l_margin
            else:
                x = self.width - self.r_margin
            
            if gridy == 0:
                box = self.addText(text, x, basey, font, size, colour, align = [gridx,0])
                lowy = box[3]+self.ybuffer
            else:
                box = self.addText(text, x, lowy, font, size, colour, align = [gridx,0])
                    
        #between bulk date block and supplimentary details
        self.step_y() #add some separation
                
        for com in subs.keys():
            arg = subs[com][0]
            val = subs[com][1]
            
            self.processCommand(com,arg,val)
            
        self.step_y(self.ybuffer) #add some separation after block
                
    def addList(self, listvals, headings = False):
        
        if not headings:
            heads = ["• "]*len(listvals)
            bodies = listvals
                
        else:
            
            heads = []
            bodies = []
            for item in listvals:
                heads.append(item.split("|")[0].strip())
                bodies.append(item.split("|")[1].strip())
                
        y = self.get_y() 
        
        #find longest heading to index from
        maxlen = max(heads, key=len)
        
        fsize = "text"
        
        maxw = self.get_string_width(maxlen)
        midx = self.l_margin + maxw
        
        for i in range(len(heads)):
            x = midx
            
            self.addText(heads[i], x, y, font = "bold", size = fsize, align = [1,0],step=False)
            self.addText(bodies[i], x+self.xbuffer, y, font = "text", size = fsize, align = [0,0],step=False)
            
            y = self.get_y() + self.ybuffer
               
        y = self.step_y()
        
    def save(self):
        self.output("testcv.pdf")

if __name__ == "__main__":
    
    content = parseText()
    
    cv = PDF()    
    cv.create()