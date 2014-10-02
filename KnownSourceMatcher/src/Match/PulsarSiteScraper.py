"""
Extracts pulsar information from web pages. Still requires some manual work, since the pages being
parsed are often not correctly formatted!!! So always check the file output by this script,
particularly with respect to those sources loaded from HTRU South web source (HTML not regular).

Designed to run on python 2.4 or later. 

Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""

# Command Line processing Imports:
from optparse import OptionParser
import datetime, sys, urllib2
from bs4 import BeautifulSoup
import re, os

# Custom file Imports:
import Utilities

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class PulsarSiteScraper:
    """                
    Attempts to extract the details of known pulsar sources from specific web pages.
    
    """
    
    # ******************************
    #
    # MAIN METHOD AND ENTRY POINT.
    #
    # ******************************

    def main(self,argv=None):
        """
        Main entry point for the Application.
    
        """
        
        print "\n****************************"
        print "|                          |"
        print "|   Pulsar Site Scraper    |"
        print "|                          |"
        print "|--------------------------|"
        print "| Version 1.0              |"
        print "| robert.lyon@cs.man.ac.uk |"
        print "***************************\n"
        
        # Known sites:
        self.lotaas     = "http://www.astron.nl/lotaas/"
        self.gbt_drift  = "http://astro.phys.wvu.edu/GBTdrift350/"
        self.palfa      = "http://www.naic.edu/~palfa/newpulsars/"
        self.ao_drift   = "http://www.naic.edu/~deneva/drift-search/"
        self.htru_south = "https://sites.google.com/site/htrusouthdeep/home"
        self.superb     = "https://sites.google.com/site/publicsuperb/discoveries"
        
        # Update variables with command line parameters.
        self.dataSources    = [self.lotaas,self.gbt_drift,self.palfa,self.ao_drift,self.htru_south,self.superb]
        #self.dataSources    = [self.superb]
        self.debug          = True
        self.outputPath     = "WebSourceParsedOutput1.txt"
        
        # Parsing variables.
        self.ignore = True
        self.cand = 3000
        self.non_decimal = re.compile(r'[^\d.]+')
        
        # Helpers.
        self.utils = Utilities.Utilities(self.debug)
        os.remove(self.outputPath)
                 
        # ******************************
        #
        # Perform parsing....
        #
        # ******************************
        
        for source in self.dataSources:
            self.processSource(source)
        
        # Finally clean the file
        self.clean(self.outputPath)
            
        print "Done."
    
    # ****************************************************************************************************
    
    def output(self,data):
        """
        Writes a string of data to the output file.
        """
        self.utils.appendToFile(self.outputPath,str(data+"\n"))
    
    # ****************************************************************************************************
    
    def clean(self,path):
        """
        Cleans the output produced by this script, removing any lines
        containing improper values.
        """
        
        f = open(path)
        lines = f.readlines()
        f.close()
        # delete original which may contain errors
        os.remove(path)
        
        good=0
        bad=0
        
        if(len(lines)>0):
            for line in lines:
                filterText = self.filterText(line).replace("\n","")
                components = filterText.split()
                
                if(len(components)!=12 or components==None or len(components)==0):
                    continue
                
                # Component 1 is the pulsar name
                # Component 2 is the pulsar RA
                # Component 4 is the pulsar DEC
                # Component 6 is the pulsar Period
                # Component 8 is the pulsar F0
                # Component 10 is the pulsar DM
                
                valid = True
                
                if(components[1].startswith("J") == False):
                    valid = False
                elif(len(components[1])< 8 or len(components[1])>10):
                    valid = False
                
                if((components[2].count(":")!=2) and (len(components[2])>7 and len(components[2]) < 13)):
                    valid = False
                
                if((components[4].count(":")!=2) and (len(components[4])>8 and len(components[2]) < 14)):
                    valid = False
                
                try:
                    tmp = float(components[6])
                except ValueError:
                        valid = False
        
                try:
                    tmp = float(components[10])
                except ValueError:
                        valid = False
                
                if(valid):
                    good+=1
                    self.output(filterText)
                else:
                    bad+=1
                    
        print "Good: ",good
        print "Bad : ",bad
    
    # ****************************************************************************************************
                
    def filterText(self,text):
        """
        Basic text filtering to remove any orphaned HTML tags.
        """
        
        t_1 = text.decode('ascii',errors='ignore')
        t_2 = t_1.replace("<font size=\"2\">","")
        t_3 = t_2.replace("</font>","")
        t_4 = t_3.replace("<br>","")
        t_5 = t_4.replace("<br/>","")
        t_6 = t_5.replace("<strike>","")
        t_7 = t_6.replace("</strike>","")
        t_8 = t_7.replace("<span>","")
        t_9 = t_8.replace("</span>","")
        t_10 = t_9.replace("<i>","")
        t_11 = t_10.replace("</i>","")
        t_12 = t_11.replace("<br/>","")
        
        return t_12
        
    # ****************************************************************************************************
        
    def processSource(self,source):
        """
        Process each source, taken the required action.
        """
        if(source==self.lotaas):
            self.processLotaas()
        elif(source==self.gbt_drift):
            self.processGBTDrift()
        elif(source==self.palfa):
            self.processPalfa()
        elif(source==self.ao_drift):
            self.processAODrift()
        elif(source==self.htru_south):
            self.processHTRUSouth()
        elif(source==self.superb):
            self.processSuperb()
    
    # **************************************************************************************************** 
    
    def processSuperb(self):
        """
        Process the HTML of the SUPERB survey web page.
        """
        # Read in URL and parse.
        response = urllib2.urlopen(self.superb)
        page_source = response.read()
        source = self.filterText(page_source)
        soup = BeautifulSoup(source)
        
        nameIndex   = 0
        periodIndex = -1
        dmIndex     = -1
        raIndex     = -1
        decIndex    = -1
        
        tables = soup.findAll('table')
        rows = tables[2].findAll('tr')
        
        # First pre-process to find the columns containing useful information.
        for tr in rows:
            cols = tr.findAll('td')
            
            index = 0
            for td in cols:
                    
                if("Period (ms)" in td):
                    periodIndex=index
                    
                if("DM (cm^-3*pc)" in td):
                    dmIndex=index
                
                if("RA (J2000)" in td ):
                    raIndex=index
                
                if("Dec (J2000)" in td):
                    decIndex=index
                    
                index+=1
        
        # Debug statements to show potentially useful information found.    
        print "Name Index:   ", nameIndex
        print "Period Index: ", periodIndex
        print "DM Index :    ", dmIndex
        print "RA Index :    ", raIndex
        print "DEC Index :    ", decIndex
        
        # Now process again but this time extract useful information.
        
        for tr in rows:
            
            src = PulsarSiteScraper.Source()
            cols = tr.findAll('td')
            index = 0
            
            for td in cols:
                
                try:
                    tmp = td.contents[0]
                except Exception:
                    continue
                    
                
                if(index == nameIndex):
                    #print "Name: ",td
                    try:                        
                        sp = BeautifulSoup(str(tmp))

                        if ("<a" in str(tmp)):
                            
                            for a in sp.findAll('a'):
                                b=str(a.contents[0])
                                src.setName(self.filterText(b))  
                        else:
                            src.setName(self.filterText(str(tmp)))
                             
                    except TypeError:
                        print ""
                                          
                elif(index == periodIndex):
                    #print "Period: ", td.contents[0]
                    tmp=self.non_decimal.sub('', str(tmp))
                    src.setPeriod(self.filterText(str(tmp)))
                    
                elif(index == dmIndex):
                    #print "DM: ", td.contents[0]
                    tmp=self.non_decimal.sub('', str(tmp))
                    src.setDM(self.filterText(str(tmp)))
                    
                elif(index == raIndex):
                    #print "RA: ", td.contents[0]
                    src.setRA(self.filterText(str(tmp)))
                    
                elif(index == decIndex):
                    #print "DEC: ", td.contents[0]
                    src.setDEC(self.filterText(str(tmp)))
                    
                index+=1

            if(src.isValid()):
                print "Source valid:",src.toString(self.cand)
                self.output(src.toString(self.cand))
            else:
                print "Source invalid",src.toString(self.cand)
                
            self.cand+=1
        
    def processLotaas(self):
        """
        Process the HTML of the LOTAAS survey web page.
        """
        print "Processing Lotaas data at: ", self.lotaas
        
        # Read in URL and parse.
        response = urllib2.urlopen(self.lotaas)
        page_source = response.read()
        source = self.filterText(page_source)
        soup = BeautifulSoup(source)
        
        nameIndex   = -1
        periodIndex = -1
        dmIndex     = -1
        
        table = soup.find('table')
        rows = table.findAll('tr')
        
        # First pre-process to find the columns containing useful information.
        for tr in rows:
            cols = tr.findAll('td')
            
            index = 0
            for td in cols:
                
                if("Pulsar" in td):
                    nameIndex=index
                    
                if("P (ms)" in td or "P(ms)" in td):
                    periodIndex=index
                    
                if("DM (pc/cc)" in td or "DM" in td):
                    dmIndex=index
                    
                index+=1
        
        # Debug statements to show potentially useful information found.    
        #print "Name Index:   ", nameIndex
        #print "Period Index: ", periodIndex
        #print "DM Index :    ", dmIndex
        
        # Now process again but this time extract useful information.
        
        for tr in rows:
            
            src = PulsarSiteScraper.Source()
            cols = tr.findAll('td')
            index = 0
            
            for td in cols:
                
                if(index == nameIndex):
                    #print "Name: ",td
                    try:                        
                        sp = BeautifulSoup(str(td.contents[0]))
                        for a in sp.findAll('a'):
                            src.setName(a.contents[0])   
                    except TypeError:
                        print ""
                                          
                elif(index == periodIndex):
                    #print "Period: ", td.contents[0]
                    src.setPeriod(td.contents[0])
                    
                elif(index == dmIndex):
                    #print "DM: ", td.contents[0]
                    src.setDM(td.contents[0])
                    
                index+=1

            if(src.isValid()):
                print "Source valid:",src.toString(self.cand)
                self.output(src.toString(self.cand))
            else:
                print "Source invalid",src.toString(self.cand)
                
            self.cand+=1
              
    # **************************************************************************************************** 
    
    def processGBTDrift(self):
        """
        Process the HTML of the GBT Drift survey web page.
        """
        print "Processing GBT Drift data at: ", self.gbt_drift
        
        # Read in URL and parse.
        response = urllib2.urlopen(self.gbt_drift)
        page_source = response.read()
        source = self.filterText(page_source)
        soup = BeautifulSoup(source)
        
        nameIndex   = 0
        periodIndex = 1
        dmIndex     = 2
        
        table = soup.find('table')
        rows = table.findAll('tr')
        
        # First pre-process to find the columns containing useful information.
        for tr in rows:
            cols = tr.findAll('td')

            index = 0
            for td in cols:

                if("Pulsar" in td):
                    nameIndex=index
                    
                if("P (ms)" in td or "P(ms)" in td):
                    periodIndex=index
                    
                if("DM (pc/cc)" in td or "DM" in td):
                    dmIndex=index
                    
                index+=1
        
        # Debug statements to show potentially useful information found.    
        print "Name Index:   ", nameIndex
        print "Period Index: ", periodIndex
        print "DM Index :    ", dmIndex
        
        # Now process again but this time extract useful information.
        
        for tr in rows:
            
            src = PulsarSiteScraper.Source()
            cols = tr.findAll('td')
            index = 0
            
            for td in cols:
                
                if(index == nameIndex):
                    #print "Name: ",td
                    try:                        
                        sp = BeautifulSoup(str(td.contents[0]))
                        for a in sp.findAll('a'):
                            src.setName(a.contents[0])   
                    except TypeError:
                        print ""
                                          
                elif(index == periodIndex):
                    #print "Period: ", td.contents[0]
                    src.setPeriod(td.contents[0])
                    
                elif(index == dmIndex):
                    #print "DM: ", td.contents[0]
                    src.setDM(td.contents[0])
                    
                index+=1

            if(src.isValid()):
                print "Source valid:",src.toString(self.cand)
                self.output(src.toString(self.cand))
            else:
                print "Source invalid",src.toString(self.cand)
                
            self.cand+=1
        
    # **************************************************************************************************** 
    
    def processPalfa(self):
        """
        Process the HTML of the P-ALFA survey web page.
        """
        print "Processing Palfa data at: ", self.palfa
        
        # Read in URL and parse.
        response = urllib2.urlopen(self.palfa)
        page_source = response.read()
        source = self.filterText(page_source)
        soup = BeautifulSoup(source)
        
        nameIndex   = -1
        periodIndex = -1
        dmIndex     = -1
        
        table = soup.find('table')
        rows = table.findAll('tr')
        
        # First pre-process to find the columns containing useful information.
        for tr in rows:
            cols = tr.findAll('td')
            
            index = 0
            for td in cols:
                
                if("Pulsar" in td):
                    nameIndex=index
                    
                if("P (ms)" in td or "P(ms)" in td or "Period(ms)" in td):
                    periodIndex=index
                    
                if("DM (pc/cc)" in td or "DM" in td or "DM(pc/cc)" in td):
                    dmIndex=index
                    
                index+=1
        
        # Debug statements to show potentially useful information found.    
        #print "Name Index:   ", nameIndex
        #print "Period Index: ", periodIndex
        #print "DM Index :    ", dmIndex
        
        # Now process again but this time extract useful information.
        
        for tr in rows:
            
            src = PulsarSiteScraper.Source()
            cols = tr.findAll('td')
            index = 0
            
            for td in cols:
                
                if(index == nameIndex):
                    #print "Name: ",td
                    try:                        
                        sp = BeautifulSoup(str(td.contents[0]))

                        if ("<a" in str(td.contents[0])):
                            
                            for a in sp.findAll('a'):
                                src.setName(a.contents[0])  
                        else:
                            src.setName(td.contents[0])
                             
                    except TypeError:
                        print ""
                                          
                elif(index == periodIndex):
                    #print "Period: ", td.contents[0]
                    tmp = td.contents[0].encode('ascii',errors='ignore')
                    tmp =self.non_decimal.sub('', tmp)
                    src.setPeriod(tmp)
                    
                elif(index == dmIndex):
                    #print "DM: ", td.contents[0]
                    src.setDM(td.contents[0])
                    
                index+=1

            if(src.isValid()):
                print "Source valid:",src.toString(self.cand)
                self.output(src.toString(self.cand))
            else:
                print "Source invalid",src.toString(self.cand)
                
            self.cand+=1
        
    # **************************************************************************************************** 
    
    def processAODrift(self):
        """
        Process the HTML of the AO Drift survey web page.
        """
        print "Processing AO Drift data at: ", self.ao_drift
        
        # Read in URL and parse.
        response = urllib2.urlopen(self.ao_drift)
        page_source = response.read()
        source = self.filterText(page_source)
        soup = BeautifulSoup(source)
        
        nameIndex   = -1
        periodIndex = -1
        dmIndex     = -1
        
        table = soup.find('table')
        rows = table.findAll('tr')
        
        # First pre-process to find the columns containing useful information.
        for tr in rows:
            cols = tr.findAll('td')
            
            index = 0
            for td in cols:
                
                if("Pulsar" in td):
                    nameIndex=index
                    
                if("P (ms)" in td or "P(ms)" in td or "Period(ms)" in td):
                    periodIndex=index
                    
                if("DM (pc/cc)" in td or "DM" in td or "DM(pc/cc)" in td):
                    dmIndex=index
                    
                index+=1
        
        # Debug statements to show potentially useful information found.    
        #print "Name Index:   ", nameIndex
        #print "Period Index: ", periodIndex
        #print "DM Index :    ", dmIndex
        
        # Now process again but this time extract useful information.
        
        for tr in rows:
            
            src = PulsarSiteScraper.Source()
            cols = tr.findAll('td')
            index = 0
            
            for td in cols:
                
                if(index == nameIndex):
                    #print "Name: ",td
                    try:                        
                        sp = BeautifulSoup(str(td.contents[0]))

                        if ("<a" in str(td.contents[0])):
                            
                            for a in sp.findAll('a'):
                                src.setName(a.contents[0])  
                        else:
                            src.setName(td.contents[0])
                             
                    except TypeError:
                        print ""
                                          
                elif(index == periodIndex):
                    #print "Period: ", td.contents[0]
                    tmp = td.contents[0].encode('ascii',errors='ignore')
                    tmp=self.non_decimal.sub('', tmp)
                    src.setPeriod(tmp)
                    
                elif(index == dmIndex):
                    #print "DM: ", td.contents[0]
                    src.setDM(td.contents[0])
                    
                index+=1

            if(src.isValid()):
                print "Source valid:",src.toString(self.cand)
                self.output(src.toString(self.cand))
            else:
                print "Source invalid",src.toString(self.cand)
                
            self.cand+=1
        
    # **************************************************************************************************** 
    
    def processHTRUSouth(self):
        """
        Process the HTML of the HTRU South survey web page.
        """
        print "Processing HTRU South data at: ", self.htru_south
        
        # Read in URL and parse.
        response = urllib2.urlopen(self.htru_south)
        page_source = response.read()
        source = self.filterText(page_source)
        soup = BeautifulSoup(source)
        
        nameIndex   = 1
        periodIndex = 8
        dmIndex     = 9
        raIndex     = 6
        decIndex    = 7
        
        # Debug statements to show potentially useful information found.    
        #print "Name Index:   ", nameIndex
        #print "Period Index: ", periodIndex
        #print "DM Index :    ", dmIndex
        #print "RA Index :    ", raIndex
        #print "DEC Index :    ", decIndex
        
        tables = soup.findAll('table')
        rows = tables[4].findAll('tr')
        
        # Now process again but this time extract useful information.
        
        for tr in rows:
            
            src = PulsarSiteScraper.Source()
            cols = tr.findAll('td')
            index = 0
            
            for td in cols:
                
                try:
                    tmp = td.contents[0]
                except Exception:
                    continue
                    
                
                if(index == nameIndex):
                    #print "Name: ",td
                    try:                        
                        sp = BeautifulSoup(str(tmp))

                        if ("<a" in str(tmp)):
                            
                            for a in sp.findAll('a'):
                                b=str(a.contents[0])
                                src.setName(self.filterText(b))  
                        else:
                            src.setName(self.filterText(str(tmp)))
                             
                    except TypeError:
                        print ""
                                          
                elif(index == periodIndex):
                    #print "Period: ", td.contents[0]
                    tmp=self.non_decimal.sub('', str(tmp))
                    src.setPeriod(self.filterText(str(tmp)))
                    
                elif(index == dmIndex):
                    #print "DM: ", td.contents[0]
                    tmp=self.non_decimal.sub('', str(tmp))
                    src.setDM(self.filterText(str(tmp)))
                    
                elif(index == raIndex):
                    #print "RA: ", td.contents[0]
                    src.setRA(self.filterText(str(tmp)))
                    
                elif(index == decIndex):
                    #print "DEC: ", td.contents[0]
                    src.setDEC(self.filterText(str(tmp)))
                    
                index+=1

            if(src.isValid()):
                print "Source valid:",src.toString(self.cand)
                self.output(src.toString(self.cand))
            else:
                print "Source invalid",src.toString(self.cand)
                
            self.cand+=1
        
    # ****************************************************************************************************
    
    class Source(object):
        """
        Represent a single source object extracted from a web resource.
        """
        
        # ******************************
        #
        # INIT FUNCTION
        #
        # ******************************
        
        def __init__(self):
            """
            Initialises the class.
        
            """
            self.name   = None
            self.period = None 
            self.dm     = None
            self.RA     = None
            self.DEC    = None
        
        # ************************************************************************************************
        
        def setName(self,nme):
            """
            Sets the name of the source.
            """
            self.name = str(nme).strip()
        
        # ************************************************************************************************
            
        def setDM(self,d):
            """
            Sets the DM value of the source.
            """
            self.dm = d   
        
        # ************************************************************************************************
        
        def setPeriod(self,p):
            """
            Sets the period of the source.
            """
            self.period = p    
        
        # ************************************************************************************************
        
        def setRA(self,r):
            """
            Sets the RA of the source.
            """
            self.RA = r  
        
        # ************************************************************************************************
        
        def setDEC(self,d):
            """
            Sets the DEC of the source.
            """
            self.DEC = d    
        
        # ************************************************************************************************
                  
        def isValid(self):
            """
            Checks if a source is valid, i.e. is the RA and DEC correctly formed?
            """
            #print "Checking validity..."
            # If the three main variables required are null
            if( self.name is not None and self.dm is not None and self.period is not None):
                
                if(self.name.startswith("J")==False):
                    return False
                    
                #print "Name, DM and Period are NOT null"
                # Try and calculate RA and DEC from pulsar name.
                self.extractRAAndDECFromName()

                # If the candidate has no RA or DEC data.
                if(self.RA is not None and self.DEC is not None):
                    #print "RA and DEC are NOT null"
                    return True
                else:
                    #print "RA and DEC are null"
                    return False
            else:
                return False
        
        # ************************************************************************************************
        
        def extractRAAndDECFromName(self):
            """
            Attempts to extract RA and DEC values from a pulsar name, i.e.
            given J0024-7204, extract 00:24:00 and -72:04:00. This method is useful
            for obtaining a reasonable RA and DEC value for those web sources that
            don't have RA and DEC values listed explicitly.
            """                
            #print "Name: ",self.name
            if("+" in self.name):
                #print "Dealing with +"
                # Count characters from J to +
                j_to_plus_count = self.name.find("+")-self.name.find("J")-1
                # Count characters from + to end
                plus_to_end_count = len(self.name)-self.name.find("+")-1
                
                #print "J to + count: ", j_to_plus_count
                #print "+ to end count: ",plus_to_end_count
                
                if(j_to_plus_count==4 and plus_to_end_count==2):
                    
                    RA_1 = self.name[1:3]
                    RA_2 = self.name[3:5]
                    DEC_1= self.name[6:]
                    
                    if(self.RA is None):
                        self.RA = RA_1 + ":" + RA_2 + ":00"
                    
                    if(self.DEC is None):
                        self.DEC = "+" + DEC_1 + ":00:00"
                    
                    #print "RA: ", self.RA
                    #print "DEC: ", self.DEC
                    
                elif(j_to_plus_count==4 and plus_to_end_count==4):
                    
                    RA_1 = self.name[1:3]
                    RA_2 = self.name[3:5]
                    DEC_1= self.name[6:8]
                    DEC_2= self.name[8:10]
                    
                    if(self.RA is None):
                        self.RA = RA_1 + ":" + RA_2 + ":00"
                    if(self.DEC is None):
                        self.DEC = "+" + DEC_1 + ":" + DEC_2 + ":00"
                    
                    #print "RA: ", self.RA
                    #print "DEC: ", self.DEC
                else:
                    print "Unknown format"
                    
            elif("-" in self.name):
                
                #print "Dealing with -"
                # Count characters from J to +
                j_to_minus_count = self.name.find("-")-self.name.find("J")-1
                # Count characters from + to end
                minus_to_end_count = len(self.name)-self.name.find("-")-1
                
                #print "J to + count: ", j_to_plus_count
                #print "+ to end count: ",plus_to_end_count
                
                if(j_to_minus_count==4 and minus_to_end_count==2):
                    
                    RA_1 = self.name[1:3]
                    RA_2 = self.name[3:5]
                    DEC_1= self.name[6:]
                    
                    if(self.RA is None):
                        self.RA = RA_1 + ":" + RA_2 + ":00"
                    if(self.DEC is None):
                        self.DEC = "-" + DEC_1 + ":00:00"
                    
                    #print "RA: ", self.RA
                    #print "DEC: ", self.DEC
                    
                elif(j_to_minus_count==4 and minus_to_end_count==4):
                    
                    RA_1 = self.name[1:3]
                    RA_2 = self.name[3:5]
                    DEC_1= self.name[6:8]
                    DEC_2= self.name[8:10]
                    
                    if(self.RA is None):
                        self.RA = RA_1 + ":" + RA_2 + ":00"
                    if(self.DEC is None):
                        self.DEC = "-" + DEC_1 + ":" + DEC_2 + ":00"
                    
                    #print "RA: ", self.RA
                    #print "DEC: ", self.DEC
                else:
                    print "Error"
            else:
                "Don't know why I'm here."
            
        # ************************************************************************************************
        
        def toString(self,numb):
            """
            Produces a simple string representation of a source.
            """
            
            # The required output per source found resembles the following:
            #
            # -----------------------------------------------------------------------------------------
            # #     NAME    RAJ               DECJ              P0            F0           DM
            #              (hms)              (dms)             (s)           (Hz)         (cm^-3 pc)
            # -----------------------------------------------------------------------------------------
            # 1     PSR A   00:06:04 2.0e-01  +18:34:59 4.0e+00  1.0 1.4e-10  1.4 3.0e-10  9.0 6.0e-01
            # -----------------------------------------------------------------------------------------
            
            return str(numb) + "\t" +str(self.name) + "\t\t" + str(self.RA) + "\t\t1.0e-01\t\t" + str(self.DEC) + "\t\t1.0e-01\t\t" + str(self.period) + "\t\t1.0e-01\t\t0\t\t1.0e-01\t\t" + str(self.dm) + "\t\t1.0e-01"
                            
        # ************************************************************************************************       
        
    # ****************************************************************************************************
        
if __name__ == '__main__':
    PulsarSiteScraper().main()