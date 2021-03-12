# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 15:11:00 2021

@author: Louis Beal
"""

import os,io,sys,pathlib
import pandas as pd

from fpdf import FPDF

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
        
        if com == "list":
            data["values"].append(val.split("\n"))
        else:
            data["values"].append(val)
    
    data = pd.DataFrame(data)
        
    return(data)

class CV:
    
    def __init__(self,
                 maincolour = [60,60,60],
                 textcolour = [110,110,110],
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
                          "subheading":12,
                          "text":9,
                          "contact":7.6}
        
        self.cv = FPDF(orientation='P', unit='mm', format='A4')
        
        self.sizing()
        self.addFonts()
        self.inset = 14
        self.margin = 2.5
        self.vmargin = 0.5
        self.placement = {"x":0,"y":0}
        
        
        self.cv.add_page()
        
        if debug:
            self.enableDebug()
        else:
            self.b = 0
            
            
            
            
            
            
        
        self.content = parseText()
        
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
                    
            if com == "bulktext":
                
                self.addHeader(arg)
                self.addBulkText(val)
                
            if com == "dated":
                
                self.addHeader(arg)
                
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
        
    def enableDebug(self):
        
        self.b = 1
        
        #draw width margins
        self.cv.line(self.inset,0,self.inset,self.h)
        self.cv.line(self.w - self.inset,0,self.w - self.inset,self.h)
                
        
    def sizing(self):
        
        self.w = self.cv.w
        self.h = self.cv.h
        self.size = [self.w,self.h]
        
    def addFonts(self):
        
        for fontName in fonts:
            name = fontName.split(".")[0]
            ttype = fontName.split(".")[1]
            
            if ttype in ["ttf"]:
                path = str(pathlib.Path().absolute()) + "\\font\\" + fontName
                
                self.cv.add_font(family=name,fname=path, uni= True)
        
        
    def footer(self):
        print("drawing footer "+"#"*24)
        # Go to 1.5 cm from bottom
        self.cv.set_y(-15)
        
        self.cv.set_font('Roboto-Thin', size = 8)
        # Print centered page number
        # self.cv.cell(0, 10, 'Page %s' % self.cv.page_no(), 0, 0, 'C')
        
        self.cv.rect(10,10,100,100)
            
        
    def detailColumn(self,fraction = 0.33):
        
        x2 = round(self.w * fraction)
        y2 = self.h
        
        self.cv.set_fill_color(*self.colours["accent"])
        
        self.cv.rect(0,0,x2,y2,"F")
        
    def textCell(self,x,y,text,font,size="text",colour="main",align = 'L',link=None):
        
        print("creating text cell ({}...) at {}, {}".format(text[:5],round(x,2),round(y,2)))
        
        ptmm = 0.352778
        
        fontsize = self.fontsizes[size]
        fontcol = self.colours[colour]
        
        inset = self.inset
        margin = self.margin
        vmargin = self.vmargin
        
        self.cv.set_font(font,size=fontsize)
        
        twidth = self.cv.get_string_width(text)
        
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
        
        self.cv.set_xy(x,y)
        self.cv.set_text_color(*fontcol)
        self.cv.cell(w=twidth, h=(vmargin/2)+fontsize*ptmm, align=align, txt=text, border=self.b, link = link)
    
        self.placement = {"x":x,"y":y + vmargin+fontsize*ptmm}
        
    
    def addHeader(self,heading):
        
        y = self.placement["y"] + 6
        
        ptmm = 0.352778
        
        fontsize = self.fontsizes["heading"]
        fontcol = self.colours["main"]
        
        inset = self.inset
        margin = self.margin
        vmargin = self.vmargin
        
        self.cv.set_font("Roboto-Bold",size=fontsize)
        twidth = self.cv.get_string_width(heading)
        self.cv.set_xy(inset,y)
        self.cv.set_text_color(*fontcol)
        self.cv.cell(w=twidth+margin, h=(vmargin)+fontsize*ptmm,txt=heading,border=self.b)
        
        #x at edge margin
        x = inset+twidth + margin
        y =  y-(margin/4)+fontsize*ptmm
        
        self.cv.set_draw_color(*self.colours["main"])
        self.cv.line(x,y ,self.w-inset,y)
        
        self.placement["y"] = y
        
    def addName(self, name, bold = "last"):
        
        font_bold = "Roboto-Bold"
        font_norm = "Roboto-Thin"
        
        name = name.split(" ")
        
        #get name cell sizes
        sizes = [0]
        for i in range(len(name)):
            if (i == len(name) -1) and (bold == "last"):
                self.cv.set_font(font_norm,size = self.fontsizes["name"])
            else:
                self.cv.set_font(font_bold,size = self.fontsizes["name"])
            
            temp = name[i]
            sizes.append(self.cv.get_string_width(temp))
        
        
        midx = self.w/2
        for i in range(len(name)):
            temp = name[i]
            x = midx - sum(sizes)/2 + sum(sizes[:i+1])
            
            x+= i*2 #extra spacing
            
            if (i == len(name) -1) and (bold == "last"):
                self.textCell(x, 6, temp, "Roboto-Bold", size = "name", align = "R")
            else:
                self.textCell(x, 6, temp, "Roboto-Thin", size = "name", align = "R")
    
    def addContacts(self,mob,email,git=None):
        data = {}
        fields = ["mobile","email","git"]
        
        i=0
        for item in mob, email, git:
            data[fields[i]] = item
            
            i+=1
        
        font = "Roboto-Regular"
        
        self.cv.set_font(font,size = self.fontsizes["contact"])
        self.cv.set_text_color(*self.colours["main"])
        sizes = [0]
        
        i = 0
        for item in data.keys():
            if i != 0:
                text = " | "
            else:
                text = ""
                
            text += item +": " + data[item]
            
            sizes.append(self.cv.get_string_width(text))
            
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
        
        
    def addBulkText(self,text,font = "Roboto-Thin", extramargin = 3):
        
        text = text.replace("\n", " ")
        
        x = self.inset
        y = self.placement["y"] + extramargin
        
        self.cv.set_xy(x,y)
        self.cv.set_font(font)
        self.cv.set_font_size(self.fontsizes["text"])
        h = self.fontsizes["text"]/2
        w = self.w - self.inset*2
        
        self.cv.multi_cell(w,h,text,border=self.b)
        
        self.placement["y"] = self.cv.get_y()
        
    def addList(self,listvals,font = "Roboto-Thin"):
        
        x = self.inset + 4
        
        
        for item in listvals:
            y = self.placement["y"]
            
            item = "• " + item
            
            self.textCell(x, y, item, font)
        
        
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
                
            if com == "list":
                
                print("create list:")
                print("\t",arg,val)
                
                self.addList(val)
        
    def save(self):
        self.cv.output("testcv.pdf")
    
    
    
if __name__ == "__main__":
    
    cv = CV()    
    cv.save()
    
    content = parseText()