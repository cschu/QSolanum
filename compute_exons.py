#!/usr/bin/env python
'''
Created on Nov 1, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import re
"""
chr01   Cufflinks       mRNA    3198    6347    .       -       .       ID=PGSC0003DMT400077762;Parent=PGSC0003DMG400030251;Source_id=RNASEQ34.2864.0;Mapping_depth=16.912202;Class=1;Name="Conserved gene of unknown function"
"""

"""exon
chr01   Cufflinks       exon    6270    6347    .       -       .       ID=PGSC0003DME400205201;Parent=PGSC0003DMT400077762
"""


class Transcript(object):
    def __init__(self, contig, start, end, strand, comments=None):
        self.contig = contig
        self.strand = strand
        self.start = start
        self.end = end        
        self.exons = []
        if comments is not None:
            # print comments
            comments = dict([token.split('=') for token in comments.strip(';').split(';')])
            try:
                self.ID = comments['ID']
            except:
                self.ID = None
            try: 
                self.name = comments['name']
            except: 
                self.name = None
            try:
                self.Parent = comments['Parent']
            except:
                self.Parent = None
        pass
    def get_pos_id(self):
        return (self.contig, self.start, self.end)
    pass

class Exon(Transcript):
    def __init__(self):
        pass
    pass



def main(argv):
    
    transcripts = {}
    lut_transcripts = {}
    
    fn = argv[0]
    for line in open(fn):
        fields = map(str.strip, line.split())
        if re.search('(Cufflinks)|(GLEAN)', fields[1]):
            if fields[2] == 'mRNA':                
                transcript = Transcript(fields[0], int(fields[3]), int(fields[4]), fields[6],
                                        comments=fields[8])
                """
                tid = transcript.get_pos_id()
                
                if tid in transcripts:
                    print 'PROBLEM: Duplicate transcript', tid
                    print line
                    print transcripts[tid]
                    sys.exit(1)
                else:
                    transcripts[tid] = transcript
                    lut_transcripts[transcript.ID] = tid
                    pass
                """                
                transcripts[transcript.ID] = transcript
            elif fields[2] == 'exon':
                exon = Transcript(fields[0], int(fields[3]), int(fields[4]), fields[6],
                                  comments=fields[8])
                parents = exon.Parent.split(',')
                for parent in parents:
                    # print '>>>', parent
                    try:                    
                        # parent = lut_transcripts[parent]
                        transcripts[parent].exons.append(exon.get_pos_id())
                    except:
                        # sys.stderr.write('PROBLEM: Missing transcript %s\n' % parent)
                        # sys.stderr.write(line)
                        # sys.exit(1)
                        pass
                    # transcripts[parent].exons.append(exon.get_pos_id())                
                    pass
                pass
            else:
                pass
    
    #for transcript in sorted(transcripts.values(), key=lambda x:x.get_pos_id()):
    #    print 'TRANSCRIPT %s:%i-%i\n' % transcript.get_pos_id()
    #    for exon in sorted(transcript.exons, key=lambda x:(x[1], x[2])):
    #        print '\tEXON %s:%i-%i\n' % exon
            
    out = open('transcript_sizes.csv', 'w')
    for k in transcripts:
        transcript_size = 0
        for exon in transcripts[k].exons:
            transcript_size += (exon[2] - exon[1]) + 1
        out.write('%s,%i\n' % (k, transcript_size))
    out.close()      
            
                
                      
            
                
              
         
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
