"""

Designed to run on python 2.4 or later. 

Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""

import copy, gzip, os, math, string, ordereddict, operator
import KnownSource
import  numpy as np
import PFDFile as pfd
from Utilities import Utilities
from xml.dom import minidom

# For viewing candidates.
from PIL import Image  # @UnresolvedImport - Ignore this comment, simply stops my IDE complaining.
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class Interactive(Utilities):
    """                
    Script used to interactively match against a collection of known sources
    from a pulsar catalog, given user specified period or DM values.
    """
    
    # ******************************
    #
    # INIT FUNCTION
    #
    # ******************************
    def __init__(self,debugFlag, db,output):
        """
        Initialises the class, and passes the pulsar catalog to it.
        
        """
        Utilities.__init__(self,debugFlag)  
        self.db = db
        self.harmonics = [1, 0.5, 0.3, 0.25, 0.2, 0.16, 0.142, 0.125, 0.111, 0.1, 0.0909,0.0833,0.0769,0.0714,0.0666,0.0625,0.03125,0.015625]
        self.width          = 10 # The width of the image viewing panel.
        self.height         = 8  # The height of the image viewing panel.
    
    # ******************************
    #
    # FUNCTIONS.
    #
    # ******************************
    
    def run(self):
        """
        Begins the process of interactively search a pulsar catalog.
        """
        print "Running interactively, press '3' to exit."
        
        self.showMenu()
    
    
    # ****************************************************************************************************
    def showMenu(self):
        """
        Shows the first menu that provides a choice between
        searching a catalog, or exiting the application.
        """
        exit = False
        
        while(exit == False):
            
            print "********************"
            print "1. Search...."
            print "2. Manually match"
            print "3. Exit"
            print "********************\n"
        
            choice = 0
            
            while (choice <= 0 or choice >=4):
                try:
                    choice = int(raw_input("Enter choice (1-3): "))
                except:
                    choice = 0
            if(choice == 1):
                self.processChoice()
            elif(choice == 2):        
                self.manuallyMatch()
            elif(choice == 3):        
                exit = True
    
    # ****************************************************************************************************
        
    def processChoice(self):
        """
        Processes the users choice to search the catalog. Provides the option
        to search by period or DM.
        """
        print "\n\t********************"
        print "\t1. Search by period"
        print "\t2. Search by DM"
        print "\t********************\n"
        
        choice = 0
            
        while (choice <= 0 or choice >=3):
            try:
                choice = int(raw_input("Enter choice (1 or 2): "))
            except:
                choice = 0
                
        if(choice == 1):
            self.searchByPeriod()
        elif(choice == 2):        
            self.searchByDM()
    
    # ****************************************************************************************************
        
    def manuallyMatch(self):
        """
        Enables manual matching.
        """
        print "\n\t*************************"
        print "\tManually match candidates"
        print "\t*************************\n"
        
        directory = ""
            
        while (not os.path.isdir(directory)):
            try:
                directory = str(raw_input("Enter path to directory containing candidates to match (or x to exit): "))
                if(directory=='x'): # User wants to exit.
                    return True
            except:
                directory = ""
        
        outputFile = ""
        
        while (not os.path.exists(outputFile)):
            try:
                outputFile = str(raw_input("Enter a valid file path to write matches to (or x to exit): "))
                
                if(outputFile=='x'): # User wants to exit.
                    return True
                
                open(outputFile, 'a').close()
                
                if(self.fileExists(outputFile)):
                    self.appendToFile(outputFile, "Manual match log,,,,,,,,',\n")
                    self.appendToFile(outputFile, "Candidate,RAJ,DECJ,P0,DM,Known Source,RAJ,DECJ,P0,DM,Harmonic,Angular Separation\n")
                
            except:
                outputFile = ""
        
        maxAngSep = 0
            
        while (maxAngSep <= 0 or maxAngSep >=1000):
            try:
                maxAngSep = float(raw_input("Enter max angular separation you're willing to tolerate between matches: "))
            except:
                maxAngSep = 0
                        
        count = 0
        
        print "\n\tWill now loop over candidates found to be matched. Press x to break loop.\n\n"
        
        # Temporary values
        RAJ  = ""
        DECJ = ""
        P0   = 0
        DM   = 0
        matches = []
        imageShown = False
                  
        # Search the supplied directory recursively.    
        for root, directories, files in os.walk(directory):
            
            for file in files:
                
                # If the file found isn't some form of candidate file, then ignore it.
                if(not file.endswith('.phcx.gz') and not file.endswith('.pfd')):
                    continue
                
                # Else if we reach here we must have a candidate file.
                print "\n\n************************************************************************************************************************\nProcessing file: ", file, "\n"
                
                # If we have a HTRU candidate
                if file.endswith('.phcx.gz'):
                    
                    # Create a KnownSource object from the candidate file.
                    candidate = self.processPHCX(os.path.join(root, file))
                    count += 1
                    
                    RAJ = candidate.getParameterAtIndex("RAJ", 0)
                    DECJ = candidate.getParameterAtIndex("DECJ",0)
                    P0 = float(candidate.getParameterAtIndex("P0",0))
                    DM = candidate.getParameterAtIndex("DM",0)
                    
                    # Output formatting and the details of the candidate found

                    print '{:<55}'.format("Name") + "\t" + '{:<12}'.format("RA") + "\t" + '{:<13}'.format("DEC") + "\t" + '{:<20}'.format("Period") + "\t" + '{:<15}'.format("DM")
                    print '{:<55}'.format(file) + "\t" + '{:<12}'.format(str(RAJ)) + "\t" + '{:<13}'.format(str(DECJ)) + "\t" + '{:<20}'.format(str(P0)) + "\t" + '{:<15}'.format(str(DM))
                    print "\nPossible matches to check\n"
                    
                    # Look for potential matches.
                    matches=self.searchPeriod(P0)
                    
                    pngPath = os.path.join(root, file) + ".png"
                    
                    if(self.fileExists(pngPath)):
                        fig=plt.figure(figsize=(self.width,self.height))# @UnusedVariable
                        plt.ion()
                        candidateImage = mpimg.imread(pngPath)
                        plt.imshow(candidateImage, aspect='auto')
                        plt.show()
                        imageShown = True
                
                # If we have a PFD candidate    
                elif file.endswith('.pfd'):
                    
                    # Create a KnownSource object from the candidate file.
                    candidate = self.processPFD(os.path.join(root, file))
                    count += 1
                    
                    RAJ = candidate.getParameterAtIndex("RAJ", 0)
                    DECJ = candidate.getParameterAtIndex("DECJ",0)
                    P0 = float(candidate.getParameterAtIndex("P0",0))
                    DM = candidate.getParameterAtIndex("DM",0)
                    
                    # Output formatting and the details of the candidate found
                    print '{:<55}'.format("Name") + "\t" + '{:<12}'.format("RA") + "\t" + '{:<13}'.format("DEC") + "\t" + '{:<20}'.format("Period") + "\t" + '{:<15}'.format("DM")
                    print '{:<55}'.format(file) + "\t" + '{:<12}'.format(str(RAJ)) + "\t" + '{:<13}'.format(str(DECJ)) + "\t" + '{:<20}'.format(str(P0)) + "\t" + '{:<15}'.format(str(DM))
                    print "\nPossible matches to check\n"
                    
                    # Look for potential matches.
                    matches=self.searchPeriod(P0)
                
                # If no matches found and we are dealing with a candidate file of some sort...    
                if(len(matches)==0 and (file.endswith('.phcx.gz') or file.endswith('.pfd'))):
                    print "No match"
                    #detail = file + "," + RAJ + "," + DECJ + "," + str(P0) + "," + str(DM) + ",,,,\n"
                    #.appendToFile(outputFile, detail)
                
                # Else there is at least 1 potential match    
                elif(len(matches) > 0 and (file.endswith('.phcx.gz') or file.endswith('.pfd'))):
                    
                    # First print out the potential matches. These need to be ordered according
                    # to angular separation. This is important as there could be many matches, especially
                    # when considering that harmonics could match.
                    
                    # At this point matches contains tuples of known sources along with the potential reason for
                    # a match, e.g. 1st harmonic or 8th harmonic. But these matches are not sorted in any way.
                    
                    print '{:<5}'.format("Match") + "\t" +'{:<10}'.format("Name") + "\t" + '{:<12}'.format("RA") + "\t" + '{:<13}'.format("DEC") + "\t" + '{:<20}'.format("Period") + "\t" + '{:<15}'.format("DM") + "\t" + '{:<15}'.format("Harmonic") + "\t" + '{:<15}'.format("Separation")
                    
                    # Here we filter according the the angular separation specified by the user.
                    separationFilteredMatches={}
                    separationFilteredDetails={}
                    count=0
                    for source, reasonForMatch in matches:
                        angularSeparation = self.findAngularSep(source.getParameterAtIndex("RAJ", 0),source.getParameterAtIndex("DECJ",0), RAJ, DECJ)
                        if(angularSeparation <= maxAngSep ):
                            count+=1
                            harmonic = int(1.0/float(reasonForMatch))
                            source.harmonic = harmonic
                            source.angularSeparation = angularSeparation
                            separationFilteredMatches[source.sourceName]= source
                            separationFilteredDetails[source.sourceName]=source.shortStr() + "\t" + '{:<15}'.format(str(harmonic)) + "\t" + '{:<15}'.format(str(angularSeparation))
                            #print str(count) + "\t" + source.shortStr() + "\t" + '{:<15}'.format(str(reasonForMatch)) + "\t" + '{:<15}'.format(str(angularSeparation))
                    
                    # Add an extra candidate in case the user would like to match to RFI.
                    # This is a quick messy fix to allow you to match an RFI candidate explicitly
                    # to RFI, if any such RFI candidates squeezed through previous filtering steps.
                    rfi = KnownSource.KnownSource("RFI")
                    rfi.angularSeparation = 100000
                    rfi.harmonic = 1
                    rfi.addParameter("PSRJ    RFI    0    0")
                    rfi.addParameter("RAJ    00:00:00    0    0")
                    rfi.addParameter("DECJ   00:00:00    0    0")
                    rfi.addParameter("P0    0    0    0")
                    rfi.addParameter("F0    0    0    0")
                    rfi.addParameter("DM    0    0    0")
                    separationFilteredMatches["RFI"]= rfi
                    separationFilteredDetails["RFI"]= rfi.shortStr() + "\t" + '{:<15}'.format(str("RFI")) + "\t" + '{:<15}'.format(str("NaN"))
                    
                    # Now order according to location in the sky.    
                    orderedSourcesDict = ordereddict.OrderedDict()
                    for s in (sorted(separationFilteredMatches.values(), key=operator.attrgetter('angularSeparation'))):
                        orderedSourcesDict[copy.copy(s.sourceName)] = copy.deepcopy(s)
                    
                    count=0
                    matches=[] # Reset matches....
                    for key in orderedSourcesDict.keys():
                        value =  orderedSourcesDict[key]
                        count+=1
                        matches.append(value) # Re-populate matches.
                        print str(count) + "\t" + separationFilteredDetails[key]                   
            
                    print "Which match to record (0 for none, last in the list for RFI, otherwise choose the appropriate number)."
                    
                    choice = -2
                    while (choice <= -2 or choice >=len(separationFilteredMatches)):
                        try:
                            c = raw_input("Enter choice (or x for exit): ")
                            
                            if(c=='x'): # User wants to exit.
                                return True
                            
                            choice = int(c)-1 # user must have chosen a match
                        except:
                            choice = -6  # Arbitrary value.
                    
                    # If user has chosen a match, then record it.        
                    if(choice >= 0):
                        detail_a = str(os.path.join(root, file)) + "," + RAJ + "," + DECJ + "," + str(P0) + "," + str(DM) + ","
                        detail_b = matches[choice].shortStrCSV() + "," + str(matches[choice].harmonic) + "," + str(matches[choice].angularSeparation) + "\n"
                        detail_c = detail_a+detail_b
                        self.appendToFile(outputFile, detail_c)
                    
                    if(imageShown):
                        plt.clf()
                        plt.close()
                        imageShwon = False
                    
        
        print "Compared ", count , " candidates to ", len(self.db.orderedSourcesDict), " known sources. "
                
    # ****************************************************************************************************
    
    def searchByPeriod(self):
        """
        Searches the loaded catalog by period.
        """   
        
        period = 0.0
        while (period <= 0.0):
            try:
                period = float(raw_input("Enter period(s): "))
            except:
                period =0.0
        
        print "Name          \tRA            \tDEC            \tPeriod(s)\tDM"
                
        for key in self.db.orderedSourcesDict.keys():
            
            try:
                knownSource = self.db.orderedSourcesDict[key]
                cand_period = float(knownSource.getParameterAtIndex("P0",0))
                
                acc = (float(self.db.accuracy)/100)*float(cand_period)
                
                for i in range(0,len(self.harmonics)):
                    # Evaluate the search condition
                    search_cond = float(cand_period) > (float(period) * float(self.harmonics[i])) - float(acc) and\
                    (float(cand_period) < (float(period) * float(self.harmonics[i])) + float(acc))
                    
                    if(search_cond):
                        print knownSource.shortStr() + " Harmonic: " + str(self.harmonics[i])
                    
            except ValueError as ve:
                pass
    
    # ****************************************************************************************************
            
    def searchPeriod(self,period):
        """
        Searches the loaded catalog by period.
        """   
        
              
        #print "Name          \tRA            \tDEC            \tPeriod(s)\tDM"
         
        matches = []
        count = 0         
        for key in self.db.orderedSourcesDict.keys():
            
            try:
                knownSource = self.db.orderedSourcesDict[key]
                cand_period = float(knownSource.getParameterAtIndex("P0",0))
                
                acc = (float(self.db.accuracy)/100)*float(cand_period)
                
                for i in range(0,len(self.harmonics)):
                    # Evaluate the search condition
                    search_cond = float(cand_period) > (float(period) * float(self.harmonics[i])) - float(acc) and\
                    (float(cand_period) < (float(period) * float(self.harmonics[i])) + float(acc))
                    
                    if(search_cond):
                        count+=1
                        #print str(count) + "\t" + knownSource.shortStr() + " Harmonic: " + str(self.harmonics[i])
                        matches.append(tuple([knownSource,str(self.harmonics[i])]))
                    
            except ValueError as ve:
                pass
            
        return matches
        
    # ****************************************************************************************************
    
    def searchByDM(self):
        """
        Searches the loaded catalog by DM.
        """
        dm = 0.0
        while (dm <= 0.0):
            try:
                dm = float(raw_input("Enter DM: "))
            except:
                dm =0.0
        
        print "Name          \tRA            \tDEC            \tPeriod(s)\t\tDM"
                
        for key in self.db.orderedSourcesDict.keys():
            
            try:
                knownSource = self.db.orderedSourcesDict[key]
                cand_dm = float(knownSource.getParameterAtIndex("DM",0))
                
                acc = (float(self.db.accuracy)/100)*float(cand_dm)
                
                # Evaluate the search condition
                search_cond = float(cand_dm) > (float(dm) ) - float(acc) and\
                             (float(cand_dm) < (float(dm) ) + float(acc))
                
                if(search_cond):
                    print knownSource.shortStr()
                    
            except ValueError as ve:
                pass
        
    # ****************************************************************************************************
    
    def processPHCX(self,path):
        """
        Compares a candidate in a ".phcx.gz" file to the known sources in
        the ATNF catalog. Each ".phcx.gz" file is a compressed XML file,
        so here we use XML parsing modules to extract the candidate parameters.
        """
        self.o("Processing PHCX file at: " + path + "\n")
        
        contents = gzip.open(path,'rb')
        xmldata = minidom.parse(contents)
        contents.close()
        
        # Build candidate by extracting data from .phcx file.
        period = float(xmldata.getElementsByTagName('BaryPeriod')[1].childNodes[0].data)
        RAJ = xmldata.getElementsByTagName('RA')[0].childNodes[0].data
        DECJ = xmldata.getElementsByTagName('Dec')[0].childNodes[0].data
        DM = float(xmldata.getElementsByTagName('Dm')[1].childNodes[0].data)
        SNR = float(xmldata.getElementsByTagName('Snr')[1].childNodes[0].data)
        
        # BUILD the candidate. 
        # Here there are two possible cases to watch out for. Either RAJ and DECJ
        # are user specified strings, or they are numerical values extracted from
        # a candidate file. If these are numerical values, then they must be converted
        # in to the correct string format for comparison.
        
        if (not isinstance(RAJ, str)):
            # Convert the RA in degrees into HH:MM:SS
            ra_hrs = float(RAJ) * 24.0 / 360.0
            ra_hr = int( ra_hrs )
            ra_min = int( float( ra_hrs - ra_hr ) * 60.0 )
            ra_sec = int( float( ra_hrs - ra_hr - ra_min / 60 ) * 60.0 )
            
            # Convert the DEC in degrees into HH:MM:SS
            dec_deg = int(float(DECJ))
            dec_abs = np.abs(float(DECJ))
            dec_min = int((float(dec_abs) - np.abs(dec_deg)) * 60.0 )
            dec_sec = int((float(dec_abs) - np.abs(dec_deg) - dec_min / 60.0 ) * 60.0 )
            
            RAJ_str = str(ra_hr) + ":"+str(ra_min)+":"+str(ra_sec)
            DECJ_str = str(dec_deg) + ":" + str(dec_min) + ":" + str(dec_sec)

            #print "RAJ: " + RAJ_str + " DECJ: "+DECJ_str
        
        # DEBUGGING
        self.o( "Candidate -> "+ path + " Period = " + str(period) + " RAJ = " + str(RAJ_str) + " DECJ = " + str(DECJ_str) + " DM = " + str(DM) )
                 
        # Build a KnownSource object from this candidate. We will then find its
        # position in the ordered dictionary, and if no known sources have a sortAttribute
        # within a user specified threshold ( the self.searchPadding variable).
        # Note that not all sources will have a DM value.
        candidateSource = KnownSource.KnownSource()
        candidateSource.addParameter("PSRJ    " + path + "    0")
        
        if (isinstance(RAJ, str)):
            candidateSource.addParameter("RAJ    " + RAJ + "    0")
            candidateSource.addParameter("DECJ    " + DECJ + "    0")
        else:
            candidateSource.addParameter("RAJ    " + RAJ_str + "    0")
            candidateSource.addParameter("DECJ    " + DECJ_str + "    0")
            
        candidateSource.addParameter("DM    " + str(DM) + "    0")
        candidateSource.addParameter("P0    " + str(period) + "    0")
        candidateSource.addParameter("SNR    " + str(SNR) + "    0")
        
        return candidateSource
        
    # ****************************************************************************************************
    
    def processPFD(self,path):
        """
        Compares a candidate in a ".pfd" file to the known sources in
        the ATNF catalog. 
        """
        self.o("Processing PFD file at: " + path + "\n")
        
        cand = pfd.PFD(self.debug,path)
        cand.load()
        
        # Build candidate by extracting data from .phcx file.
        period = float(cand.getPeriod())
        RAJ = cand.getRA()
        DECJ = cand.getDEC()
        DM = cand.getDM()
        SNR = cand.getSNR()
        
        # BUILD the candidate. 
        # Here there are two possible cases to watch out for. Either RAJ and DECJ
        # are user specified strings, or they are numerical values extracted from
        # a candidate file. If these are numerical values, then they must be converted
        # in to the correct string format for comparison.
        
        if (not isinstance(RAJ, str)):
            # Convert the RA in degrees into HH:MM:SS
            ra_hrs = float(RAJ) * 24.0 / 360.0
            ra_hr = int( ra_hrs )
            ra_min = int( float( ra_hrs - ra_hr ) * 60.0 )
            ra_sec = int( float( ra_hrs - ra_hr - ra_min / 60 ) * 60.0 )
            
            # Convert the DEC in degrees into HH:MM:SS
            dec_deg = int(float(DECJ))
            dec_abs = np.abs(float(DECJ))
            dec_min = int((float(dec_abs) - np.abs(dec_deg)) * 60.0 )
            dec_sec = int((float(dec_abs) - np.abs(dec_deg) - dec_min / 60.0 ) * 60.0 )
            
            RAJ_str = str(ra_hr) + ":"+str(ra_min)+":"+str(ra_sec)
            DECJ_str = str(dec_deg) + ":" + str(dec_min) + ":" + str(dec_sec)

            #print "RAJ: " + RAJ_str + " DECJ: "+DECJ_str
        else:
            RAJ_str = RAJ
            DECJ_str = DECJ
        
        # DEBUGGING
        self.o( "Candidate -> "+ path + " Period = " + str(period) + " RAJ = " + str(RAJ_str) + " DECJ = " + str(DECJ_str) + " DM = " + str(DM) )
                 
        # Build a KnownSource object from this candidate. We will then find its
        # position in the ordered dictionary, and if no known sources have a sortAttribute
        # within a user specified threshold ( the self.searchPadding variable).
        # Note that not all sources will have a DM value.
        candidateSource = KnownSource.KnownSource()
        candidateSource.addParameter("PSRJ    " + path + "    0")
        
        if (isinstance(RAJ, str)):
            candidateSource.addParameter("RAJ    " + RAJ + "    0")
            candidateSource.addParameter("DECJ    " + DECJ + "    0")
        else:
            candidateSource.addParameter("RAJ    " + RAJ_str + "    0")
            candidateSource.addParameter("DECJ    " + DECJ_str + "    0")
            
        candidateSource.addParameter("DM    " + str(DM) + "    0")
        candidateSource.addParameter("P0    " + str(period) + "    0")
        candidateSource.addParameter("SNR    " + str(SNR) + "    0")
        
        return candidateSource
    
    # ****************************************************************************************************
    
    def findAngularSep(self, knownSource_RAJ, knownSource_DECJ, candidate_RAJ, candidate_DECJ):
        """
        Calculates the angular separation between a known source and a candidate pulsar.
        The expected input is four strings, such that each string is of the form:
        
        00:00:00
        
        These correspond to the right ascension and declination of each of the sources.
        The value returned is the separation between the two sources theta.
        
        Code originally written by Ben Stappers.
        
        """

        # Split the strings
        list_RAJ_A = string.split(knownSource_RAJ, ":")
        list_DECJ_A = string.split(knownSource_DECJ, ":")
        
        #print "Candidate -> RAJ = ", candidate_RAJ," DECJ = ", candidate_DECJ
        #print "KnownSource -> RAJ = ", knownSource_RAJ," DECJ = ", knownSource_DECJ
        
        pointA_RA_dec = float(str(list_RAJ_A[0])) + float(str(list_RAJ_A[1]))/60.0 + float(str(list_RAJ_A[2]))/3600.0
        pointA_DEC_dec = float(str(list_DECJ_A[0])) + float(str(list_DECJ_A[1]))/60.0 + float(str(list_DECJ_A[2]))/3600.0

        list_RAJ_B = string.split(candidate_RAJ, ":")
        list_DECJ_B = string.split(candidate_DECJ, ":")

        if(len(list_RAJ_B)==3):
            pointB_RA_dec = float(str(list_RAJ_B[0])) + float(str(list_RAJ_B[1]))/60.0 + float(str(list_RAJ_B[2]))/3600.0
        elif(len(list_RAJ_B)==2):
            pointB_RA_dec = float(str(list_RAJ_B[0])) + float(str(list_RAJ_B[1]))/60.0
        if(len(list_DECJ_B)==3):
            pointB_DEC_dec = float(str(list_DECJ_B[0])) + float(str(list_DECJ_B[1]))/60.0 + float(str(list_DECJ_B[2]))/3600.0
        elif(len(list_DECJ_B) == 2):
            pointB_DEC_dec = float(str(list_DECJ_B[0])) + float(str(list_DECJ_B[1]))/60.0
        

        # Convert to Radians
        r1 = (pointA_RA_dec/360) * 2 * math.pi
        d1 = (pointA_DEC_dec/360)* 2 * math.pi

        r2 = (pointB_RA_dec/360) * 2 * math.pi
        d2 = (pointB_DEC_dec/360) * 2 * math.pi

        # Calculate the angular separation theta
        atanpart = math.atan(math.sqrt(  math.cos(d2)*math.cos(d2)*math.pow((math.sin(r2-r1)),2)  + math.pow((math.cos(d1)*math.sin(d2)-math.sin(d1)*math.cos(d2)*math.cos(r2-r1)),2 )) / (math.sin(d1)*math.sin(d2)+math.cos(d1)*math.cos(d2)*math.cos(r2-r1)))
        if(atanpart < 0):
            theta = (atanpart*180/math.pi) + 180
        else:
            theta = atanpart*180/math.pi

        return theta
    
    # ****************************************************************************************************
    