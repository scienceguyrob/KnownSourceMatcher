"""
Compares pulsar candidates to known sources from the ANTF pulsar catalog.
First parses the catalog before comparisons can take place. Alternatively
this class with parse the output from the ANTF web interface in "Long with errors"
format (provided you have saved this output to a file and passed in the path
to this file).

Based on source code provided by Ben Stappers <Ben.Stappers@manchester.ac.uk>,
and Dan Thornton <dan.thornton-2@postgrad.manchester.ac.uk>.

By Rob Lyon <robert.lyon@cs.man.ac.uk>

"""

# TODO: EDIT 2:  Added ordereddict here to make compatible with Python 2.4.
import ordereddict, collections, copy, KnownSource, math, operator, os, string, numpy as np

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class KnownSourceDB:
    """
    Represents and wraps around the ANTF catalog file or
    ANTF web interface output.
    
    """
    
    # ******************************
    #
    # INIT FUNCTION
    #
    # ******************************
    def __init__(self, path,settings):
        """
        Initialises the class, and passes the path to the ANTF catalog file.
        
        """             
        self.path = path
        self.harmonics = [1, 0.5, 0.25,0.125,0.0625]
        self.possibleMatches = 0
        self.knownSourceCount = 0
        self.NaiveSearch = False
        
        self.accuracy = settings.getAccuracy()
        self.radius = settings.getRadius()
        self.searchPadding = settings.getPadding()
        self.DM_percentAccuracy = settings.getAccuracy()
        
    
    # ******************************
    #
    # PARSE FUNCTION.
    #
    # ******************************
    
    def parse(self):
        """
        Reads the catalog file or ATNF web form output line by line. A new KnownSource
        object is created for each source found in the file.
        
        """       
        # The ANTF catalog file contains a number of known sources.
        # Each source has a number of parameters, though the exact number
        # of parameters varies from source to source. The format of the
        # catalog file is as follows (as structured from the start of the file):
        #
        # PSRJ     J0007+7303                    aaa+09c     
        # RAJ      00:07:01.7               2    awd+12      
        # DECJ     +73:03:07.4              8    awd+12      
        # F0       3.165827392              3    awd+12      
        # F1       -3.6120E-12              5    awd+12      
        # F2       4.1E-23                  7    awd+12      
        # F3       5.4E-30                  9    awd+12      
        # @-----------------------------------------------------------------
        # PSRB     B0021-72G                     rlm+95      
        # PSRJ     J0024-7204G                               
        # RAJ      00:24:07.9587            3    fck+03      
        # DECJ     -72:04:39.6911           7    fck+03      
        # PMRA     4.2                      14   fck+03      
        # PMDEC    -3.7                     12   fck+03      
        # F0       247.50152509652          2    fck+03 
        # @-----------------------------------------------------------------
        # .
        # .
        # . 
        # <continued>
        #           
        # Here we read each line of the file, and create a new known source
        # each time we encounter the text "PSR". Each time a parameter is
        # found it is added to this object.
        #
        # ALTERNATIVELY, the format we can expect from the web interface "Long with errors"
        # looks like the following:
        #
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        # #     NAME         RAJ                       DECJ                      P0                            F0                          DM
        #                   (hms)                     (dms)                     (s)                           (Hz)                        (cm^-3 pc)
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        # 1     J0006+1834   00:06:04.8       2.0e-01  +18:34:59        4.0e+00  0.69374767047        1.4e-10  1.4414462816       3.0e-10  12.0       6.0e-01
        # 2     J0007+7303   00:07:01.7       2.0e-01  +73:03:07.4      8.0e-01  0.3158731909         3.0e-10  3.165827392        3.0e-09  *                0
        # 3     B0011+47     00:14:17.75      4.0e-02  +47:46:33.4      3.0e-01  1.240699038946       1.1e-11  0.805997239145     7.0e-12  30.85      7.0e-02
        # 4     J0023+09     00:23                  0  +09:00                 0  0.00305                    0  327.868852         0        14.3             0
        # 5     B0021-72C    00:23:50.35311   9.0e-05  -72:04:31.4926   4.0e-04  0.00575677999551320  1.7e-16  173.708218966053   5.0e-12  24.599     2.0e-03
        #        
        # 6     B0021-72D    00:24:13.87934   7.0e-05  -72:04:43.8405   3.0e-04  0.00535757328486266  1.8e-16  186.651669856838   6.0e-12  24.729     2.0e-03
        # 7     B0021-72E    00:24:11.1036    1.0e-04  -72:05:20.1377   4.0e-04  0.00353632915276031  1.3e-16  282.77910703517    1.0e-11  24.230     2.0e-03
        # 8     B0021-72F    00:24:03.8539    1.0e-04  -72:04:42.8065   5.0e-04  0.00262357935251098  1.4e-16  381.15866365655    2.0e-11  24.379     5.0e-03
        # 9     B0021-72G    00:24:07.9587    3.0e-04  -72:04:39.6911   7.0e-04  0.0040403791435629   4.0e-16  247.50152509652    2.0e-11  24.441     5.0e-03
        # 10    B0021-72H    00:24:06.7014    3.0e-04  -72:04:06.795    1.0e-03  0.0032103407093484   5.0e-16  311.49341784442    4.0e-11  24.36      3.0e-02
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        
        knownSources = {}
        
        if(self.isCatalogueFile(self.path)==True):
            
            self.catalogueFile = open(self.path,'r') # Read only access

            # A temporary object that is used create new KnownSource instances.
            tempSource = KnownSource.KnownSource()
        
            for line in self.catalogueFile.readlines():
                if ( line[0] == '#'):
                    # Ignore these lines.
                    pass
                elif ( line[0] == '@'):
                    # This signals the end of the current source
                    # so simply add the current KnownSource object
                    # to the known source dictionary and clean up.
                    knownSources[copy.copy(tempSource.sourceName)] = copy.deepcopy(tempSource)
                
                    # Simply resets the temporary object. Does
                    # not initialise a new object, thus saving
                    # CPU overhead (although minuscule, it all adds up). 
                    tempSource.sourceParameters.clear()
                    tempSource.sortAttribute = 0
                    tempSource.sourceName = "Unknown"
                
                elif ( len(line) > 2 ):
                    # If the line doesn't begin with '#' or '@' and isn't
                    # an empty line, then process it.
                    tempSource.addParameter(line)
                else:
                    pass # else ignore
        
            self.catalogueFile.close()
        
        elif(self.isCatalogueWebOutput(self.path) == True):
            
            self.catalogueFile = open(self.path,'r') # Read only access
        
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
                                       
                    knownSources[copy.copy(tempSource.sourceName)] = copy.deepcopy(tempSource)
                
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
        
        # Make sure dictionary isn't empty. If it is then the 
        # file has not been read. So we empty the application.
        if(len(knownSources) < 1):
            return False
            
        # Next we create an ordered dictionary object. We
        # can then store the known sources sorted according
        # to their sortAttribute.
         
        # TODO: EDIT 2: Change to make compatible with Python 2.7
        #self.orderedSourcesDict = collections.OrderedDict()
        #self.orderedAccess = collections.OrderedDict()
        self.orderedSourcesDict = ordereddict.OrderedDict()
        self.orderedAccess = ordereddict.OrderedDict()
        
        index = 0
        for source in (sorted(knownSources.values(), key=operator.attrgetter('sortAttribute'))):
            self.orderedSourcesDict[copy.copy(source.sourceName)] = copy.deepcopy(source)
            
            # This next data structure is used for faster searching.
            # It creates an ordered dictionary structured as follows:
            # 
            # [0:"PSR 1", 1:"PSR 2", 2:"PSR 3" ,..., n:"PSR n"]
            #
            # where the keys are pulsar names. It allows us to access known sources using an
            # integer key, rather than a string key. This is extremely useful, as to iterate over a
            # dictionary we must usually get the keys first. Obtaining keys, i.e. a call like:
            #
            # for key in self.orderedSourcesDict.keys():
            #  ... do something
            #
            # This actually requires stepping through the entire dictionary to extract each key. This
            # is an expensive operation (in terms of CPU time) if performed more than a handful of times.
            #
            # However using this orderedAccess dictionary we can iterate over
            # known sources as though they were in a list, without the expensive
            # call to get the keys. For instance we can just call:
            #
            # knownSource = self.orderedAccess[5]
            #
            # This might not seem to useful, but it allows us to build a much faster comparison algorithm.
            
            self.orderedAccess[index] = copy.copy(source.sourceName)
            index += 1
        
        # Clean up this dictionary as it is no longer required.
        knownSources.clear()
        
        # DEBUGGING -- Check contents of the ordered dictionary.
        MissingParamsCount = 0
        self.knownSourceCount = 0;
        for key in self.orderedSourcesDict.keys():
            value =  self.orderedSourcesDict[key]
            #print key + " : "+ str(value.sortAttribute)
            #print value.__str__()
            self.knownSourceCount += 1
            
            # Count those entries without RAJ and DECJ
            if (value.getParameter("RAJ") == None):
                MissingParamsCount +=1
        
        print "Total sources: ", self.knownSourceCount       
        print "Sources missing parameters: ", MissingParamsCount
        
        return True
        
    # ******************************
    #
    # COMPARISON FUNCTIONS.
    #
    # ****************************
    
    # ******************************
    # 
    # ******************************
    
    def match(self,candidateSource,outputFile):
        """
        Looks for matches in the ATNF catalog given the supplied parameters.
        
        """
        
        # First define output file.
        self.outputFile = outputFile
        
        # SEARCH OPTION ONE: NAIVE COMPARISON
        # Given N known sources and M candidates, this will require N x M comparisons. 
        # With M =11,000,000 and N = 2008, this equates to 2.2088 x 10^10 or
        # 22,088,000,000 comparisons.
        
        # Only allow the naive search if no RAJ or DECJ is provided
        if(candidateSource.getParameter("RAJ") is None ):
            self.NaiveSearch = True;
            
        if (self.NaiveSearch == True):
            
            # For each known source....
            for key in self.orderedSourcesDict.keys():
            
                knownSource = self.orderedSourcesDict[key]
                self.compareCandidateToKnownSources(candidateSource,knownSource)
                  
        # SEARCH OPTION TWO: THRESHOLDED COMPARISON:
        # Given N known sources and M candidates, this will require WORST case N x M comparisons.
        # This would only happen if all the known sources have nearly the same RAJ and
        # DECJ as each candidate (within some bounds i.e. +/- 100). The chances of this happening
        # are as close to zero as you'll ever get!
        #
        # So by using the sort attribute and a threshold on this value, the actual
        # number of comparisons will be much less. The AVERAGE case is M + log2(N) + C , where C is a number
        # of comparisons made between known sources and candidates which have similar RAJ and DECJ
        # values. The true value of C is dependent on the padding parameter supplied by the user
        # and the similarity of the known sources and candidates.
        #
        # i.e. Given M = 11,000,000 and N = 2008 and C=50 (overestimate!), there would be 561,000,011 comparisons,
        # compared to 22,088,000,000 comparisons for the naive approach.
        # 
        # To illustrate this difference, comparing 1300 candidates to 2008 known sources using the naive
        # approach took ~5 minutes. This optimized approach took only 10 seconds.
        #
        # The expected numbers of comparisons given varying C and M = 11,000,000 and N = 2008:
        #
        # C = 1    -> ~ 22,000,000 BEST CASE
        # C = 10   -> ~ 121,000,011
        # C = 20   -> ~ 231,000,011
        # C = 50   -> ~ 561,000,011
        # C = 100  -> ~ 1,111,000,011
        # C = 1000 -> ~ 11,011,000,010
        # C = 2008 -> ~ 22,099,000,010 WORST CASE only marginally worse than Naive Case = 22,088,000,000
        
        else:
            
            # This call gives us an index in the sources dictionary,
            # where we can start looking for matches (rather than searching 
            # the whole data structure exhaustively).
            
            indexToBeginSearch = self.divideAndConquerSearch(0,self.knownSourceCount,candidateSource.sortAttribute)
            
            # Compare with the known source at the specified index.
            key = self.orderedAccess[indexToBeginSearch]
            knownSource = self.orderedSourcesDict[key]
            
            # Check if the sort attribute is within the bounds.
            if( (candidateSource.sortAttribute - int(self.searchPadding)) <= knownSource.sortAttribute <= (candidateSource.sortAttribute + int(self.searchPadding)) ):
                self.compareCandidateToKnownSources(candidateSource,knownSource)
            
                # Now recursively compare to the left and the right of this index.
                # We use a user specified padding (defaults to 3600) to catch those sources that are nearby.
                self.compareRight(candidateSource, indexToBeginSearch,  int(self.searchPadding) )
                self.compareLeft(candidateSource, indexToBeginSearch,  int(self.searchPadding) )
        
        
        # Explicit cleanup.
        candidateSource.sourceParameters.clear()
        candidateSource.sortAttribute = 0
        candidateSource.sourceName = "Unknown"
    
    # ******************************
    # 
    # ******************************
    
    def compareCandidateToKnownSources(self,candidateSource,knownSource):
        """
        Performs the comparison. This works by evaluating a number of search 
        conditions w.r.t candidate period, DM, and its position. The following
        conditions must hold before a candidate is matched to a known source:
        
        1. The candidate period must fall within a user specified range of the known source period.
           Here this range is a percentage, i.e. the candidate period must be no greater than,
           and no less than say m % of the known source period. i.e. given m = 5, if a known
           source period is one, then a candidate will only match it if its period is in the
           range 1.05 - 0.95.  The default accuracy level is 0.5%.
           
        2. The candidate DM must fall within a range as above. The default DM accuracy is 5%.
        
        3. The angular separation in degrees between the known source and candidate,
           must be less than a user specified radius (default is 1 degree).
        
        To change the defaults above, go the the CandidateCrosschecker.py file, and modify the
        parser arguments at the top.
        
        """
        
        # This check is added as the HTRU catalog file maintained
        # by Michael Keith has a F0 parameter but not P0. So here we convert F0
        # to P0 in this case.
        if(knownSource.getParameter("P0") is None and  knownSource.getParameter("F0") is not None):
            F0 = knownSource.getParameter("F0")[0]
            P0 = 1 / float(F0)
            knownSource.addParameter("P0    "  + str(P0) + "    0    0")
            
        if(knownSource.getParameter("P0") is not None ):
            
            #print knownSource.__str__()  
            # We now try to extract the parameters we need for our comparison.  
            catalog_period = knownSource.getParameter("P0")[0]
            catalog_RA = knownSource.getParameter("RAJ")[0]
            catalog_DEC = knownSource.getParameter("DECJ")[0]
            
            # If reading the ATNF plain catalog file DM may not be present.
            if(knownSource.getParameter("DM") is None):
                catalog_DM = "*"
            else:
                catalog_DM = knownSource.getParameter("DM")[0]  
                
            # DEBUGGING
            #print "PULSAR -> Period = ",catalog_period, " RA = ", catalog_RA, " DEC = ", catalog_DEC, " DM = ", catalog_DM
            
            cand_RAJ = candidateSource.getParameter("RAJ")[0]
            cand_DECJ = candidateSource.getParameter("DECJ")[0]
            cand_period = candidateSource.getParameter("P0")[0]
            cand_DM = candidateSource.getParameter("DM")[0]
            
            # Extra check added to stop errors when a candidates is loaded in outside
            # the main application, i.e. via validation methods.
            if("*" in cand_period):
                cand_period=0
                
            acc = (float(self.accuracy)/100)*float(cand_period)
                
            for i in range(0,len(self.harmonics)):
                        
                # Some candidates have no P0 or F0, i.e. J0923-31
                if(catalog_period is not "*"):
                            
                    search_cond = float(cand_period) > (float(catalog_period) * float(self.harmonics[i])) - float(acc) and\
                                 (float(cand_period) < (float(catalog_period) * float(self.harmonics[i])) + float(acc))
                        
                    if( cand_DM is not "*" and float(cand_DM) != 0 and float(self.DM_percentAccuracy) != 0 and (catalog_DM != "unknown" and catalog_DM != "*")): # has the user input these as options? 
                        
                        dm_acc = (float(self.DM_percentAccuracy)/100)*float(cand_DM) 
                                   
                        search_cond = search_cond and ((float(catalog_DM) > float(cand_DM) - float(dm_acc)) and\
                                                       (float(catalog_DM) < float(cand_DM) + float(dm_acc)))
                            
                    if(cand_RAJ != "00:00:00" and cand_DECJ != "00:00:00"):
                        theta = self.findAngularSep(cand_RAJ, cand_DECJ, catalog_RA, catalog_DEC)
                        search_cond = search_cond and (theta<float(self.radius))
                    else:
                        theta = "unspecified"
                            
                    if(search_cond):  
                        self.recordPossibleMatch(candidateSource,knownSource.sourceName, catalog_period, self.harmonics[i],\
                                                 catalog_RA, catalog_DEC, catalog_DM, theta,knownSource.sortAttribute)
                
    # ******************************
    # 
    # ******************************
    
    def divideAndConquerSearch(self,start,end,sort):
        """
        Searches through a data structure containing KnownSource objects using a
        divide and conquer approach. Instead of looping through all the known
        sources in a data structure, this recursive procedure searches by
        dividing the data structure up based on the outcome of an attribute test.
        Hence the search space is divided in half with each recursive call. This method
        then returns an index for us to search from in the self.orderedSourcesDict.
        
        Attribute test:
        In the the KnownSource class I have created a "sort" attribute that 
        can be used to order KnownSource objects. This "sort" attribute is the RAJ converted
        to seconds added to the DECJ converted to seconds. Any two sources which are
        nearby should have very similar sums. i.e. a contrived example:
        
        Source 1
        RAJ = 00:00:01
        DECJ = 00:00:00
        Sort attribute = 1
        
        Source 2
        RAJ = 00:00:01
        DECJ = 00:00:01
        Sort attribute = 2
        
        We can use this to compare candidates extremely quickly.
        
        Example of how this algorithm works:
        
        We have a candidate with a sortAttribute == 1. We want to know which known 
        sources are most similar to it.
        
        We have 100 known sources against which to compare, which are ordered
        according to their sort attribute. The first known source
        has a sort attribute = 1 and the last a sort attribute = 100.
        
        So the known source at position 1 has a sort attribute = 1.
        ..
        The known source at position 50 has a sort attribute = 50.
        ..
        The known source at position 100 has a sort attribute = 100.
        
        SEARCH PROCEDURE:
        
        Start            Midpoint            End
         |                  |                 |
         V                  V                 V
         ______________________________________
        | | | | | | | | | | | | | | | | | | | |
        --------------------------------------
         0                                   n-1
        
        If the candidate sort attribute is less than the midpoint sort attribute then search:
        
        Start            Midpoint
         |                  |                 
         V                  V                 
         ____________________
        | | | | | | | | | | | 
        ---------------------
        0                (n-1)/2
        
        else search:
        
                         Midpoint            End
                            |                 |
                            V                 V
                             __________________
                            | | | | | | | | | |
                            -------------------
                        (n-1)/2               n-1
        
        If the sort attribute is less than the midpoint, we search:
        
        Start    Midpoint    End
         |         |         |        
         V         V         V           
         ____________________
        | | | | | | | | | | | 
        ---------------------
        0       (n-1)/4    (n-1)/2
                            
        We then repeat this procedure, splitting each time
        until we have found a single index. Using the values above the
        search would proceed as follows,
        
        1. Search 1 - 100:
            Split point is index 51 which has sort a attribute = 51
            As 1 < 51, search 1 - 51           
            |
            V
            2. Search 1 - 51:
                Split point is index 26 (rounded up from 25.5) which has sort a attribute = 26
                As 1 < 26, search 1 - 26
                |
                V
                3. Search 1 - 26:
                    Split point is index 14 (13.5 rounded up) which has sort a attribute = 14
                    As 1 < 14, search 1 - 14 
                    |
                    V
            
                    4. Search 1 - 14:
                        Split point is index 8 (7.5 rounded up) which has sort a attribute = 8
                        As 1 < 8, search 1 - 8 
                        |
                        V
                    
                        5. Search 1 - 8:
                            Split point is index 5 (4.5 rounded up) which has sort a attribute = 5
                            As 1 < 5, search 1 - 5 
                            |
                            V
                            
                            6. Search 1 - 5:
                                Split point is index 3 which has sort a attribute = 3
                                As 1 < 3, search 1 - 3 
                                |
                                V
                                
                                7. Search 1-3:
                                    return index 2.
                                    
        Note that even though the procedure above returned index 2 and not one, 
        thats OK. we are only looking for a place to start searching from. From this
        index we then search left and right using compareRight(candidateSource,index,padding)
        and compareLeft(self,candidateSource,index,padding).
        
        """
        
        #print "Start: ", start, " End: ", end, " Sort: ",sort
        
        # If there is only one gap between start and end,
        # then return that position. This prevents the algorithm
        # from looping recursively forever.
        if(end - start == 2):
            #print "End - start == 2."
            return start+1
        elif(end - start == 1):
            return start
        
        midpoint = int( math.ceil( (float(end) + float(start) ) / float(2) ) )
        
        #print "Midpoint: ", midpoint
        key = self.orderedAccess[midpoint]
        sourceAtMidpoint = self.orderedSourcesDict[key]
        knownSourceSortAttribute = sourceAtMidpoint.sortAttribute
        
        #print "Known Source Attribute: ", knownSourceSortAttribute
    
        if(sort < knownSourceSortAttribute):
            return self.divideAndConquerSearch(start,midpoint,sort)
        elif(sort > knownSourceSortAttribute):
            return self.divideAndConquerSearch(midpoint,end,sort)
        else:
            return midpoint

    def compareRight(self,candidateSource,index,padding):
        """
        Compares a candidate to those known sources which occur
        to the right of a specified index in the orderedSourcesDict to a candidate. 
        
        """
        
        if(index+1 < self.knownSourceCount and index+1 > -1):
            # Compare with the known source at the specified index.
            key = self.orderedAccess[index+1]
            knownSource = self.orderedSourcesDict[key]
            
            if( (candidateSource.sortAttribute - padding) <= knownSource.sortAttribute <= (candidateSource.sortAttribute + padding) ):
                #print str(candidateSource.sortAttribute - padding), "<=" ,str(knownSource.sortAttribute), "<=", str(candidateSource.sortAttribute + padding)
                self.compareCandidateToKnownSources(candidateSource,knownSource)
                self.compareRight(candidateSource,index+1,padding)
            
    def compareLeft(self,candidateSource,index,padding):
        """
        Compares a candidate to those known sources which occur
        to the left of a specified index in the orderedSourcesDict to a candidate. 
        
        """
        
        if(index-1 < self.knownSourceCount and index-1 > -1):
            # Compare with the known source at the specified index.
            key = self.orderedAccess[index-1]
            knownSource = self.orderedSourcesDict[key]
            
            if( (candidateSource.sortAttribute - padding) <= knownSource.sortAttribute <= (candidateSource.sortAttribute + padding) ):
                #print str(candidateSource.sortAttribute - padding), "<=" ,str(knownSource.sortAttribute), "<=", str(candidateSource.sortAttribute + padding)
                self.compareCandidateToKnownSources(candidateSource,knownSource)
                self.compareLeft(candidateSource,index-1,padding)
            
        
    # ******************************
    # 
    # ******************************
               
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
    
    # ******************************
    #
    # FILE OUTPUT FUNCTIONS.
    #
    # ******************************

    def recordPossibleMatch(self,candidate,catalog_name, catalog_period, harmonic_n, catalog_RA, catalog_DEC, catalog_DM, theta_sep,catalog_sortAttribute):
        """
        Writes a possible known source match to the output file.
        
        """
        self.possibleMatches += 1
        
        harmonicNumber = str(1/harmonic_n)
        harmonicPeriod = str(float(catalog_period)*float(harmonic_n))
        harmonicPeriod_div_candidatePeriod = str(float(float(catalog_period)*float(harmonic_n))/float(candidate.getParameter("P0")[0]))
        
        try:
            snr_str=str(candidate.getParameter("SNR")[0])
        except TypeError as te:
            snr_str = "0.0"
            
        # First produce human friendly output
        outputFile = open(self.outputFile, "a")
        outputFile.write("POSSIBLE MATCH FOR: \n" + candidate.sourceName + "\n")
        outputFile.write("Candidate Source -> RAJ: " + candidate.getParameter("RAJ")[0] + " DECJ:" + candidate.getParameter("DECJ")[0] + " P0:"  +\
                          candidate.getParameter("P0")[0] + " DM:" + candidate.getParameter("DM")[0] + " SNR: "+ snr_str+" SORT ATTRIB: "+ str(candidate.sortAttribute) + "\n")
        outputFile.write("Known Source     -> RAJ: " +str(catalog_RA) + " DECJ:" + str(catalog_DEC) + " P0:" +\
                          str(catalog_period) + " DM:" + str(catalog_DM) + " SORT ATTRIB: "+ str(catalog_sortAttribute) + "\n")
        outputFile.write("PSR: " + catalog_name + "\n")
        #outputFile.write("P0: " + str(catalog_period) + "\n")
        outputFile.write("Harmonic Number = " + harmonicNumber + "\n")
        outputFile.write("Harmonic Period: " + harmonicPeriod + "\n")
        outputFile.write("Harmonic Period/Candidate Period: " + harmonicPeriod_div_candidatePeriod + "\n")
        #outputFile.write("RA: " +str(catalog_RA) + "\n")
        #outputFile.write("DEC: " + str(catalog_DEC) + "\n")
        #outputFile.write("DM: " + str(catalog_DM) + "\n")
        outputFile.write("Angular separation of psr and cand (deg): " + str(theta_sep) + "\n")
        outputFile.write("@-----------------------------------------------------------------" + "\n")
        outputFile.close()
        
        # Now produce machine friendly CSV format.
        # 
        # Format of CSV file:
        # Candidate name,RAJ,DECJ,P0,DM,SNR,Known Source,RAJ,DECJ,P0,DM,Harmonic Number,Harmonic Period,Harmonic Period/Candidate Period,Angular separation(deg)
        #
        
        csvFile = open(self.outputFile.replace(".txt",".csv"), "a")
        csvFile.write(candidate.sourceName + "," + candidate.getParameter("RAJ")[0] + "," + candidate.getParameter("DECJ")[0] + "," +\
                       candidate.getParameter("P0")[0] + "," + candidate.getParameter("DM")[0] + "," + snr_str + "," + catalog_name + "," + str(catalog_RA) +\
                       "," + str(catalog_DEC) + "," + str(catalog_period) + "," + str(catalog_DM) + "," + harmonicNumber +\
                       "," + harmonicPeriod + "," + harmonicPeriod_div_candidatePeriod +  "," + str(theta_sep) + "\n")
        csvFile.close()
    
    # ******************************
    #
    # FILE TYPE CHECKS.
    #
    # ******************************
    
    def isCatalogueFile(self,filePath):
        """
        Checks if the file at the supplied path is a catalog file.
        Returns true if the file is a catalog file, else false.
        This is a rather dumb check procedure, but for now its overkill
        to check the complete structure of the file. If you want you
        can improve this!
        
        """

        tempFile = open(filePath,'r') # Read only access
        
        for line in tempFile.readlines():
            if ( line.startswith('#CATALOGUE')):
                tempFile.close()
                return True
            else:
                tempFile.close()
                return False
    
    # ****************************************************************************************************
            
    def isCatalogueWebOutput(self,filePath):
        """
        Checks if the file at the supplied path contains output.
        from the ANTF web interface in the "Long with errors" output format.
        This is a massively dumb check procedure, but for now, it would
        be overkill to check the complete structure of the file. If you want you
        can improve this!
        
        """
        
        tempFile = open(filePath,'r') # Read only access
        
        for line in tempFile.readlines():
            if ( line.startswith('-')):
                tempFile.close()
                return True
            else:
                tempFile.close()
                return False
    
    def getPath(self):
        """
        Returns the path to the catalog file.
        """        
        return self.path
    
    # ****************************************************************************************************
    