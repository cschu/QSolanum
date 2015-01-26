#!/usr/bin/env python
'''
Created on Nov 2, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import csv

files = ['17_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2',
         '18_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2',
         '19_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2',
         '20_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2',
         '21_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2',
         '22_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2',
         '23_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2',
         '24_unpaired_fq.gsnap.unpaired_uniq.bam.intersect.genes.hits.2']

sample_d = {'17': 'ALEGRIA_ctl',
            '18': 'DESIREE_ctl',
            '19': 'MILVA_ctl',
            '20': 'SATURNA_ctl',
            '21': 'ALEGRIA_str',
            '22': 'DESIREE_str',
            '23': 'MILVA_str',
            '24': 'SATURNA_str'}


"""
['chr10', '51027650', '51030420', 'PGSC0003DMG400019149', 'Ribulose bisphosphate carboxylase/oxygenase activase, chloroplastic', 'None', '93195']
"""

class HitTranscript(object):
    def __init__(self, row):
        self.contig = row[0]
        self.start = int(row[1])
        self.end = int(row[2])
        self.ID_ = row[3]
        self.name_ = row[4]
        self.Parent_ = row[5]
        self.hits = int(row[6])
        pass
    def __repr__(self):
        return '%s %i %i "%s" %i' % (self.contig, self.start, self.end, self.name_, self.hits)
    def __str__(self):
        return '%s %i %i "%s" %i' % (self.contig, self.start, self.end, self.name_, self.hits)
    def get_csv(self):
        return '%s,%i,%i,"%s",%i' % (self.contig, self.start, self.end, self.name_, self.hits)
    pass

MIN_N_TRANSCRIPTS = 10

def main(argv):
    
    transcripts = {}
    transcripts_in_samples = {}
    
    for fn in files:
        sampleID = fn[:2]
        reader = csv.reader(open(fn, 'rb'), delimiter=',', quotechar='"')
        for row in reader:
            if not row[0].startswith('#'):
                htr = HitTranscript(row)
                if htr.hits >= MIN_N_TRANSCRIPTS:
                    transcripts[htr.ID_] = transcripts.get(htr.ID_, []) + [htr]
                    transcripts_in_samples[htr.ID_] = transcripts_in_samples.get(htr.ID_, []) + [sampleID] 
        pass
    
    all_transcripts = [(k, v, transcripts[k][0].hits) 
                       for k, v in transcripts_in_samples.items()]
    
    # unique transcripts
    out = open('unique_transcripts.csv', 'w')
    # unique_transcripts = sorted([(k, v, transcripts[k][0].hits) 
    #                             for k, v in transcripts_in_samples.items() 
    #                             if len(v) == 1], reverse=False, key=lambda x:x[2])
    unique_transcripts = sorted([(tid, samples, hits) 
                                 for tid, samples, hits in all_transcripts
                                 if len(samples) == 1], reverse=True, key=lambda x:x[2])    
    for k, v, dummy in unique_transcripts:
        string = '%s,%s,%s' % (k, '%s(%s)' % (sample_d[v[0]], v[0]), transcripts[k][0].get_csv())
        out.write(string + '\n')
    out.close()
    
    
    counts = {}
    for tid, samples, hits in all_transcripts:
        samples = list(set(samples))
        counts[len(samples)] = counts.get(len(samples), 0) + 1
    for k, v in sorted(counts.items()):
        print k, v
    
    
    # differentially expressed transcripts
    out = open('diff_transcripts.csv', 'w')
    
    out.write('TranscriptID,Occurs_In_Sample,Contig,Start,End,Name,#reads,Associated_Condition,Associated_CultivarID,Classified!\n')
    
    
    control_set = set(['17', '18', '19', '20'])
    stress_set = set(['21', '22', '23', '24'])
    sensitive_set = set(['17', '20', '21', '24'])
    tolerant_set = set(['18', '19', '22', '23'])
    
    MILVA_set = set(['19', '23'])
    ALEGRIA_set = set(['17', '21'])
    DESIREE_set = set(['18', '22'])
    SATURNA_set = set(['20', '24'])
    
    for tid, samples, hits in all_transcripts:
        
        if 5 > len(set(samples)) > 1:
            string = '%s,%s,%s' % (tid, '-'.join(map(str, sorted(samples))), transcripts[tid][0].get_csv())
            if len(set(samples) - control_set) == 0:
                string += ',control,,'
            elif len(set(samples) - stress_set) == 0:
                string += ',stress,,'
            elif len(set(samples) - sensitive_set) == 0:
                string += ',sensitive,'
                if len(set(samples) - ALEGRIA_set) == 0:
                    string += '2673,ALEGRIA'
                elif len(set(samples) - SATURNA_set) == 0:
                    string += '2675,SATURNA'
                else:
                    string += ','
            elif len(set(samples) - tolerant_set) == 0:
                string += ',tolerant,'
                if len(set(samples) - MILVA_set) == 0:
                    string += '2674,MILVA'
                elif len(set(samples) - DESIREE_set) == 0:
                    string += '91,DESIREE'
                else:
                    string += ','
            else:
                continue
            out.write(string + '\n')
    out.close()
    
    
     
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
