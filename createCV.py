# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 15:11:00 2021

@author: Louis Beal
"""

import os,io,sys,pathlib
import pandas as pd

from fpdf import FPDF
from datetime import datetime

sys.path.append("C:\\Users\\pc\\Documents\\Python Scripts\\misc\\wordstats\\")

import wordstats

fonts = os.listdir('font/')
icons = os.listdir('icon/')


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

class CV(FPDF):
    
    #need to extend FPDF for footer to function properly
    
    def inert(self,
                 maincolour = [60,60,60],
                 textcolour = [90,90,90],
                 lightcolour = [140,140,140],
                 accentcolour = [210,60,60]):
        
        #### debug ####
        debug = False
        ###############
        
        self.colours = {"main":maincolour,
                        "text":textcolour,
                        "light":lightcolour,
                        "accent":accentcolour}
        
        self.fontsizes = {"name":32,
                          "heading":14,
                          "subheading":10,
                          "text":9,
                          "contact":7.6}
        
        # self = FPDF(orientation='P', unit='mm', format='A4')
                
        self.version = "v0.0.1"
        
        self.addFonts()
        self.inset = 14
        self.margin = 2.5
        self.vmargin = 0.5
        self.placement = {"x":0,"y":0}
        
        
        self.font_bold = "Roboto-Bold"
        self.font_norm = "Roboto-Light"
        
            
        self.content = parseText()
        
        self.userName = self.content.loc[(self.content["command"] == "info") &
                                         (self.content["args"] == "name")]["values"][0]
        
        self.add_page()
        
        if debug:
            self.enableDebug()
        else:
            self.b = 0
            
        storage = {}
        store = None
        i = 0
        while i < len(self.content):
            
            com = self.content.iat[i,0]
            arg = self.content.iat[i,1]
            val = self.content.iat[i,2]
            
            if com == "info":
                
                storage[arg.lower()] = val                
                store = "info"
                
            elif store:
                if store == "info":
                    
                    name = storage["name"]
                    addr = storage["address"]
                    num = storage["mobile"]
                    email = storage["email"]
                    git = storage["github"]
                    
                    self.addTitleSection(name, addr, num, email, git)
                    
                    store = None                    
               
            if com == "newpage":
                
                #force new page by writing empty string to end of page and resetting y
                self.textCell(x=self.inset,y = self.h,text="",font="Roboto-Thin")
                self.updatePlacement(y = self.inset)
               
            if com == "subheading":
                
                self.addHeader(arg,sub=True)
                    
            if com == "heading":
                self.addHeader(arg)
                
            if com == "bulktext":                
                self.addBulkText(val)
                
            if com == "list":
                
                print("create list:")
                print("\t",arg,val)
                
                self.addList(val, extramargin = 3)
                
            if com == "headlist":
                
                print("create headed list:")
                print("\t",arg,val)
                
                self.addList(val, extramargin = 3, headings = True)
                
                
            if com == "dated":        
                
                #stretch down the content until end of date block is found
                j = i
                
                #create blocks
                blocks = []
                temp = {}
                while self.content.iat[j,0] != "enddated":
                    
                    com = self.content.iat[j,0]
                    arg = self.content.iat[j,1]
                    val = self.content.iat[j,2]
                    
                    print(com)
                    
                    if com == "nextdated":
                        blocks.append(temp)
                        temp = {}
                    else:
                        temp[com] = (arg,val)
                    
                    j+=1                    
                    if j > len(self.content):
                        
                        raise Exception("No end to dated block found")                        
                        break
                
                i = j #skip processed lines and continue
                
                blocks.append(temp)
                
                for block in blocks:
                    
                    self.addDateBlock(block)
                
            i += 1
        
    def updatePlacement(self,x=None,y=None):
        
        if not x:
            newx = self.get_x()
        else:
            newx = x
            
        if not y:
            newy = self.get_y()
        else:
            newy = y
        
        if newy > self.h:
            y = self.inset
        
        self.placement = {"x":newx,"y":newy}
        
    def enableDebug(self):
        
        self.b = 1
        
        #draw width margins
        self.line(self.inset,0,self.inset,self.h)
        self.line(self.w - self.inset,0,self.w - self.inset,self.h)
        
    def addFonts(self):
        
        for fontName in fonts:
            name = fontName.split(".")[0]
            ttype = fontName.split(".")[1]
            
            if ttype in ["ttf"]:
                path = str(pathlib.Path().absolute()) + "\\font\\" + fontName
                
                self.add_font(family=name,fname=path, uni= True)
        
        
    def footer(self):
        print("drawing footer "+"#"*24)
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        
        self.set_font('Roboto-Regular', size = self.fontsizes["contact"])
        
        #print centered "name    cv"
        footerText = "{}    ~    {}".format(self.userName, "Curriculum Vitae")
        self.cell(0, 10, footerText, align = 'C')
        
        # Print page number on right        
        pageNo = "Page {}/{}".format(self.page_no(),self.alias_nb_pages())
        width = self.get_string_width(pageNo)
        self.set_x(self.w - self.inset- width)
        self.cell(width, 10, pageNo, align = 'L')
            
        #might as well self credit
        version = "Compiled {}".format(datetime.now().strftime("%d %B, %Y"))
        self.set_x(self.inset)
        self.cell(width, 10, version, align = 'L')
        
        
    def detailColumn(self,fraction = 0.33):
        
        x2 = round(self.w * fraction)
        y2 = self.h
        
        self.set_fill_color(*self.colours["accent"])
        
        self.rect(0,0,x2,y2,"F")
        
    def textCell(self,x,y,text,font,size="text",colour="main",align = 'L',link=None):
        
        print("creating text cell ({}...) at {}, {}".format(text[:5],round(x,2),round(y,2)))
        
        ptmm = 0.352778
        
        fontsize = self.fontsizes[size]
        fontcol = self.colours[colour]
        
        inset = self.inset
        margin = self.margin
        vmargin = self.vmargin
        
        self.set_font(font,size=fontsize)
        
        twidth = self.get_string_width(text)
        
        # print(text,twidth)
        
        if align[0] == "L":
            x -= (twidth + margin/2)
        elif align[0] == "C":
            x -= twidth/2
        else:
            x += margin/2
         
        if len(align) > 1:
            if align[1] == "U":            
                y -= (fontsize*ptmm)
            else:
                y += vmargin/2
        else:
            y += vmargin/2
        
        if x < inset:
            x = inset
        
        self.set_xy(x,y)
        self.set_text_color(*fontcol)
        self.cell(w=twidth, h=(vmargin/2)+fontsize*ptmm, align=align, txt=text, border=self.b, link = link)
    
        self.updatePlacement(y=y + vmargin+fontsize*ptmm)
        
    
    def addHeader(self,heading,sub=False):
        
        ptmm = 0.352778
        
        if sub:
            fontsize = self.fontsizes["subheading"]
            self.set_font("Roboto-Bold",size=fontsize)
            y = self.placement["y"] + 3
            print("adding subheading {}... at y={}".format(heading,y))
            
        else:
            fontsize = self.fontsizes["heading"]
            self.set_font("Roboto-Bold",size=fontsize)
            y = self.placement["y"] + 6
            print("adding heading {}... at y={}".format(heading,y))
        
        
        fontcol = self.colours["main"]
        
        inset = self.inset
        margin = self.margin
        vmargin = self.vmargin
        
        twidth = self.get_string_width(heading)
        self.set_xy(inset,y)
        self.set_text_color(*fontcol)
        self.cell(w=twidth+margin, h=(vmargin)+fontsize*ptmm,txt=heading,border=self.b)
        
        #x at edge margin
        x = inset+twidth + margin
        y =  y-(margin/4)+fontsize*ptmm
        
        self.set_draw_color(*self.colours["main"])
        if not sub:
            self.line(x,y ,self.w-inset,y)
        
        self.updatePlacement(y=y)
        
    def addName(self, name, bold = "last"):
        
        
        name = name.split(" ")
        
        #get name cell sizes
        sizes = [0]
        for i in range(len(name)):
            if (i == len(name) -1) and (bold == "last"):
                self.set_font(self.font_norm,size = self.fontsizes["name"])
            else:
                self.set_font(self.font_bold,size = self.fontsizes["name"])
            
            temp = name[i]
            sizes.append(self.get_string_width(temp))
        
        
        midx = self.w/2
        for i in range(len(name)):
            temp = name[i]
            x = midx - sum(sizes)/2 + sum(sizes[:i+1])
            
            x+= i*2 #extra spacing
            
            if (i == len(name) -1) and (bold == "last"):
                self.textCell(x, 6, temp, self.font_bold, size = "name", align = "R")
            else:
                self.textCell(x, 6, temp, self.font_norm, size = "name", align = "R")
    
    def addContacts(self,mob,email,git=None):
        data = {}
        fields = ["mobile","email","git"]
        
        i=0
        for item in mob, email, git:
            data[fields[i]] = item
            
            i+=1
        
        font = "Roboto-Regular"
        
        self.set_font(font,size = self.fontsizes["contact"])
        self.set_text_color(*self.colours["main"])
        sizes = [0]
        
        i = 0
        for item in data.keys():
            if i != 0:
                text = " | "
            else:
                text = ""
                
            text += item +": " + data[item]
            
            sizes.append(self.get_string_width(text))
            
            i += 1            
        
        midx = self.w/2
        y = self.placement["y"]
        i = 0
        for item in data.keys():
            text = data[item]
            x = midx - sum(sizes)/2 + sum(sizes[:i+1])
            
            x+= i #extra spacing
            
            if i != 0:
                text = " | "
            else:
                text = ""
                
            text += item +": " + data[item]
            
            if item == "git":
                link = "www.github.com/"+data[item]
            else:
                link = None
            
            self.textCell(x, y, text, font, size = "contact", align = "R",link=link)
            
            i += 1            
            
    def addTitleSection(self, name, addr, num, email, git):
        
        midx = self.w/2
        print("adding name")
        self.addName(name)
        print("adding address")
        
        self.textCell(midx, self.placement["y"], addr, "Roboto-Italic", size = "contact", colour = "light", align = "C")
        
        print("adding contacts")
        self.addContacts(num, email, git)
        
        
    def addBulkText(self,text,font = "Roboto-Light", extramargin = 3):
        
        text = text.replace("\n", " ")
        
        x = self.inset
        y = self.placement["y"] + extramargin
        
        self.set_xy(x,y)
        self.set_font(font)
        self.set_text_color(*self.colours["text"])
        self.set_font_size(self.fontsizes["text"])
        h = self.fontsizes["text"]/2
        w = self.w - self.inset*2
        
        self.multi_cell(w,h,text,border=self.b)
        
        self.updatePlacement()
        
    def addList(self,listvals,font = "Roboto-Light", extramargin = 0, headings = False):        
        
        
        ptmm = 0.352778
        
        self.updatePlacement(y=self.placement["y"] + extramargin)
        
        if not headings:
            for item in listvals:
                
                item = "• " + item
                
                self.addBulkText(item, font, extramargin = 0)
                
        else:
            basey = self.placement["y"]
            
            # self.font_bold = "Roboto-Bold"
            # self.font_norm = "Roboto-Thin"
            heads = []
            bodies = []
            for item in listvals:
                heads.append(item.split("-")[0].strip())
                bodies.append(item.split("-")[1].strip())
                
            #find longest heading to index from
            maxlen = max(heads, key=len)
            
            fsize = self.fontsizes["text"]            
            self.set_font(self.font_bold)
            self.set_font_size(fsize)
            
            maxw = self.get_string_width(maxlen)
            midx = self.inset + maxw + self.margin
            
            for i in range(len(heads)):
                x = midx
                y = basey + i*fsize/2
                
                print(x,y)
                self.set_xy(x,y)
                self.cell(maxw, ptmm*fsize, txt = heads[i], border=self.b, align = "R")
                
            self.set_font(self.font_norm)
            for i in range(len(bodies)):                
                
                x = midx + maxw
                y = basey + i*fsize/2
                
                print(x,y)
                self.set_xy(x,y)
                self.cell(maxw, ptmm*fsize, txt = bodies[i], border=self.b, align = "L")
        
    def addDateBlock(self,block):
        #constant functions to head the block
        const = {"who":None,
                 "what":None,
                 "where":None,
                 "when":None}
        
        # x,y,text,font,size="text",colour="main",align = 'C',link=None
        styles = {"who":[0,0,"Roboto-Bold","text","main"],
                 "what":[0,1,"Roboto-Regular","text","text"],
                 "where":[1,0,"Roboto-Italic","text","accent"],
                 "when":[1,1,"Roboto-Italic","text","text"]}
        
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
        basey = self.placement["y"]
        for key in const.keys():
            
            text = const[key]
            gridx = styles[key][0]
            gridy = styles[key][1]
            font = styles[key][2]
            size = styles[key][3]
            colour = styles[key][4]
            
            if gridx == 0:
                x = self.inset
            else:
                x = self.w - self.inset
            
            if gridy == 0:
                y = basey + 4
            else:
                y = basey + 8
            
            self.textCell(x, y, text, font, size, colour)
            
        for com in subs.keys():
            arg = subs[com][0]
            val = subs[com][1]
            if com == "bulktext":
                
                self.addBulkText(val, extramargin = 1)     
                    
            if com == "subheading":
                
                self.addHeader(arg,sub=True)
                
            if com == "list":
                
                print("create list:")
                print("\t",arg,val)
                
                self.addList(val)
        
    def save(self):
        self.output("testcv.pdf")
    
    
    
if __name__ == "__main__":
    
    cv = CV()    
    cv.inert()
    cv.save()
    """
    print("\n"+"#"*24)
    print("scanning CV text contents for repeated language")
    print("#"*24)
    
    content = parseText()
    
    bulkcontent = list(content.loc[content["command"].isin(("bulktext","list"))]["values"])
    
    prescan = ""
    for item in bulkcontent:
        if type(item) == list:
            prescan += " ".join(item)
            
        else:
            prescan += item
            
    wordstats.process(prescan,False)"""