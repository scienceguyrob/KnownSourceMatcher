KnownSourceMatcher
==================

A set of python scripts used to match pulsar candidates (in PFD or PHCX format) to known
pulsar sources. It compares each user supplied candidate against known sources in the 
ANTF pulsar catalog. 

http://www.atnf.csiro.au/people/pulsar/psrcat/

To do so the ATNF catalog must first be parsed. However the catalog can be downloaded in many formats.
The scripts supplied will parse the candidates output from the ANTF web interface standard format, and
in the "Long with errors" format, provided you have save this output to a file passed to these scripts.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Its distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See <http://www.gnu.org/licenses/> for more license details.

Author:       Rob Lyon
 
Contact:    rob@scienceguyrob.com or robert.lyon@postgrad.manchester.ac.uk

Web:        http://www.scienceguyrob.com

1.	Overview

	Matches pulsar candidates against known sources from the ANTF pulsar catalog.

	The ANTF catalog file contains a number of known sources. Each source has a number of parameters,
	though the exact number of parameters varies from source to source. The format of the catalog file
	is as follows (as structured from the start of the file):
    
	PSRJ     J0007+7303                    aaa+09c     
	RAJ      00:07:01.7               2    awd+12      
	DECJ     +73:03:07.4              8    awd+12      
	F0       3.165827392              3    awd+12      
	F1       -3.6120E-12              5    awd+12      
	F2       4.1E-23                  7    awd+12      
	F3       5.4E-30                  9    awd+12      
	@-----------------------------------------------------------------
	
	PSRB     B0021-72G                     rlm+95      
	PSRJ     J0024-7204G                               
	RAJ      00:24:07.9587            3    fck+03      
	DECJ     -72:04:39.6911           7    fck+03      
	PMRA     4.2                      14   fck+03      
	PMDEC    -3.7                     12   fck+03      
	F0       247.50152509652          2    fck+03 
	
	@-----------------------------------------------------------------
	
	.
	.
	. 
   <continued>
              
	The scripts can read this format.
    
	Alternatively, they can also read the "Long with errors" format produced by the web interface.
         
2. Requirements

	The KnownSourceMatcher scripts have the following system requirements:

	Python 2.4 or later.
	[SciPy](http://www.scipy.org/)
	[NumPy](http://www.numpy.org/)
	[matplotlib library] (http://matplotlib.org/)

2. Usage

The application script Matcher.py can be executed via:
	
<i>python Matcher.py</i>
	
The script accepts a number of arguments. It requires three of these to execute, and accepts another three as optional.
	
Required Arguments
	
<table>
  <tr>
    <th>Flag</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>−p</td>
    <td>string</td>
    <td>Path to the directory containing PHCX or PFD candidates to match to known sources.</td>
  </tr>
  <tr>
    <td>−o</td>
    <td>string</td>
    <td>Full path to the output file to write any matches found to.</td>
  </tr>
  <tr>
    <td>--psrcat</td>
    <td>string</td>
    <td>Path to the file containing the ANTF pulsar catalog data.</td>
  </tr>
</table>

Optional Arguments

<table>
  <tr>
    <th>Flag</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>−−v</td>
    <td>boolean</td>
    <td>Flag that when provided, put the application into validation mode.</td>
  </tr>
  <tr>
    <td>−i</td>
    <td>boolean</td>
    <td>Puts the application into interactive mode, allowing matching via the terminal.</td>
  </tr>
  <tr>
    <td>-v</td>
    <td>boolean</td>
    <td>Verbose debugging flag.</td>
  </tr>
</table>

3. Matching Function

	The following conditions must hold before a candidate is considered a match for a known source:
    
	1. The candidate period must fall within a user specified range of the known source period.
		This range is a percentage, i.e. the candidate period must be no greater than,
		and no less than m % of the known source period. i.e. given m = 5%, if a known
		source period is 1, then a candidate will only match if its period is in the
		range 1.05 - 0.95.  The default accuracy level is 0.5%.
       
	2. The candidate DM must fall within the same range as above. The default DM accuracy is 5%.
    
	3. The angular separation in degrees between the known source and candidate,
       must be less than a user specified radius (default is 1 degree).
       
	All these matching settings can be altered in the settings file described below.
	
3. Settings File

	The settings for the matching procedure are stored in a file, Settings.txt. This can
	be modified to tune the matching procedure to give better results. Here is an example of
	a valid settings file:
	
	accuracy=1.0
	radius=2.5
	padding=36000
	
	The padding setting is useful for altering the precision of the thresholded comparison function
	described below.
    
3. How It Works
    
	There are two options for candidate comparison to known sources. The first is fine if you only
	have a small number of candidates to compare. The second is better when you have many
	candidates you wish to compare.
	
	i) NAIVE COMPARISON
	
		It works simply by comparing each candidate to every known source in the pulsar catalog. Given
		N known sources and M candidates, this will require N x M comparisons. With M =11,000,000
		and N = 2008, this equates to 2.2088 x 10^10 or 22,088,000,000 comparisons.
		
	ii) THRESHOLDED COMPARISON:
		
		Compares candidates to known sources using a divide and conquer approach. Instead of looping through
		all the known sources in the catalog, this recursive procedure compares candidates to known sources
		which are similar. Similarity is determined using a "sort" attribute computed for each candidate. The
		"sort" attribute is the RAJ converted to seconds, added to the DECJ converted to seconds. Any two
		sources which are nearby in the sky should have very similar sort attribute values. i.e. a contrived
		example:
	
			Source 1
			RAJ = 00:00:01
			DECJ = 00:00:00
			Sort attribute = 1
	
			Source 2
			RAJ = 00:00:01
			DECJ = 00:00:01
			Sort attribute = 2
	
		We can use this to compare candidates extremely quickly since it allows known sources to be sorted. Then
		each new user supplied candidate can be compared to these sorted sources quickly.
		
		Example of how this algorithm works:
	
	    We have a candidate with a sortAttribute == 1. We want to know which known 
	    sources from the pulsar catalog are most similar to it.
	    
	    Lets suppose we have 100 known sources against which to compare, which are ordered according to their sort
	    attribute. The first known source has a sort attribute = 1 and the last a sort attribute = 100.
	    
	    So the known source at position 1 has a sort attribute = 1.
	    ..
	    The known source at position 50 has a sort attribute = 50.
	    ..
	    The known source at position 100 has a sort attribute = 100.
	    
	    Here's a simple visualisation.
	    
	    Start            Midpoint            End
	     |                  |                 |
	     V                  V                 V
	     ______________________________________
	    | | | | | | | | | | | | | | | | | | | |
	    --------------------------------------
	     0                                   n-1
	    
	    If the candidate sort attribute is less than the midpoint sort attribute, then we only need to search:
	    
	    Start            Midpoint
	     |                  |                 
	     V                  V                 
	     ____________________
	    | | | | | | | | | | | 
	    ---------------------
	    0                (n-1)/2
	    
	    else we search the other half:
	    
	                     Midpoint            End
	                        |                 |
	                        V                 V
	                         __________________
	                        | | | | | | | | | |
	                        -------------------
	                    (n-1)/2               n-1
	    
	    As the sort attribute here = 1, which is less than the midpoint, we search:
	    
	    Start    Midpoint    End
	     |         |         |        
	     V         V         V           
	     ____________________
	    | | | | | | | | | | | 
	    ---------------------
	    0       (n-1)/4    (n-1)/2
	                        
	    This procedure repeats, splitting each time until a single known source closest to the candidate
	    is found. Then it compares the candidate to that known source, and to those immediately to the left
	    and right of it. How many it is compared to, to the left and right of the known source, is determined
	    by the padding parameter stored in the settings file.
	
		Given N known sources and M candidates, this will require WORST case N x M comparisons. The worst
		case only occurs if all the known sources have nearly the same RAJ and DECJ as each candidate being
		compared. The chances of this happening are as close to zero.
		
		The AVERAGE case is M + log2(N) + C , where C is a number of comparisons made between known sources
		and candidates which have similar RAJ and DECJ values. The true value of C is dependent on the padding
		parameter supplied by the user and the similarity of the known sources and candidates.
		
		i.e. Given M = 11,000,000 and N = 2008 and C=50 (overestimate!), there would be 561,000,011
		comparisons, compared to 22,088,000,000 comparisons for the naive approach.
		
		To illustrate this difference, comparing 1300 candidates to 2008 known sources using the naive
		approach took ~5 minutes. This optimized approach took only 10 seconds.
		
		The expected numbers of comparisons given varying C and M = 11,000,000 and N = 2008:
		
		C = 1    -> ~ 22,000,000 BEST CASE
		C = 10   -> ~ 121,000,011
		C = 20   -> ~ 231,000,011
		C = 50   -> ~ 561,000,011
		C = 100  -> ~ 1,111,000,011
		C = 1000 -> ~ 11,011,000,010
		C = 2008 -> ~ 22,099,000,010 WORST CASE only marginally worse than Naive Case = 22,088,000,000
		
4. Citing this work

	Please use the following citation if you make use of tool:
	
	@misc{KnownSourceMatcher,
	author = {Lyon, R. J.},
	title  = {{Known Source Matcher}},
	affiliation = {University of Manchester},
	month  = {November},
	year   = {2014},
	howpublished = {World Wide Web Accessed (19/11/2014), \newline \url{https://github.com/scienceguyrob/KnownSourceMatcher}},
	notes  = {Accessed 19/11/2014}
	}
	
5. Acknowledgements

	This work was supported by grant EP/I028099/1 for the University of Manchester Centre for
	Doctoral Training in Computer Science, from the UK Engineering and Physical Sciences Research
	Council (EPSRC).