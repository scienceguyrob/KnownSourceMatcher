"""
Represents a known radio source from the ANTF catalog. As the ANTF
catalog file is parsed, KnownSource objects will be created from each
catalog entry. This object retains all the information from the catalog
file.

Based on source code provided by Ben Stappers <Ben.Stappers@manchester.ac.uk>,
and Dan Thornton <dan.thornton-2@postgrad.manchester.ac.uk>.

By Rob Lyon <robert.lyon@cs.man.ac.uk>

"""
import math

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class KnownSource:
    """
    Represents a known radio source in the ANTF catalog file.
    Firstly this class is initialized by passing a name for this known source
    in to the method __init__(self,name) , i.e. "J0048+3412" or "B0052+51".
    
    This class also has an variable called sortAttribute, that is used to
    sort known sources for faster processing. For instance if we have 10,000,000
    candidate pulsars and 2,000 known sources, then a naive cross check would
    perform 10,000,000 x 2,000 = 20,000,000,000 comparisons. Hence by summing
    the right ascension (RA) and declination (DEC) values for each source,
    we can produce a single value that can be used to compare and sort the
    known sources much faster. This is based on the assumption that the sum
    of RA and DEC of two nearby sources should be very similar.
    
    """
    
    # ******************************
    #
    # INIT FUNCTION
    #
    # ******************************
    def __init__(self,name="Unknown"):
        """
        Initializes the class.
        Expects an input parameter name which is the primary name for 
        this individual source. Those pulsars named before 1993 have a
        "B" name, and are typically known by this name.
        
        """
        self.sourceParameters = {}
        self.sourceName = name
        self.sortAttribute = 0
        
    # ******************************
    #
    # UTILITY FUNCTIONS.
    #
    # ******************************
    
    def addParameter(self,lineFromFile):
        """
        Processes a parameter string found for this known source. Each parameter
        string found from the ATNF catalog file is stored in a dictionary, where
        the parameter name can be used as the key to access it. For instance
        given the string:
        
         DM       13.9                     1    snt97
        
        In this example this function will use DM as a key, and store the three accompanying 
        sub parameters in list.
        
        """
        substrings = lineFromFile.split()
        key = substrings[0]
        value = substrings[1:]
        
        # Try to grab the name of the source. A "B" name
        # will never overwrite a "J" name.
        if (key == "PSRJ" and self.sourceName == "Unknown"):
            self.sourceName = value[0]
        elif (key == "PSRB"):
            self.sourceName = value[0]
            
        if(key=="RAJ"):
            raj = str(value[0])
            rajComponents=raj.split(":")
            length = len(rajComponents)
            #print self.sourceName+"\tRAJ:"+ raj
            
            if(length<3):
                if(length==1):
                    raj=raj+":00:00"
                    value[0]=raj
                    self.sourceParameters[key] = value
                elif(length==2):
                    raj=raj+":00"
                    value[0]=raj
                    self.sourceParameters[key] = value
            else:
                self.sourceParameters[key] = value
           
        elif(key=="DECJ"):
            decj = str(value[0])
            decjComponents=decj.split(":")
            length = len(decjComponents)
            #print self.sourceName+"\tDECJ:"+ decj
            if(length<3):
                if(length==1):
                    decj=decj+":00:00"
                    value[0]=decj
                    self.sourceParameters[key] = value
                elif(length==2):
                    decj=decj+":00"
                    value[0]=decj
                    self.sourceParameters[key] = value
            else:
                self.sourceParameters[key] = value
        else:    
            # No matter what we add the parameter to the parameters dictionary
            self.sourceParameters[key] = value
        
        # Check to see if the sort attribute can be
        # computed, i.e. once we have the RA and DEC parameters.
        if (self.sortAttribute == 0 ):
            self.updateSortAttribute()
    
    # ******************************
    # 
    # ******************************
        
    def updateSortAttribute(self,):
        """
        Check to see if the RA and DEC parameters have been read in from
        the catalog file. If they have, then a sort attribute is computed.
        This attribute has NO astronomical meaning. It is simply a way
        to represent a candidate that allows for faster sorting.
        
        Some sources in the basic catalog file do not have Equatorial
        coordinates, but have an Ecliptic coordinates instead. The Ecliptic
        coordinate must be converted to Equatorial before the sort attribute is computed.
        
        """
        
        # Equatorial parameters
        RAJ_parameterList = self.getParameter("RAJ")
        DECJ_parameterList = self.getParameter("DECJ")
        
        if(RAJ_parameterList != None and DECJ_parameterList != None):
            
            self.sortAttribute += self.convert_RA_or_DEC_toInt(RAJ_parameterList[0])
            self.sortAttribute += self.convert_RA_or_DEC_toInt(DECJ_parameterList[0])
        
    # ******************************
    # 
    # ******************************
    
    def getParameter(self,key):   
        """
        Attempts to retrieve the parameter specified by the key provided
        from the sourceParameters dictionary. If the parameter is in the
        dictionary it is returned, else the value None is instead.
        
        """
        
        try:
            value = self.sourceParameters[key]
            return value
        except KeyError:
            return None
        
    # ******************************
    
    def getParameterAtIndex(self,key,index):   
        """
        Attempts to retrieve the parameter at the index supplied,
        for the list specified by the provided key.
        
        """
        value = self.getParameter(key)
        
        if(value != None):
            try:
                if( index < len(value) ):
                    return value[index]
                else:
                    return None
            except IndexError:
                return None
        else:
            return None
        
    # ******************************
    # 
    # ******************************
    
    def __str__(self):
        """
        Overridden method that provides a neater string representation
        of this class. This is useful when writing these objects to a file
        or the terminal.
        
        """
        
        # Extract the key parameters.
        RAJ = self.getParameterAtIndex("RAJ", 0)      
        DECJ = self.getParameterAtIndex("DECJ",0)        
        P0 = self.getParameterAtIndex("P0",0)       
        DM = self.getParameterAtIndex("DM",0)
            
        return self.sourceName + "," + str(RAJ) + "," + str(DECJ) + "," + str(P0) + "," + str(DM) + "," + str(self.sortAttribute)
    
    def shortStr(self):
        """
        Overridden method that provides a neater string representation
        of this class. This is useful when writing these objects to a file
        or the terminal. This version pads the source variable values to create 
        uniform outputs.
        
        """
        
        # Extract the key parameters.
        RAJ = self.getParameterAtIndex("RAJ", 0)      
        DECJ = self.getParameterAtIndex("DECJ",0)        
        P0 = self.getParameterAtIndex("P0",0)       
        DM = self.getParameterAtIndex("DM",0)
            
        return '{:<10}'.format(self.sourceName) + "\t" + '{:<12}'.format(str(RAJ)) + "\t" + '{:<13}'.format(str(DECJ)) + "\t" + '{:<20}'.format(str(P0)) + "\t" + '{:<15}'.format(str(DM)) 

    # ******************************
    
    def debug(self):
        """
        Produces a string representation of this complete object.
        """
        concat = ""
        
        for key in self.sourceParameters:
            value = self.sourceParameters[key]
            
            stringKey = str(key)
            stringValue = ",".join(value)
            concat += "Key: " + stringKey + " Value: " + stringValue+ "\n"
        
        return concat
    
    # ******************************
    
    def printLabelOutput(self):
        """
        Returns a string describing this object, formatted nicely
        for when labeling candidates.
        """
        
        print "Candidate: " , str(self.sourceName) , "\n" ,\
               "RAJ: "       , str(self.getParameter("RAJ")[0])  , "\n" , \
               "DECJ: "      , str(self.getParameter("DECJ")[0]) , "\n" , \
               "P0: "        , str(self.getParameter("P0")[0])   , "\n" , \
               "DM: "        , str(self.getParameter("DM")[0])   , "\n" , \
               "SNR: "       , str(self.getParameter("SNR")[0]) , "\n" , "MATCHED TO...\n"\
               "Known Source: "     , str(self.getParameter("KS")[0] )    , "\n" ,\
               "Known Source RAJ: " , str(self.getParameter("KS_RAJ")[0]) , "\n" ,\
               "Known Source DECJ: ", str(self.getParameter("KS_DECJ")[0]), "\n" ,\
               "Known Source P0: "  , str(self.getParameter("KS_P0")[0])  , "\n" ,\
               "Known Source DM: "  , str(self.getParameter("KS_DM")[0])  , "\n" ,\
               "Harmonic Number: "  , str(self.getParameter("HARMONIC_NUMBER")[0]) , "\n",\
               "Separation (deg): "       , str(self.getParameter("SEP")[0])    , "\n"
               
    # ******************************
    # 
    # ******************************
    
    def convert_RA_or_DEC_toInt(self, RA_or_DEC):
        """
        Converts a string of the form HH:MM:SS i.e. 00:00:00 or 00:00 to an
        integer value. This is done by expressing the hours and minutes in
        seconds, and then summing the result. PLEASE note that this method
        isn't intended to be astronomically correct. I'm simply manipulating,
        the numbers, meaning is irrelevant.
        
        """
        
        h = 0
        m = 0
        s = 0
        
        splitTime = str.split(RA_or_DEC, ":")

        h = int(splitTime[0].replace("+",""))
        try:
            m = math.floor(float(splitTime[1]))
        except IndexError:
            m = 0
            
            
        # Some sources do not have seconds listed.
        try:
            s = math.floor(float(splitTime[2]))
        except IndexError:
            s = 0
            
        return int( (h * 3600) + (m * 60) + s )
    
    # ******************************