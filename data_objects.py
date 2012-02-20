#!/usr/bin/python

import re
import os
import sys
import math

import cast

#
class DataObject(object):
    def __init__(self, headers=[], values=[]):
        for header, value in zip(headers, values):
            setattr(self, header, cast.cast(value))
        pass
    def __add__(self, other):
        res = DataObject(self.__dict__.keys(), self.__dict__.values())
        res.__dict__.update(other.__dict__)
        return res
    def __repr__(self):
        return str(self.__dict__)
    pass

#
class CompiledData(DataObject):
    def eat_starch_data(self, dobj):
        self.plantspparcelle = dobj.plantspparcelle
        self.planted = dobj.planted
        self.terminated = dobj.terminated
        self.cultivar = dobj.cultivar
        self.breeder = dobj.breeder
        self.reifegruppe = dobj.reifegruppe
        self.sub_id = int(dobj.sub_id)
        pass
    pass
        
        
        
        

# 
class StarchData(DataObject):    

    def __init__(self, headers=[], values=[]):
        min_starch = 100
        max_starch = 300
        warning = 'Warning: Starch content out of bounds in\n%s.\n' 

        super(StarchData, self).__init__(headers=headers, values=values)
        if self.staerkegehalt_g_kg < min_starch:
            # sys.stdout.write(warning % str(self))
            self.staerkegehalt_g_kg *= 10.0
        elif self.staerkegehalt_g_kg > max_starch:
            sys.stdout.write(warning % str(self))

        if hasattr(self, 'cultivar') :
            if self.cultivar.startswith('JA'):
                self.cultivar = 'JASIA'
            elif re.match('KOR?MORAN', self.cultivar):
                self.cultivar = 'KORMORAN'
                
            
        starch_content = self.staerkegehalt_g_kg
        yield_tuber = self.knollenmasse_kgfw_parzelle
        nplants = self.plantspparcelle
        self.starch_abs = StarchData.calc_starch_abs(starch_content,
                                                     yield_tuber,
                                                     nplants=nplants)
        pass        

    @staticmethod
    def calc_starch_abs(starch_content, yield_tuber, nplants=16):
        return starch_content * yield_tuber / float(nplants)
   
    pass

#
class ClimateData(DataObject):
    
    def __init__(self, headers=[], values=[]):
        warning = 'Warning: Missing climate data in\n%s.\n' 

        super(ClimateData, self).__init__(headers=headers, values=values)

        try:
            self.heat_sum = ClimateData.calc_heat_sum(self.tmin, self.tmax)
        except:
            sys.stdout.write(warning % str(self))
            self.heat_sum = None
        pass
    
    @staticmethod
    def calc_heat_sum(tmin, tmax, tbase=6.0):
        """
        Daily heat summation is defined as:
        heat_sum_d = max(tx - tbase, 0), with    
        tx = (tmin + tmax)/2 and
        tmax = min(tmax_measured, 30.0) 
        """
        tmax = min(tmax, 30.0)
        tx = (tmin + tmax) / 2.0
        return max(tx - tbase, 0.0)



if __name__ == '__main__': main(sys.argv[1:])
