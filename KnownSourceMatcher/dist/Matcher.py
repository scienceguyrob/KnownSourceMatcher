"""
Matches pulsar candidates against known sources from the ANTF pulsar catalog.
Will match against other sources added to a a catalog file that have the same format.
The PulsarSiteScraper.py script for instance extracts the details of new pulsars from
specific web pages, and outputs their details in a parseable format (when appended to
the catalog file passed to this script.

Designed to run on python 2.4 or later. 

Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""

# Command Line processing Imports:
from optparse import OptionParser
import datetime, sys

# Custom file Imports:
import Utilities
import Settings
import KnownSourceDB
import InputProcessor
import Interactive
import Validator

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class Matcher:
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
        print "|    Candidate Matcher     |"
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
        parser.add_option("-p", action="store", dest="path",help='Path to the directory/file containing candidates.',default="")
        parser.add_option("-i", action="store_true", dest="interactive",help='Interactive mode flag (optional).'    ,default=False)
        parser.add_option("-v", action="store_true", dest="verbose",    help='Verbose debugging flag (optional).'   ,default=False)
        parser.add_option("--v", action="store_true", dest="validator",    help='Validation flag (optional).'   ,default=False)
        parser.add_option('-o', action="store", dest="outputPath",type="string",help='The path to write matches to (optional).',default="")
        parser.add_option("--psrcat", action="store", dest="psrcat",help='Path to the pulsar catalog data to use (required).',default="")
        
        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.
        
        # Update variables with command line parameters.
        self.path           = args.path
        self.interactive    = args.interactive
        self.debug          = args.verbose
        self.outputPath     = args.outputPath
        self.psrcat         = args.psrcat
        self.validate       = args.validator
        
        # Non-user defined variables
        self.log      = "log.txt"
        
        # Helpers.
        utils = Utilities.Utilities(self.debug)
        
        utils.o("Loading Pulsar ATNF Catalog:")
        
        # Build the settings object
        settings = Settings.Settings(self.debug)
        settings.load()
        
        psrcat = KnownSourceDB.KnownSourceDB(self.psrcat,settings)
        start = datetime.datetime.now()

        if(psrcat.parse() == True):
            end = datetime.datetime.now()
            utils.o("Loaded, time taken: " + str(end - start) + "\n")
        else:
            utils.o("Catalog file or ANTF web output has unexpected structure! Exiting...")
            sys.exit()
            
        # Check if the log file exists, if not, then create a new log file.
        # Check output file exists.
        if(utils.fileExists(self.log)==False):
            try:
                output = open(self.log, 'w') # First try to create file.
                output.close()
            except IOError:
                print "Cannot create application log file - this is not good!"
                    
        # ******************************
        #
        # Process user decision
        #
        # ******************************
    
        # If user chooses interactive mode.
        if(self.interactive):
            
            print "\nEntering interactive mode"
            
            interactive = Interactive.Interactive(self.debug,psrcat,self.outputPath)
            interactive.run()
            
        elif(self.validate):
            
            print "\nEntering validation mode"
            
            validator = Validator.Validator(self.debug,psrcat,self.outputPath)
            validator.run()
              
        else:
            # Else user chooses normal mode.
            print "\nRunning in standard mode"
            
            # Check output file exists.
            if(utils.fileExists(self.outputPath)):
                utils.o("Output file exists")
            else:
                try:
                    output = open(self.outputPath, 'w') # First try to create file.
                    output.close()
                except IOError:
                    print "Cannot create output file, exiting"
                    sys.exit()
            
            if(utils.dirExists(self.path)):
                self.processDirectory = True
                self.processFile      = False
            elif(utils.fileExists(self.path)):
                self.processDirectory = False
                self.processFile      = True
            else:
                print "Invalid path input, exiting"
                sys.exit()
            
            print "\n****************************"
            print "|  Command Line Arguments  |"
            print "****************************\n"
            print "\tCommand line arguments:"
            print "\tDebug:",               self.debug
            print "\tSearch path:",         self.path
            print "\tInteractive:",         self.interactive
            print "\tPSRCAT path:",         self.psrcat
            print "\tOutput path:",         self.outputPath
            print "\tProcess file:",        self.processFile
            print "\tProcess directory:",   self.processDirectory,"\n\n"
            
            inputProcessor = InputProcessor.InputProcessor(self.debug,psrcat,settings,self)
            inputProcessor.process()
        
        print "Done."
    
    # **************************************************************************************************** 
      
if __name__ == '__main__':
    Matcher().main()