"""
Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""

# Standard library Imports:
import gzip,sys, os

# XML processing Imports:
from xml.dom import minidom
from Utilities import Utilities

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class PhcxExperimenter(Utilities):
    """                
    
    """
    
    # ******************************
    #
    # MAIN METHOD AND ENTRY POINT.
    #
    # ******************************
    def __init__(self,debugFlag,):
        """
        
        """
        Utilities.__init__(self,debugFlag) 
        
    def main(self,argv=None):
        """
        Main entry point for the Application.
    
        """
        
        print "\n****************************"
        print "|                          |"
        print "|--------------------------|"
        print "| Version 1.0              |"
        print "| robert.lyon@cs.man.ac.uk |"
        print "***************************\n"
        
        directory = "/Users/rob/Dropbox/Data/Raw/HTRU/ReprocessedHTRU/ALL_MAYBES/Attempt_3_Filtering/Final"
        dataFile = "/Users/rob/Dropbox/Data/Raw/HTRU/ReprocessedHTRU/ALL_MAYBES/Attempt_3_Filtering/Final/data.csv"
        
        # Search the supplied directory recursively.    
        for root, directories, files in os.walk(directory):
            
            for file in files:
                
                # If the file found isn't some form of candidate file, then ignore it.
                if(not file.endswith('.phcx.gz') and not file.endswith('.pfd')):
                    continue
                
                candidateFile = os.path.join(root, file)
                # Read data directly from phcx file.
                cand = gzip.open(candidateFile,'rb')
                c = minidom.parse(cand) # strip off xml data
                cand.close()
                
                snr = float(c.getElementsByTagName('Snr')[1].childNodes[0].data)
                dm = float(c.getElementsByTagName('Dm')[1].childNodes[0].data)
                period = float(c.getElementsByTagName('BaryPeriod')[1].childNodes[0].data) * 1000
                width = float(c.getElementsByTagName('Width')[1].childNodes[0].data)
                
                self.appendToFile(dataFile, str(dm)+","+str(period)+"\n")
        
        print "Done."
    
    # **************************************************************************************************** 
      
if __name__ == '__main__':
    PhcxExperimenter(True).main()