"""
Matches pulsar candidates against known sources from the ANTF pulsar catalog.
Will match against other sources added to a a catalog file that have the same format.
The PulsarSiteScraper.py script for instance extracts the details of new pulsars from
specific web pages, and outputs their details in a parsable format (when appended to
the catalog file passed to this script.

Designed to run on python 2.4 or later. 

Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""

# Command Line processing Imports:
from optparse import OptionParser
import os, sys, shutil
from os import listdir
from os.path import isfile, join

# Custom file Imports:
import Utilities

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class Filter:
    """                
    Begins the process of matching by processing command line options
    and executing the correct commands.
    
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
        print "|    Candidate Filter      |"
        print "|                          |"
        print "|--------------------------|"
        print "| Version 1.0              |"
        print "| robert.lyon@cs.man.ac.uk |"
        print "***************************\n"
            
        # Python 2.4 argument processing.
        parser = OptionParser()

        # REQUIRED ARGUMENTS
        # None.
        
        # OPTIONAL ARGUMENTS
        parser.add_option("-p", action="store", dest="path",help='Path to the csv output of the Matcher.py script.',default="")
        parser.add_option("-v", action="store_true", dest="verbose",    help='Verbose debugging flag (optional).'   ,default=False)
        parser.add_option('-o', action="store", dest="outputDir",type="string",help='The directory to store copy non-matched candidates to.',default="")
        parser.add_option('-i', action="store", dest="inputDir",type="string",help='The directory to filter.',default="")
        
        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.
        
        # Update variables with command line parameters.
        self.path           = args.path
        self.debug          = args.verbose
        self.outputDir      = args.outputDir
        self.inputDir       = args.inputDir
        
        # Helpers.
        utils = Utilities.Utilities(self.debug)
                    
        # ******************************
        #
        # Process matches made earlier
        #
        # ******************************
            
        # Check input file exists.
        if(utils.fileExists(self.path)):
            
            utils.o("Match file exists")
            
            if not os.path.exists(self.outputDir):
              
                utils.o("Creating directory at: "+str(self.outputDir))
                
                os.makedirs(self.outputDir)
            
            else:
                utils.o("Directory exists at: "+str(self.outputDir))
            
            # If directory still does not exist, for whatever reason...    
            if not os.path.exists(self.outputDir):
                utils.o("Could not create directory at: "+str(self.outputDir))
                sys.exit()
            else:
                # Check input directory containing candidates exists.
                if not os.path.exists(self.inputDir):
                    utils.o("Input directory doesn't exist: "+str(self.inputDir))
                    sys.exit()
                else:
                    # Ok inputs have been checked, proceed...
                    
                    pathsToAvoid = self.read(self.path)
                    
                    #print "Candidates to not copy to destination directory:\n" , pathsToAvoid
                    
                    candidateFiles = [ f for f in listdir(self.inputDir) if isfile(join(self.inputDir,f)) ]
                    
                    #print "Paths to avoid:"
                    #print pathsToAvoid
                    #print "Candidates in input directory: ", self.inputDir
                    #print candidateFiles
                    
                    refusals = 0
                    allows   = 0
                    
                    for c in candidateFiles:
                        
                        if(c.endswith(".phcx.gz") or c.endswith(".phcx.gz.png")):
                            
                            fullpath       = self.inputDir  + "/" + c
                            fullOutputPath = self.outputDir + "/" + c
                            
                            #print "Checking file:" , fullpath
                            
                            if(fullpath.replace(".png","") in pathsToAvoid):
                                
                                refusals+=1
                                continue
                            
                            else:
                                
                                #print "Allow: ", fullpath
                                shutil.copyfile(fullpath, fullOutputPath)
                                allows+=1
                    
                    print "Refusals :" ,refusals
                    print "Allows   :" ,allows
        else:
            print "Match file does not exist, exiting."
        
        print "Done."
    
    # ****************************************************************************************************
        
    def read(self,path):
        """
        Reads in settings from a file. The settings are then stored in this object.
        """
        
        candidates = []
        
        f = open(path)
        lines = f.readlines()
        f.close()
        
        if(len(lines)>0):
            for line in lines:
                
                components = line.split(",")
                cand = components[0]
                candidates.append(cand)
                
        return candidates                
                
    # **************************************************************************************************** 
      
if __name__ == '__main__':
    Filter().main()