"""

Designed to run on python 2.4 or later. 

Rob Lyon <robert.lyon@cs.man.ac.uk>
 
"""
from Utilities import Utilities

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
        self.harmonics = [1, 0.5, 0.3, 0.25, 0.2, 0.16, 0.125,0.0625,0.03125]
    
    # ******************************
    #
    # FUNCTIONS.
    #
    # ******************************
    
    def run(self):
        """
        Begins the process of interactively search a pulsar catalog.
        """
        print "Running interactively, press '2' to exit."
        
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
            print "2. Exit"
            print "********************\n"
        
            choice = 0
            
            while (choice <= 0 or choice >=3):
                try:
                    choice = int(raw_input("Enter choice (1 or 2): "))
                except:
                    choice = 0
            if(choice == 1):
                self.processChoice()
            elif(choice == 2):        
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
    