"""

Designed to run on python 2.4 or later. 

Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""

# Custom file Imports:
from Utilities import Utilities

# ****************************************************************************************************
#
# CLASS DEFINITION
#
# ****************************************************************************************************

class Settings(Utilities):
    """                
    Contains basic settings for the candidate matcher, which can be changed
    by the user via a simple text based settings file.
    
    """
    
    # ****************************************************************************************************
    #
    # Constructor.
    #
    # ****************************************************************************************************
    
    def __init__(self,debugFlag):
        """
        Default constructor.
        
        Parameters:
        
        debugFlag     -    the debugging flag. If set to True, then detailed
                           debugging messages will be printed to the terminal
                           during execution.
        candidateName -    the name for the candidate, typically the file path.
        """
        
        Utilities.__init__(self,debugFlag)
        self.accuacy = -1.0
        self.radius  = -1.0
        self.path    = "Settings.txt"
        self.padding = 3600

    # ****************************************************************************************************
    
    def load(self):
        """
        Attempts to load settings from a file. If the file does not exist, the
        a new settings file will be automatically created.
        """
        
        if(self.fileExists(self.path)==False):
            self.build()    
        else:
            self.read()
            
        self.o("Settings:")
        self.o("Accuracy = " + str(self.accuacy) + " (Percentage accuracy to match the period and harmonics to).")
        self.o("Radius   = " + str(self.radius)  + " (The radius in degrees to search).")
        self.o("Padding   = " + str(self.padding)  + " (The padding to use for advanced matching).")
         
    # ****************************************************************************************************
        
    def read(self):
        """
        Reads in settings from a file. The settings are then stored in this object.
        """
        
        f = open(self.path)
        lines = f.readlines()
        f.close()
        
        if(len(lines)>0):
            for line in lines:
                self.process(line)
                
    # ****************************************************************************************************
            
    def build(self):
        """
        Builds a new settings file, then loads it.
        """
        destinationFile = open(self.path,'a')
        destinationFile.write(str("accuracy=0.5\n"))
        destinationFile.write(str("radius=0.5\n"))
        destinationFile.write(str("padding=3600\n"))
        destinationFile.close()
        
        self.read()
    
    # ****************************************************************************************************
        
    def process(self,line):
        """
        Process any lines of text found in the settings file.
        
        Parameters:
        
        line     -    the line of text from the file.
        
        Return:
        
        None.
        """
        
        if(line.startswith("accuracy")):
            value = line.replace("accuracy=","")
            self.accuacy = float(value)
        elif(line.startswith("radius")):
            value = line.replace("radius=","")
            self.radius = float(value)   
        elif(line.startswith("padding")):
            value = line.replace("padding=","")
            self.padding = float(value)   
    
    # ****************************************************************************************************
    
    def getAccuracy(self):
        """
        Gets the accuracy level stored in the settings.
        """
        return self.accuacy
    
    def getRadius(self):
        """
        Gets the radius stored in the settings.
        """
        return self.radius
    
    def getPath(self):
        """
        Gets the path to the settings file.
        """
        return self.path
    
    def getPadding(self):
        """
        Gets the advanced matching padding value
        """
        return self.padding
    
    # ****************************************************************************************************
    