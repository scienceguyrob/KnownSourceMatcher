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

File name:    Validator.py
Created:      February 7th, 2014
Author:       Rob Lyon
 
Contact:    rob@scienceguyrob.com or robert.lyon@postgrad.manchester.ac.uk
Web:        <http://www.scienceguyrob.com> or <http://www.cs.manchester.ac.uk> 
            or <http://www.jb.man.ac.uk>
            
This code runs on python 2.4 or later.

"""

from Utilities import Utilities
import KnownSource
import copy

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class Validator(Utilities):
    """                
    Provides methods that can be used to validate searching code performance.
    This helps tune to the searching code so that it is not too sensitivity nor
    to aggressive in rejective potential matches.
    """
    
    # ******************************
    #
    # INIT FUNCTION
    #
    # ******************************
    def __init__(self,debugFlag,db,output):
        """
        Initialises the class.
        
        """
        Utilities.__init__(self,debugFlag)  
        self.db = db
        self.outputFile = output
    
    # ******************************
    #
    # FUNCTIONS.
    #
    # ******************************
    
    def run(self):
        """
        Runs the validation code.
        """
        print "Running validation tests"
        
        cands_1 = self.getRealCands()
        cands_2 = self.getMutatedCands()
        
        for cand in cands_1:
            self.db.match(cand,self.outputFile)
           
        for cand in cands_2:
            self.db.match(cand,self.outputFile)
        
    # ****************************************************************************************************
    
    def getRealCands(self):
        """
        Here we simply try to match candidates in the catalog to themselves.
        If the matching algorithm works, then all known sources should be matched to
        themselves. This can be checked by looking at the output file produced by this 
        function and checking the matches.
        """
        
        knownSources = []
        
        self.catalogueFile = open(self.db.getPath(),'r') # Read only access
        
        # A temporary object that is used create new KnownSource instances.
        tempSource = KnownSource.KnownSource()
            
        # Stores the headers in the file, so we can match parameters
        # with their intended meaning.
        columnDictionary = {}
            
        for line in self.catalogueFile.readlines():
            if ( line[0] == '-'):
                # Ignore these lines starting with empty space.
                pass
            elif(line[0] == ' ' or line[0] == '\n' or line[0] == '\r'):
                pass
            elif ( line[0] == '#'):
                # This line contains the column headers, we need these
                # to understand the structure of the file.
                headers = line.split()
                    
                # Add headers to a dictionary.          
                for i in range(len(headers)):
                    if(i > 2):
                            
                        # Here we have to apply an offset, as the "Long with errors"
                        # format has a structure that is not consistent. If you look
                        # below you will see why using an annotated version of the
                        # start of one such file. If we parse the header of the file,
                        # we can get indexes for the parameters. But these do not match up.
                        # 
                        # -------------------------- Expected Index of Parameters ----------------------
                        # |      |       |                |                 |             |            |
                        # |      |       |                |                 |             |            |
                        # v      v       v                v                 v             v            v
                        # 0      1       2                3                 4             5            6
                        #
                        # -----------------------------------------------------------------------------------------
                        # #     NAME    RAJ               DECJ              P0            F0           DM
                        #              (hms)              (dms)             (s)           (Hz)         (cm^-3 pc)
                        # -----------------------------------------------------------------------------------------
                        # 1     PSR A   00:06:04 2.0e-01  +18:34:59 4.0e+00  1.0 1.4e-10  1.4 3.0e-10  9.0 6.0e-01
                        # -----------------------------------------------------------------------------------------
                        #
                        # 0       1         2       3         4        5      6     7      8     9      10    11
                        # ^       ^         ^       ^         ^        ^      ^     ^      ^     ^      ^     ^
                        # |       |         |       |         |        |      |     |      |     |      |     |
                        # |       |         |       |         |        |      |     |      |     |      |     |
                        # ------------------------ Actual Index of Each Parameter -----------------------------
                        #
                        #
                        # As can be seen, when the parameter index is greater than two,
                        # an offset must be used to get the desired parameter. i.e. if you want
                        # to get the DM, you might use the index=6. But an index of 6 actually
                        # points to P0. To get the DM we must use (index - 1) x 2 as:
                        #
                        # DM index = (expected index - 1) x 2 
                        #          = (6 - 1) x 2
                        #          = 10 
                        #
                        # As you can see 10 points to the parameter we actually wanted in this example.                         
                              
                        columnDictionary[copy.copy(headers[i])] = (i-1)*2
                    else:
                        columnDictionary[copy.copy(headers[i])] = i
                    
            else:
                # Build a known source object from the data, assuming we know
                # the file structure from the headers. Basically this looks
                # more complicated than it is. All we are doing is 1) taking the
                # single pieces of information out of an individual line describing
                # a source, then 2) format it so that it can be added to a known
                # source object. I've had to do this, as the ATNF catalogue file
                # doesn't contain all the information we need (RAJ,DECJ,P0,F0 are often missing).
                # So the only way to get this is to use the ANTF web form, which outputs
                # data in a different file format to that used in the catalogue file.
                    
                # Split the individual source entry, this produce a list.                  
                sourceDetails = line.split()
                    
                # Use the column keys to map the entries in the sourceDetails list.
                for key in columnDictionary.keys():
                    if(key != "#"):
                            
                        # The key is the header name remember
                        index = columnDictionary[key]
                            
                        if(key == "NAME"):
                            name = sourceDetails[index] # get name of the source using the correct index
                            if("J" in name):
                                tempSource.addParameter("PSRJ    " + name + "    0    0")
                            else:
                                tempSource.addParameter("PSRB    " + name + "    0    0")
                        elif(key == "RAJ"):
                            raj = sourceDetails[index] 
                            tempSource.addParameter("RAJ    " + raj + "    " + sourceDetails[index+1] + "    0")
                        elif(key == "DECJ"):
                            decj = sourceDetails[index]
                            tempSource.addParameter("DECJ    " + decj + "    " + sourceDetails[index+1] + "    0")
                        elif(key == "P0"):
                            p0 = sourceDetails[index]
                            tempSource.addParameter("P0    "  + p0 + "    " + sourceDetails[index+1] + "    0")
                        elif(key == "F0"):
                            f0 = sourceDetails[index]
                            tempSource.addParameter("F0    " + f0 + "    " + sourceDetails[index+1] + "    0")
                        elif(key == "DM"):
                            dm = sourceDetails[index]
                            tempSource.addParameter("DM    " + dm + "    " + sourceDetails[index+1] + "    0")
                                       
                knownSources.append(copy.deepcopy(tempSource))
                
                # Simply resets the temporary object. Does
                # not initialise a new object, thus saving
                # CPU overhead (although small, it all adds up). 
                # Particularly when this application may need to do
                # 200,000,000,000 comparisons if checking all the candidates
                # at /local/scratch/cands .
                tempSource.sourceParameters.clear()
                tempSource.sortAttribute = 0
                tempSource.sourceName = "Unknown"
        
            self.catalogueFile.close()
            
        return knownSources
        
    # ****************************************************************************************************
    
    def getMutatedCands(self):
        """
        Uses this code to manually tune the application to your needs. So alter the settings
        file manually outside of this script, and then test to see if candidates you expect
        or don't expect to be matched, are. This function contains three candidates which you can
        alter in terms of RA and DEC, period and DM.
        
        Settings of:
        accuracy=1.0
        radius=0.5
        padding=36000
        
        appear to work well.
        """
        
        knownSources = []
        
        # A temporary object that is used create new KnownSource instances.
        tempSource = KnownSource.KnownSource()
        
        # Actual known source:
        # Name          RA             DEC            P     F0    DM
        # J1830-1033    18:30:11.88    -10:33:40.7    245    0    203
            
        tempSource.addParameter("PSRJ    J1830-1033    0    0")
        tempSource.addParameter("RAJ    18:30:44    1.0e-01    0")
        tempSource.addParameter("DECJ   -10:33:55   1.0e-01    0")
        tempSource.addParameter("P0     244         1.0e-01    0")
        tempSource.addParameter("F0     0           1.0e-01    0")
        tempSource.addParameter("DM     203         1.0e-01    0")
                                     
        knownSources.append(copy.deepcopy(tempSource))
        tempSource.sourceParameters.clear()
        tempSource.sortAttribute = 0
        tempSource.sourceName = "Unknown"
        
        tempSource.addParameter("PSRJ    J1830-1033    0    0")
        tempSource.addParameter("RAJ    18:30:52    1.0e-01    0")
        tempSource.addParameter("DECJ   -10:33:10   1.0e-01    0")
        tempSource.addParameter("P0     243         1.0e-01    0")
        tempSource.addParameter("F0     0           1.0e-01    0")
        tempSource.addParameter("DM     205         1.0e-01    0")
                                       
        knownSources.append(copy.deepcopy(tempSource))
        tempSource.sourceParameters.clear()
        tempSource.sortAttribute = 0
        tempSource.sourceName = "Unknown"
        
        tempSource.addParameter("PSRJ    J1830-1033    0    0")
        tempSource.addParameter("RAJ    18:29:52    1.0e-01    0")
        tempSource.addParameter("DECJ   -10:32:10   1.0e-01    0")
        tempSource.addParameter("P0     243         1.0e-01    0")
        tempSource.addParameter("F0     0           1.0e-01    0")
        tempSource.addParameter("DM     205         1.0e-01    0")
                                       
        knownSources.append(copy.deepcopy(tempSource))
        tempSource.sourceParameters.clear()
        tempSource.sortAttribute = 0
        tempSource.sourceName = "Unknown"
            
        return knownSources
        
    # ****************************************************************************************************
    
    def validateOutput(self,path):
        """
        """
        print "Validation output in file at: ",path

    # ****************************************************************************************************