"""

Designed to run on python 2.4 or later. 

Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""

import gzip, os
import KnownSource
import  numpy as np
import PFDFile as pfd
from Utilities import Utilities
from xml.dom import minidom

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class InputProcessor(Utilities):
    """                
    This script processes user command line input and takes the action specified.
    
    """
    
    # ******************************
    #
    # INIT FUNCTION
    #
    # ******************************
    def __init__(self,debugFlag, db, st,mt):
        """
        Initialises the class, and sets up initial variables.
        
        """
        Utilities.__init__(self,debugFlag)
        self.matcher = mt         
        self.db = db
        self.settings = st
        
        # This call creates the headers for an output CSV file that will
        # be used to store shortened versions of candidate matches found.
        self.createCSVFile(self.matcher.outputPath)
    
    # ******************************
    #
    # PROCESS FUNCTION.
    #
    # ******************************
    
    def process(self):
        """
        Processes the user input, and takes the appropriate action.
        
        """
        self.o("Processing user input...")
        
        if(self.matcher.processFile):
            
            if(self.isAPathFile(self.matcher.path)):
                
                self.o("Found a path file")
                self.processPathFile(self.matcher.path)
                
            elif(self.isAClassifierOutputFile(self.matcher.path)):
                self.o("Found a classifier predictions file")
                self.processPredictionsFile(self.matcher.path)  
                  
            else:
                
                self.o("Found either a PHCX or PFD file")
                
                if(self.matcher.path.endswith(".phcx.gz")):
                    self.processPHCX(self.matcher.path)
                    
                elif(self.matcher.path.endswith(".pfd")):
                    self.processPFD(self.matcher.path)
                              
        elif(self.matcher.processDirectory):
            
            self.o("Found a directory")
            self.processDirecotry(self.matcher.path)
            
        else:
            self.o("Invalid input received")
            
        print "Possible matches found: ", self.db.possibleMatches
        
        
    # ****************************************************************************************************
    
    def processPathFile(self,path):
        """
        Processes a file that contains paths to candidate
        files. 
        
        The structure of the file expected by this function is as follows:
        
        /local/scratch/cands/2008-11/2008-11-18-05:34:16/01/2008-11-18-05:34:16.01.fil_sigproc_001.phcx.gz.png
        /local/scratch/cands/2008-11/2008-11-18-05:34:16/02/2008-11-18-05:34:16.02.fil_sigproc_001.phcx.gz.png
        /local/scratch/cands/2008-11/2008-11-18-05:34:16/03/2008-11-18-05:34:16.03.fil_sigproc_001.phcx.gz.png
        /local/scratch/cands/2008-11/2008-11-18-05:34:16/04/2008-11-18-05:34:16.04.fil_sigproc_001.phcx.gz.png
        .
        .
        .
        <continued>
        """
        self.o("Processing path file at: " + path + "\n")
        
        count = 0
        directoryFile = open(path,'rU') # Read only access
        
        content = directoryFile.readlines()
        for line in content:
            
            tmpLine = line.replace('\n','')
            tmpLine = tmpLine.replace('\r','')
            
            if ( len(tmpLine) > 2):
                
                if(self.fileExists(tmpLine)):

                    if tmpLine.endswith('.phcx.gz'):
                        self.processPHCX(tmpLine)
                        count += 1
                    elif tmpLine.endswith('.pfd'):
                        self.processPFD(tmpLine)
                        count += 1
            else:
                pass
            
        print "Compared ", count , " candidates to ", len(self.db.orderedSourcesDict), " known sources. "
    
    # ****************************************************************************************************
    
    def processPredictionsFile(self,path):
        """
        Processes a file that contains paths to candidate
        files. 
        
        The structure of the file expected by this function is as follows:
        
        Candidate,Profile Mean,Profile STDEV,Profile Skew,Profile Kurt,DM Mean,DM STDEV,DM Skew,DM Kurt
        /Volumes/A/LOFAR/NOISE/L155450_SAP2_BEAM12_DM26.75_Z0_ACCEL_Cand_1.pfd,36.2,31.2,4.3,25.8,1.9,0.9,1.8,2.7
        /Volumes/B/LOFAR/NOISE/L155451_SAP3_BEAM12_DM26.76_Z1_ACCEL_Cand_2.pfd,22.2,11.2,2.1,16.1,3.9,0.3,1.6,2.1
        /Volumes/C/LOFAR/NOISE/L155452_SAP4_BEAM12_DM26.77_Z2_ACCEL_Cand_3.pfd,11.2,23.2,8.9,20.8,2.3,0.7,1.7,2.3
        .
        .
        .
        <continued>
        """
        self.o("Processing path file at: " + path + "\n")
        
        count = 0
        file = open(path,'rU') # Read only access
        content = file.readlines()
        file.close()
        
        for line in content:
            
            tmpLine = line.replace("\n","")
            tmpLine = tmpLine.replace("\r","")
            
            if ( len(tmpLine) > 2):
                
                components = tmpLine.split(",")
                
                if(self.fileExists(components[0])):
                    

                    if components[0].endswith('.phcx.gz'):

                        self.processPHCX(components[0])
                        count += 1
                    elif components[0].endswith('.pfd'):
                        self.processPFD(components[0])
                        count += 1
            else:
                pass
            
        print "Compared ", count , " candidates to ", len(self.db.orderedSourcesDict), " known sources. "
            
    # ****************************************************************************************************
    
    def processDirecotry(self,path):
        """
        Searches a directory for ".phcx.gz" candidate files, and for each file found,
        looks for matches in the ANTF catalog.
        
        """
        self.o("Processing directory at: " + path + "\n")
        
        count = 0
        
        # Search the supplied directory recursively.    
        for root, directories, files in os.walk(path):
            for file in files:
                if file.endswith('.phcx.gz'):
                    self.processPHCX(os.path.join(root, file))
                    count += 1
                elif file.endswith('.pfd'):
                    self.processPFD(os.path.join(root, file))
                    count += 1
        
        print "Compared ", count , " candidates to ", len(self.db.orderedSourcesDict), " known sources. "
        
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
        
        self.db.match(candidateSource,self.matcher.outputPath)  
        
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
        
        self.db.match(candidateSource,self.matcher.outputPath)
        
    # ****************************************************************************************************
    
    def isAPathFile(self,path):
        """
        Checks if a file contains paths to files, one per line.
        
        Parameters:
        path    -    the path to the file check.
        
        Returns:
        True if the file contains only paths, else false.
        """
        f = open(path)
        lines = f.readlines()
        f.close()

        if(len(lines)>0):
            for line in lines:
                
                line=line.replace("\n","")
                line=line.replace("\r","")
                
                if(line is None):
                    return False
                
                try:
                    if(self.fileExists(line)==False):
                        return False
                except Exception as e: # catch *all* exceptions
                    return False
                
        # Only get here IF a file contains ONLY file paths.        
        return True
    
    # ****************************************************************************************************
    
    def isAClassifierOutputFile(self,path):
        """
        Checks if a file contains paths to files, one per line.
        
        Parameters:
        path    -    the path to the file check.
        
        Returns:
        True if the file contains only paths, else false.
        """
        f = open(path)
        lines = f.readlines()
        f.close()
        
        if(len(lines)>0):
            for line in lines:
                
                line=line.replace("\n","")
                line=line.replace("\r","")
                
                if(line is None):
                    return False
                
                if(line.startswith("Candidate,Profile Mean,Profile STDEV,Profile Skew,")):
                    continue;
                
                try:
                    components = line.split(",")
                    if(self.fileExists(components[0])==False):
                        return False
                except Exception as e: # catch *all* exceptions
                    return False
                
        # Only get here IF a file contains ONLY file paths.        
        return True
    
    # ****************************************************************************************************
    
    def createCSVFile(self,path):
        """
        Creates a CSV output file with custom header and structure.
        """
        
        # Now create a separate CSV result file.
        if os.path.isfile(path.replace(".txt",".csv")):
            os.remove(path.replace(".txt",".csv"))
            
        csvFile = open(path.replace(".txt",".csv"), 'w')
        csvFile.write('Candidate,RAJ,DECJ,P0,DM,SNR,Known Source,RAJ,DECJ,P0,DM,Harmonic Number,Harmonic Period,Harmonic Period/Candidate Period,Angular separation(deg)\n')
        csvFile.close() 
        
    # ****************************************************************************************************   
    