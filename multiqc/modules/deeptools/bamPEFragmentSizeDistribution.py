#!/usr/bin/env python

""" MultiQC submodule to parse output from deepTools bamPEFragmentSize for read length distribution """

import logging
import re
from collections import OrderedDict

from multiqc import config
from multiqc.plots import linegraph

# Initialise the logger
log = logging.getLogger(__name__)

class bamPEFragmentSizeDistributionMixin():
    def parse_bamPEFragmentSizeDistribution(self):
        """Find bamPEFragmentSize output. Supports the --outRawFragmentLengths option"""
        self.deeptools_bamPEFragmentSizeDistribution = dict()
        for f in self.find_log_files('deeptools/bamPEFragmentSizeDistribution', filehandles=False):
            parsed_data = self.parseBamPEFDistributionFile(f)
            for k, v in parsed_data.items():
                if k in self.deeptools_bamPEFragmentSizeDistribution:
                    log.warning("Replacing duplicate sample {}.".format(k))
                self.deeptools_bamPEFragmentSizeDistribution[k] = v
            if len(parsed_data) > 0:
                self.add_data_source(f, section='bamPEFragmentSizeDistribution')

        if len(self.deeptools_bamPEFragmentSizeDistribution) > 0:
            config = {
                'id': 'fragment_size_distribution_plot',
                'title': 'deeptools: Fragment Size Distribution Plot',
                'ylab': 'Occurrence',
                'xlab': 'Fragment Size (bp)',
                'smooth_points': 50,
                'xmax': 1000,
                'xDecimals': False,
                'tt_label': '<b>Fragment Size (bp) {point.x}</b>: {point.y} Occurrence',
            }

            self.add_section (
                name = 'Fragment size distribution',
                anchor = 'fragment_size_distribution',
                description="Distribution of paired-end fragment sizes",
                plot=linegraph.plot(self.deeptools_bamPEFragmentSizeDistribution, config)
            )

        return len(self.deeptools_bamPEFragmentSizeDistribution)

    def parseBamPEFDistributionFile(self, f):
        d = dict()
        lastsample = []
        for line in f['f'].splitlines():
            cols = line.rstrip().split("\t")
            if cols[0] == "#bamPEFragmentSize":
                continue
            elif cols[0] == "Size":
                continue
            else:
                s_name = self.clean_s_name(cols[2].rstrip().split("/")[-1], f['root'])
                if s_name != lastsample:
                    d[s_name] = dict()
                    lastsample = s_name
                d[s_name].update({int(cols[0]):int(cols[1])})

        return d
