#!/usr/bin/env python

import sys

import one_plot_weather_evaluation as weather


def main(argv):

    for year in sorted(weather.mpi_climate):
        start, flowering, end = weather.FIELD_TRIALS[(year, 'MPI')]
        temp, relH = weather.read_mpi_climate_data(weather.mpi_climate[year],
                                                   use_datetime=False)
        
        maxTemp, minTemp = (weather.aggregate_values_from_grouped(temp, max),
                            weather.aggregate_values_from_grouped(temp, min))
        
        keys = set(maxTemp.keys()).intersection(set(minTemp.keys()))
        for key in sorted(keys):
            params = ['NULL', "'%s'" % key, 4537, minTemp[key], maxTemp[key], 0]
            query = "INSERT INTO temperatures VALUES(%s);" % (','.join(map(str, params)))
            print query        
        pass
    
    
        
        



    pass

if __name__ == '__main__': main(sys.argv[1:])


