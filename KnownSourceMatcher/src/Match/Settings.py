"""
This file is part of the KnownSourceMatcher.

KnownSourceMatcher is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

KnownSourceMatcher is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with KnownSourceMatcher.  If not, see <http://www.gnu.org/licenses/>.

File name:    Settings.py
Created:      February 7th, 2014
Author:       Rob Lyon
 
Contact:    rob@scienceguyrob.com or robert.lyon@postgrad.manchester.ac.uk
Web:        <http://www.scienceguyrob.com> or <http://www.cs.manchester.ac.uk> 
            or <http://www.jb.man.ac.uk>
            
This code runs on python 2.4 or later.

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
        self.telescope = "Parkes"

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
        self.o("Telescope   = " + str(self.padding)  + " (Instrument used for observations).")
         
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
        destinationFile.write(str("telescope=Parkes\n"))
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
        elif(line.startswith("telescope")):
            value = line.replace("telescope=","")
            self.telescope = str(value)    
    
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
    
    def getTelescope(self):
        """
        Gets the telescope assumed used during observations.
        """
        return self.telescope
    
    # ****************************************************************************************************
    